from .issues_utils.sentry_request_response_handler import IssueReqResHandler

from django.views import View
from django.views.generic import DetailView
import asyncio
from . import models


from django.shortcuts import render
from django.http import HttpResponse

class Issues(View):

	async def get(self, request):
		return HttpResponse('Issue_list')

	async def post(self, request):
		
		async def thread1_jira_side():
			#Make request to Jira
			#Handle the Jira model
			pass

		async def thread2_sentry_side(fields):
			#Handle the sentry project model
			#Handle the Issue model
			func_fields = dict(fields)
			project = func_fields.pop('sentry_project_name')
			instance = None
			try:
				instance = await models.Sentry.objects.aget(name=project)
			except:
				instance = await models.Sentry.objects.acreate(name=project)
			finally:
				await models.Issue.objects.acreate(**func_fields, project=instance)
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
