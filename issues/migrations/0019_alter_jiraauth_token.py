# Generated by Django 4.1.6 on 2023-02-15 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0018_alter_jiraconnection_base_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jiraauth',
            name='token',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
