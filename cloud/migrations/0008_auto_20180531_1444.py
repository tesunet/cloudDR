# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-05-31 06:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0007_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='group',
        ),
        migrations.AddField(
            model_name='userinfo',
            name='group',
            field=models.ManyToManyField(to='cloud.Group'),
        ),
    ]
