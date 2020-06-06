# Generated by Django 2.2.12 on 2020-06-06 17:51

from django.db import migrations, models
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('fid', djongo.models.fields.ObjectIdField(auto_created=True, db_column='_id', primary_key=True, serialize=False)),
                ('isFile', models.BooleanField()),
                ('author', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
                ('path', models.TextField()),
                ('fileSize', models.IntegerField()),
                ('createdDate', models.CharField(max_length=20)),
                ('deletedDate', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]
