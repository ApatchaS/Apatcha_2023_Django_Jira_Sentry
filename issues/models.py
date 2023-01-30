from django.db import models
from django.utils import timezone
import datetime

class Sentry(models.Model):
	project_name = models.CharField(max_length=50, unique=True, default='DEFAULT') #may be Primary key
	last_updated = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.project_name
	
	async def clean_outdated_projects(days):
		current_time = timezone.now()
		await Sentry.objects.exclude(
				last_updated__gte=current_time - datetime.timedelta(days=days),
				last_updated__lte=current_time
				).adelete()
		return

class Jira(models.Model):
	project_name = models.CharField(max_length=50, unique=True, default='DEFAULT') #may be Primary key

	def __str__(self):
		return self.project_name

class JiraSentryLink(models.Model):
	jira_project_name = models.ForeignKey(Jira, on_delete=models.CASCADE)
	sentry_project_name = models.ForeignKey(Sentry, on_delete=models.CASCADE)

	def __str__(self):
		return f'{self.jira_project_name}:{self.sentry_project_name}'


class Issue(models.Model):
	sentry_project_name = models.ForeignKey(Sentry, on_delete=models.CASCADE)
	type = models.CharField(max_length=100)
	value = models.CharField(max_length=100)
	traceback = models.JSONField()
	url = models.URLField()
	date = models.DateTimeField(default=timezone.now)
	sent = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.sentry_project_name}: {self.type} "{self.value}"'
