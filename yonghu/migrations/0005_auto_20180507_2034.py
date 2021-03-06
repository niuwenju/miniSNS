# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-05-07 20:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yonghu', '0004_remove_userprofile_realname'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='sex',
            field=models.CharField(choices=[('m', '\u7537'), ('f', '\u5973')], max_length=5, null=True, verbose_name='\u6027\u522b'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='about',
            field=models.TextField(blank=True, default='', max_length=1000, verbose_name='\u4e2a\u6027\u7b7e\u540d'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='friend',
            field=models.ManyToManyField(related_name='_userprofile_friend_+', to='yonghu.UserProfile', verbose_name='\u670b\u53cb'),
        ),
    ]
