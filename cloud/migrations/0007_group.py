# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-05-31 06:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0006_auto_20180418_1108'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='组名')),
                ('remark', models.CharField(blank=True, max_length=5000, null=True, verbose_name='说明')),
                ('state', models.CharField(blank=True, max_length=20, null=True, verbose_name='状态')),
                ('sort', models.IntegerField(blank=True, null=True, verbose_name='排序')),
            ],
        ),
    ]
