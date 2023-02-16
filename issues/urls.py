from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'issues'
urlpatterns = [
    path('', views.About.as_view(), name='issue_about'),
	path('issues/', csrf_exempt(views.Issues.as_view()), name='issue_list'),
	path('issues/<int:pk>/', views.IssuesDetail.as_view(), name='issue_detail'),
]