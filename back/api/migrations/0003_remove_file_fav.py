# Generated by Django 2.2.12 on 2020-06-05 10:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20200605_1915'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='fav',
        ),
    ]
