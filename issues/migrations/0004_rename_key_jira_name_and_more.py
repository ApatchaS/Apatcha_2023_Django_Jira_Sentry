# Generated by Django 4.1.5 on 2023-01-29 00:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0003_rename_jira_sentry_jirasentrylink_alter_issue_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jira',
            old_name='key',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='jirasentrylink',
            old_name='jira project key',
            new_name='jira project name',
        ),
        migrations.AddField(
            model_name='sentry',
            name='last updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
