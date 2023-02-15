# Generated by Django 4.1.6 on 2023-02-15 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0016_alter_jira_project_id_alter_jira_project_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jira',
            name='auth',
            field=models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, to='issues.jiraauth'),
        ),
        migrations.AlterField(
            model_name='jira',
            name='connection',
            field=models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, to='issues.jiraconnection'),
        ),
    ]