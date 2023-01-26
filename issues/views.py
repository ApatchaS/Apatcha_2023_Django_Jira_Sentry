from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt



from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

def issue_list(request):
	return HttpResponse('Issue_list')

def issue_detail(request, pk):
	return HttpResponse(f'Issue_detail {pk}')

@csrf_exempt # We can remove csrf check cause exchanging not sensitive data
@require_http_methods(["POST"])
def issue_post(request):

	return JsonResponse({
		'id': 1,
		'first_name': 'Alexander',
		'second_name': 'Apatchenko'
	})