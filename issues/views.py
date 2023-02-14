from .issues_utils.issue_body_builder import IssueBodyBuilder
from .issues_utils.jira_request_response_handler import JiraClient
from .issues_utils.custom_exceptions import InvalidContentType, InvalidJSON, InvalidJSONFields
from . import models

from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView
from django.shortcuts import render
from asgiref.sync import sync_to_async

import asyncio
import json
import logging

SENTRY_REQUEST_CONTENT_TYPE = "application/json"
SENTRY_RESPONSE_CONTENT_TYPE = "application/json"

logger = logging.getLogger('site')

class Issues(View):
	"""
Class-based view that serves listed below HTTP methods:
*GET:
	-gets list of all issues in issue model sorted by date of receive and flag (sent to jira or not)
	-renders template to show that list of objects
*POST:
	-gets POST request from sentry
	-parse request and check if it is valid
	-returns error response to source if request doesn't valid
	-
	"""

	async def get(self, request):
		issues = models.Issue.objects.all().order_by('-date', '-sent')
		logger.debug(f'List view for {await sync_to_async(len)(issues)} issues were called')
		return await sync_to_async(render)(request, 
											'issues/issue_list.html',
											{'issues':issues})

	async def post(self, request):
		
		async def thread1_jira_side():
			#Make request to Jira
			#Handle the Jira model
			client = JiraClient() #FIXME: переписать потом
			response = await client.jira_get_request(url='https://jira.zyfra.com/rest/api/2/project/') #FIXME: перенести baseurl: https://jira.zyfra.com/
			if response != None:
				jira_projects = JiraClient.jira_get_project_list(response)
				django_projects = {(item.project_name, item.project_id)  async for item in models.Jira.objects.all()}
				projects_to_push = jira_projects.difference(django_projects)
				await models.Jira.objects.abulk_create((models.Jira(project_name=item[0], project_id=item[1]) for item in projects_to_push))
			await client.close()
			return

		async def thread2_sentry_side(fields):
			#Create or update project's record in the Sentry model
			#Create new issue record in the Issue model
			#Delete outdated project according to env variable time
			func_fields = dict(fields)
			project = func_fields.pop('sentry_project_name')
			instance, status = await models.Sentry.objects.aupdate_or_create\
							(project_name=project, defaults={'last_updated': timezone.now()})
			logger.info(f'Sentry project: {instance} were successfully ' + ('created' if status else 'updated') + '!')
			traceback = await sync_to_async(json.dumps)(func_fields.pop('traceback'), indent=10)
			await models.Issue.objects.acreate(sentry_project_name=instance, traceback=traceback, **func_fields)
			return

		async def post_issue_to_jira():
			client = JiraClient()
			async for link in models.JiraSentryLink.objects.all():
				issues = models.Issue.objects.filter(sentry_project_name=link.sentry_project_name_id, sent=False)
				jira_project_id = (await models.Jira.objects.aget(id=link.jira_project_name_id)).project_id
				post_requests = []
				async for issue in issues:
					data = {
						"fields":
						{
							"project":
							{
								"id": jira_project_id
							},
							"summary": f'{issue.type}: {issue.value}',
							"description": f'Traceback:\n{issue.traceback}\nSentry URL:\n{issue.url}\n',
							"issuetype":
							{
								"id": "10103"
							}
						}
					}
					post_requests.append(
						asyncio.ensure_future(
							client.jira_post_request(
								url='https://jira.zyfra.com/rest/api/2/issue/',
								data=json.dumps(data, indent=5),
							)))
				post_responses = await asyncio.gather(*post_requests)
				for ind in range(len(post_responses)):
					if post_responses[ind] != None:
						issues[ind].sent = True
						await sync_to_async(issues[ind].save)()
				await sync_to_async(print)(post_responses)
			await client.close()
			return
		
		def create_response(status_code, message, fields, content_type=SENTRY_RESPONSE_CONTENT_TYPE):
			body = {
				'status code': status_code,
				'message': message,
				'content': fields,
			}
			return JsonResponse(data=body,
		       					status=status_code,
								content_type=content_type)
		#Entry point
		logger.debug('New issue from Sentry were received by post view')

		try:
			if request.content_type != SENTRY_REQUEST_CONTENT_TYPE:
				raise InvalidContentType(
					406,
					"Issue should be sent as json: check request's body and headers",
					)
			try:
				json_request_body = json.loads(request.body)
			except json.JSONDecodeError as json_loading_error:
				raise InvalidJSON(
					400,
					"Sent json have syntaxis errors",
					) from json_loading_error
			json_response_body = IssueBodyBuilder(json_request_body)
		except (
				InvalidContentType,
				InvalidJSON,
	  			InvalidJSONFields,
				) as exc:
			return create_response(
							exc.status_code,
			  				exc.message,
							exc.fields,
							)

		await asyncio.gather(
							thread1_jira_side(),
							thread2_sentry_side(json_response_body.fields),
		)
		#Post to jira if there is link
		await post_issue_to_jira()
		return create_response(
								202,
								"Issue successfully processed!",
								json_response_body.fields,
								)

class IssuesDetail(DetailView):
	"""
Built-in Generic Class-based view that:
	-gets certain primary key from url
	-finds object in certain model <Issue>
	-renders that object according to initialized template <issue_detail.html>
	"""
	model = models.Issue
	template_name = 'issues/issue_detail.html'
	context_object_name = 'issue'

	def	get_object(self):
		obj = super().get_object()
		time_log_field = obj.date.isoformat(sep=' ', timespec='seconds')
		logger.debug(f'Detail view for {obj} from {time_log_field} were called')
		return obj