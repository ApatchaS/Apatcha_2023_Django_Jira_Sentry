from django.db import models
from django.utils import timezone

class JiraAuth(models.Model):
	"""
Jira's bearer auth tokens
	"""
	token = models.CharField(max_length=100, unique=True) #Unique

	def __str__(self):
		return f'Jira\'s token: {self.token}'

class JiraConnection(models.Model):
	"""
Jira's session connect configuration
	"""
	base_url = models.URLField(unique=True) #Unique
	timeout = models.IntegerField(default=30) #Not required

	def __str__(self):
		return f'Base url {self.base_url} with connection timeout {self.timeout}'

class Jira(models.Model):
	"""
Jira's projects
	"""
	project_name = models.CharField(max_length=50, unique=True) #Unique
	project_id = models.IntegerField(unique=True) #Unique
	auth = models.OneToOneField(JiraAuth, on_delete=models.RESTRICT) #One to one relation
	connection = models.OneToOneField(JiraConnection, on_delete=models.RESTRICT) #One to one relation
	last_updated = models.DateTimeField(default=timezone.now) #Not required

	def __str__(self):
		return f'{self.project_name}:{self.project_id}'

class Sentry(models.Model):
	"""
Sentry's projects
	"""
	project_name = models.CharField(max_length=50, unique=True) #Unique
	last_updated = models.DateTimeField(default=timezone.now) #Not required

	def __str__(self):
		return self.project_name

class Issue(models.Model):
	"""
Issues from Sentry to post as tasks in Jira
	"""
	sentry_project_name = models.ForeignKey(Sentry, on_delete=models.CASCADE) #One to many relation
	type = models.CharField(max_length=100)
	value = models.CharField(max_length=100)
	traceback = models.JSONField()
	url = models.URLField()
	date = models.DateTimeField(default=timezone.now) #Not required
	sent = models.BooleanField(default=False) #Not required

	def __str__(self):
		return f'{self.sentry_project_name}: {self.type} "{self.value}"'

class JiraSentryLink(models.Model):
	"""
Link between projects in Jira and Sentry
	"""
	jira_project_name = models.OneToOneField(Jira, on_delete=models.CASCADE) #Unique
	sentry_project_name = models.OneToOneField(Sentry, on_delete=models.CASCADE) #Unique

	def __str__(self):
		return f'{self.jira_project_name}:{self.sentry_project_name}'