# Generated by Django 3.1.4 on 2021-01-21 08:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0002_auto_20210121_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contest',
            name='startTime',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='contestresult',
            name='submissionTime',
            field=models.DateTimeField(),
        ),
    ]
