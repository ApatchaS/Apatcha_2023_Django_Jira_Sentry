# Generated by Django 4.1.5 on 2023-02-03 14:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0012_jira_uuid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jira',
            old_name='uuid',
            new_name='project_id',
        ),
    ]
