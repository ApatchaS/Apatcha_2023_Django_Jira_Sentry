from django.urls import path
from . import views

app_name = 'issues'
urlpatterns = [
	path('', views.issue_list, name='issue_list'),
	path('issue/<int:pk>/', views.issue_detail, name='issue_detail'),
	path('issue/new/', views.issue_post, name='issue_post'),
]