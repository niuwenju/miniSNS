# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-05-03 20:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yonghu', '0002_auto_20180503_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='friend',
            field=models.ManyToManyField(blank=True, null=True, related_name='_userprofile_friend_+', to='yonghu.UserProfile', verbose_name='\u670b\u53cb'),
        ),
    ]