# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-06-22 07:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0017_auto_20180622_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='url',
            field=models.CharField(blank=True, max_length=100, verbose_name='页面链接'),
        ),
    ]
