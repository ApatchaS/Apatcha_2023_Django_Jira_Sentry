from global_utils.environment import Environment
from .issues_utils.sentry_request_response_handler import IssueReqResHandler
from .issues_utils.jira_request_response_handler import JiraClient
from . import models

from django.utils import timezone
from django.views import View
from django.views.generic import DetailView
from django.shortcuts import render
from asgiref.sync import sync_to_async

import asyncio
import json

OUTDATED_PROJECTS_IN_DAYS = int(Environment.get_environment_variable('OUTDATED_PROJECTS_IN_DAYS'))

class Issues(View):

	async def get(self, request):
		await models.Sentry.clean_outdated_projects(OUTDATED_PROJECTS_IN_DAYS)
		issues = models.Issue.objects.all().order_by('-date', '-sent')
		return await sync_to_async(render)(request, 
											'issues/issue_list.html',
											{'issues':issues})

	async def post(self, request):

		async def thread1_jira_side():
			#Make request to Jira
			#Handle the Jira model
			client = JiraClient()
			response = await client.jira_get_request(url='https://jira.zyfra.com/rest/api/2/project/')
			if response != None:
				jira_projects = JiraClient.jira_get_project_list(response)
				django_projects = {(item.project_name, item.uuid)  async for item in models.Jira.objects.all()}
				projects_to_push = jira_projects.difference(django_projects)
				await models.Jira.objects.abulk_create((models.Jira(project_name=item[0], uuid=item[1]) for item in projects_to_push))
			await client.close()
			return

		async def thread2_sentry_side(fields):
			#Create or update project's record in the Sentry model
			#Create new issue record in the Issue model
			#Delete outdated project according to env variable time
			func_fields = dict(fields)
			project = func_fields.pop('sentry_project_name')
			instance, _ = await models.Sentry.objects.aupdate_or_create\
							(project_name=project, defaults={'last_updated': timezone.now()})
			traceback = await sync_to_async(json.dumps)(func_fields.pop('traceback'), indent=10)
			await models.Issue.objects.acreate(sentry_project_name=instance, traceback=traceback, **func_fields)
			await models.Sentry.clean_outdated_projects(OUTDATED_PROJECTS_IN_DAYS)
			return

		async def post_issue_to_jira():
			client = JiraClient()
			async for link in models.JiraSentryLink.objects.all():
				issues = models.Issue.objects.filter(sentry_project_name=link.sentry_project_name_id, sent=False)
				jira_project_uuid = (await models.Jira.objects.aget(id=link.jira_project_name_id)).uuid
				post_requests = []
				async for issue in issues:
					data = {
						"fields":
						{
							"project":
							{
								"id": jira_project_uuid
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

		issue = IssueReqResHandler(request)

		if issue.status == 0:
			await asyncio.gather(
								thread1_jira_side(),
								thread2_sentry_side(issue.fields),
			)
			#Post to jira if there is link
			await post_issue_to_jira()
		return issue.form_feedback()

class IssuesDetail(DetailView):
	model = models.Issue
	template_name = 'issues/issue_detail.html'
	context_object_name = 'issue'