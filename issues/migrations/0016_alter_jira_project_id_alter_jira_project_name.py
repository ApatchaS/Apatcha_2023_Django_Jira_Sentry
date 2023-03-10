# Generated by Django 4.1.6 on 2023-02-15 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0015_alter_sentry_project_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jira',
            name='project_id',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='jira',
            name='project_name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
