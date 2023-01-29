from django.contrib import admin
from . import models

admin.site.register(models.Jira)
admin.site.register(models.Sentry)
admin.site.register(models.JiraSentryLink)
admin.site.register(models.Issue)
