# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-07-31 02:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0024_auto_20180726_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='script',
            name='succeedtest',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='成功代码'),
        ),
    ]
