from global_utils.environment import Environment
from .issues_utils.sentry_request_response_handler import IssueReqResHandler
from . import models

from django.utils import timezone
from django.views import View
from django.views.generic import DetailView
from django.shortcuts import render

import asyncio

OUTDATED_PROJECTS_IN_DAYS = int(Environment.get_environment_variable('OUTDATED_PROJECTS_IN_DAYS'))

class Issues(View):

	async def get(self, request):
		models.Sentry.clean_outdated_projects(OUTDATED_PROJECTS_IN_DAYS)
		issues = models.Issue.objects.all().order_by('date')
		return render(request, 'issues/issue_list.html', {'issues':issues})

	async def post(self, request):

		async def thread1_jira_side():
			#Make request to Jira
			#Handle the Jira model
			pass

		async def thread2_sentry_side(fields):
			#Create or update project's record in the Sentry model
			#Create new issue record in the Issue model
			#Delete outdated project according to env variable time
			func_fields = dict(fields)
			project = func_fields.pop('sentry_project_name')
			instance, _ = await models.Sentry.objects.aupdate_or_create\
							(project_name=project, defaults={'last_updated': timezone.now()})
			await models.Issue.objects.acreate(**func_fields, sentry_project_name=instance)
			await models.Sentry.clean_outdated_projects(OUTDATED_PROJECTS_IN_DAYS)
			return

		issue = IssueReqResHandler(request)
		if issue.status == 0:
			statuses = await asyncio.gather(thread1_jira_side(),
											thread2_sentry_side(issue.fields),
											)
			#Post to jira if there is link
		return issue.form_feedback()

class IssuesDetail(DetailView):
	model = models.Issue
	template_name = 'issues/issue_detail.html'
	context_object_name = 'issue'