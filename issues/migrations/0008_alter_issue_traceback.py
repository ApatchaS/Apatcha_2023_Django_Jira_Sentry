# Generated by Django 4.1.5 on 2023-01-30 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0007_alter_issue_traceback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='traceback',
            field=models.TextField(),
        ),
    ]
