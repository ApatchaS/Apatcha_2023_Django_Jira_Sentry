from django.shortcuts import render
from django.http import HttpResponse

def issue_list(request):
	return HttpResponse('Issue_list')

def issue_detail(request):
	return HttpResponse('Issue_detail')

def post_new(request):
	return HttpResponse('Post_new')