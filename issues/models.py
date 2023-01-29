from django.db import models
from django.utils import timezone

class Sentry(models.Model):
	project_name = models.CharField(max_length=50, unique=True, name='name') #may be Primary key
	last_updated = models.DateTimeField(name='last updated', default=timezone.now)

	def __str__(self):
		return self.name

class Jira(models.Model):
	project_name = models.CharField(max_length=50, unique=True, name='name') #may be Primary key

	def __str__(self):
		return self.name

class JiraSentryLink(models.Model):
	jira_project_name = models.ForeignKey(Jira, on_delete=models.CASCADE, name='jira project name')
	sentry_project_name = models.ForeignKey(Sentry, on_delete=models.CASCADE, name='sentry project name')

	def __str__(self):
		return f'{self.jira_project_name}:{self.sentry_project_name}'


class Issue(models.Model):
	sentry_project_name = models.ForeignKey(Sentry, on_delete=models.CASCADE, name='project')
	type = models.CharField(max_length=100)
	value = models.CharField(max_length=100)
	traceback = models.JSONField()
	url = models.URLField()
	date = models.DateTimeField(name='date of receipt', default=timezone.now)
	sent = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.project}: {self.type} "{self.value}"'
