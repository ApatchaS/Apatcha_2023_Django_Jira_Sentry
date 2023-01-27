from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .issues_utils.issue_request_response_handler import IssueReqResHandler

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse




def issue_list(request):
	return HttpResponse('Issue_list')

def issue_detail(request, pk):
	return HttpResponse(f'Issue_detail {pk}')

@csrf_exempt # We can remove csrf check cause exchanging not sensitive data
@require_http_methods(["POST"])
def issue_post(request):
	issue = IssueReqResHandler(request.content_type, request.body)

	return HttpResponse(JsonResponse(issue.form_meta_response()),
									content_type='application/json',
									status=issue.status_code)