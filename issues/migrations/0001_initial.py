# Generated by Django 4.1.5 on 2023-01-26 14:30

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Jira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Sentry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='JiraSentry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jira project key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issues.jira')),
                ('sentry project name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issues.sentry')),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=100)),
                ('traceback', models.TextField()),
                ('url', models.CharField(max_length=100)),
                ('date of receipt', models.DateTimeField(default=django.utils.timezone.now)),
                ('sent', models.BooleanField(default=False)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='issues.sentry')),
            ],
        ),
    ]
