# Generated by Django 3.1.4 on 2021-10-13 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codechef', '0002_codechefcontestproblems_problemid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='codechefcontestproblems',
            name='problemid',
        ),
    ]
