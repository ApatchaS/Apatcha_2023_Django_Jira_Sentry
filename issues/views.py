from global_utils.environment import Environment
from .issues_utils.sentry_request_response_handler import IssueReqResHandler
from . import models

from django.utils import timezone
from django.views import View
from django.views.generic import DetailView

import asyncio


from django.shortcuts import render
from django.http import HttpResponse

class Issues(View):

	OUTDATE_ISSUE_IN_DAYS = Environment.get_environment_variable('OUTDATE_ISSUE_IN_DAYS')

	async def clean_old_issues():
		print(Issues.OUTDATE_ISSUE_IN_DAYS)
		return

	async def get(self, request):
		return HttpResponse('Issue_list')

	async def post(self, request):

		async def thread1_jira_side():
			#Make request to Jira
			#Handle the Jira model
			pass

		async def thread2_sentry_side(fields):
			#Create or update project's record in the Sentry model
			#Create new issue record in the Issue model
			func_fields = dict(fields)
			project = func_fields.pop('sentry_project_name')
			instance, _ = await models.Sentry.objects.aupdate_or_create\
							(name=project, defaults={'last updated': timezone.now()})
			await models.Issue.objects.acreate(**func_fields, project=instance)
			await Issues.clean_old_issues()
			return

		issue = IssueReqResHandler(request)
		if issue.status == 0:
			statuses = await asyncio.gather(thread1_jira_side(),
											thread2_sentry_side(issue.fields),
											)
			#Post to jira if there is link
		return issue.form_feedback()

class IssuesDetail(DetailView):	
	async def get(self, request, pk):
		return HttpResponse(f'Issue_detail {pk}')
