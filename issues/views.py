from .issues_utils.issue_body_builder import IssueBodyBuilder
from .issues_utils.jira_client import JiraClient
from .issues_utils.custom_exceptions import InvalidContentType, InvalidJSON, InvalidJSONFields
from . import models

from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView
from django.shortcuts import render
from asgiref.sync import sync_to_async
from validators import url as valid_url

import asyncio
import json
import logging

SENTRY_REQUEST_CONTENT_TYPE = "application/json"
SENTRY_RESPONSE_CONTENT_TYPE = "application/json"

logger = logging.getLogger('site')

class About(View):
	"""
	Class-based view to render page ABOUT
	"""
	async def get(self, request):
		logger.debug('About page were called')
		return await sync_to_async(render)(request, 'issues/about.html')

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
	-creates new object or updates time of last update for sentry model to which issue was sent
	-creates new record in issue model
	-for each link between jira and sentry models:
		--gets:
			*jira project name
			*jira project id
			*jira base url to post request on
			*timeout for connection to jira
			*bearer token for auth
			*didn't send issues from sentry model record related to link
		--creates new session with gotten parameters (timeout, bearer token)
		--for each gotten issue:
			---forms body for request
			---forms full url
			---validates url
			---creates task which send request to jira
			---appending each task to list
		--waits till finishing each task in the list
		--closes created earlier session
		--updates:
			*flag which illustates if issue was sent for each successfuly posted to jira issue
			*date of last update for jira model
	-creates response to sentry
	"""

	async def get(self, request):
		issues = models.Issue.objects.all().order_by('-date', '-sent')
		logger.debug('List view for %d issues were called' % await sync_to_async(len)(issues))
		return await sync_to_async(render)(request,
											'issues/issue_list.html',
											{'issues':issues})

	async def post(self, request):

		async def sentry_issue_models_handler(fields):
			func_fields = dict(fields)
			project = func_fields.pop('sentry_project_name')
			instance, status = await models.Sentry.objects.aupdate_or_create\
							(project_name=project, defaults={'last_updated': timezone.now()})
			logger.info('Sentry project: %s was successfully %s!' % (instance, ('created' if status else 'updated')))
			traceback = await sync_to_async(json.dumps)(func_fields.pop('traceback'), indent=10)
			await models.Issue.objects.acreate(sentry_project_name=instance, traceback=traceback, **func_fields)
			logger.info('New issue for %s sentry project was successfully created!' % instance)
			return

		async def post_issue_to_jira():
			async for link in models.JiraSentryLink.objects.all():

				jira_project = await models.Jira.objects.aget(id=link.jira_project_name_id)
				jira_project_connection = await models.JiraConnection.objects.aget(id=jira_project.connection_id)
				jira_project_auth = await models.JiraAuth.objects.aget(id=jira_project.auth_id)
				jira_project_id = jira_project.project_id
				jira_project_auth_token = jira_project_auth.token
				jira_project_connection_base_url = jira_project_connection.base_url
				jira_project_connection_timeout = jira_project_connection.timeout

				issues = models.Issue.objects.filter(sentry_project_name=link.sentry_project_name_id, sent=False)

				client = JiraClient(jira_project_auth_token, jira_project_connection_timeout)
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
					data = json.dumps(data, indent=5)
					url = jira_project_connection_base_url + 'rest/api/2/issue/'
					if not valid_url(url):
						await client.close()
						logger.error('For jira project %s specified incorrect base url %s' % (
															jira_project, 
									    					jira_project_connection_base_url))
						return
					post_requests.append(
						asyncio.ensure_future(
							client.jira_post_request(
								url=url,
								data=data,
							)))
				post_responses = await asyncio.gather(*post_requests)
				await client.close()
				post_responses_size = len(post_responses)
				jira_project.last_updated = timezone.now()
				await sync_to_async(jira_project.save)()
				logger.info('For jira project %s were successfully updated date of last update' % jira_project)
				successful_post_responses = 0
				for ind in range(post_responses_size):
					if post_responses[ind] != None:
						successful_post_responses += 1
						issues[ind].sent = True
						await sync_to_async(issues[ind].save)()
				logger.info('For link %s among %d issues %d were successfully sent to Jira!' % (
													await sync_to_async(link.__str__)(),
													post_responses_size,
													successful_post_responses))
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
			logger.info('Request from Sentry was successfuly validated!')
		except (
				InvalidContentType,
				InvalidJSON,
	  			InvalidJSONFields,
				) as exc:
			logger.error('While validating request from sentry errors were detected. Type: %s. Message: %s' % (
																		type(exc),
																		exc.message))
			return create_response(
							exc.status_code,
			  				exc.message,
							exc.fields,
							)

		await sentry_issue_models_handler(json_response_body.fields),
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
		logger.debug('Detail view for %s from %s were called' % (obj, time_log_field))
		return obj