from django.db import models
from django.utils import timezone

class JiraAuth(models.Model):
	"""
Jira's bearer auth tokens
	"""
	token = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return f'Jira\'s token: {self.token}'

class JiraConnection(models.Model):
	"""
Jira's session connect configuration
	"""
	base_url = models.URLField(unique=True)
	timeout = models.PositiveSmallIntegerField(default=30)

	def __str__(self):
		return f'Base url: "{self.base_url}" with connection timeout: {self.timeout}'

class Jira(models.Model):
	"""
Jira's projects
	"""
	project_name = models.CharField(max_length=50, unique=True)
	project_id = models.IntegerField(unique=True)
	auth = models.OneToOneField(JiraAuth, on_delete=models.RESTRICT)
	connection = models.OneToOneField(JiraConnection, on_delete=models.RESTRICT)
	last_updated = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f'{self.project_name}:{self.project_id}'

class Sentry(models.Model):
	"""
Sentry's projects
	"""
	project_name = models.CharField(max_length=50, unique=True)
	last_updated = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.project_name

class Issue(models.Model):
	"""
Issues from Sentry to post as tasks in Jira
	"""
	sentry_project_name = models.ForeignKey(Sentry, on_delete=models.CASCADE)
	type = models.CharField(max_length=100)
	value = models.CharField(max_length=100)
	traceback = models.JSONField()
	url = models.URLField()
	date = models.DateTimeField(default=timezone.now)
	sent = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.sentry_project_name}: {self.type} "{self.value}"'

class JiraSentryLink(models.Model):
	"""
Link between projects in Jira and Sentry
	"""
	jira_project_name = models.OneToOneField(Jira, on_delete=models.CASCADE)
	sentry_project_name = models.OneToOneField(Sentry, on_delete=models.CASCADE)

	def __str__(self):
		return f'{self.jira_project_name}:{self.sentry_project_name}'