from django.db import models
from django.utils import timezone

class Sentry(models.Model):
	project_name = models.CharField(max_length=50, name='name')

	def __str__(self):
		return self.project_name

class Jira(models.Model):
	project_key = models.CharField(max_length=50, name='key')

	def __str__(self):
		return self.project_key

class JiraSentry(models.Model):
	jira_project_key = models.ForeignKey(Jira, on_delete=models.CASCADE, name='jira project key')
	sentry_project_name = models.ForeignKey(Sentry, on_delete=models.CASCADE, name='sentry project name')

	def __str__(self):
		return f'{self.jira_project_key}:{self.sentry_project_name}'


class Issue(models.Model):
	sentry_project_name = models.ForeignKey(Sentry, on_delete=models.CASCADE, name='project')
	type = models.CharField(max_length=100)
	value = models.CharField(max_length=100)
	traceback = models.TextField()
	url = models.CharField(max_length=100)
	date = models.DateTimeField(name='date of receipt', default=timezone.now)
	sent = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.sentry_project_name}: {self.type} "{self.value}"'
