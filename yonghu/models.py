# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import  models
from django.contrib import admin
from django.utils import timesince, html
from django.utils.encoding import python_2_unicode_compatible

from utils import formatter, function
from shejiao.settings import *
import PIL
from StringIO import StringIO
import six
import xadmin
import time


# category model
@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField('名称', max_length=20 , default="")

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.name = self.name[0:20]
        return super(Category, self).save()

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'

    def __str__(self):
        return "%s | %s | %s" % (
            six.text_type(self.name))


class CategoryAdmin(object):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    list_per_page = ADMIN_PAGE_SIZE
    search_fields = ['name']
    list_filter = ['name']

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'

# User model
class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)

    userip = models.CharField(verbose_name='登录IP', max_length=20, default='', blank=True)
    username = models.CharField(verbose_name='用户名', max_length=20)
    password = models.CharField(verbose_name='密码', max_length=100)
    email = models.EmailField(verbose_name='邮箱')
    sex = models.CharField(verbose_name='性别',choices=(('m','男'),('f','女')), max_length=5,null=True, blank=True)
    phone = models.CharField(verbose_name='电话', max_length=20, default='', blank=True)
    # area = models.ForeignKey(Area,verbose_name='地区')
    face = models.ImageField(verbose_name='头像', upload_to='face/%Y/%m/%d', default='', blank=True)
    url = models.CharField(verbose_name='个人主页', max_length=200, default='', blank=True)
    about = models.TextField(verbose_name='个性签名', max_length=1000, default='', blank=True)
    addtime = models.DateTimeField(verbose_name='注册时间', auto_now=True)
    friend = models.ManyToManyField("self", verbose_name='朋友')

    def __unicode__(self):
        return self.username

    def addtime_format(self):
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')

    def save(self, modify_pwd=True):
        if modify_pwd:
            self.password = function.md5_encode(self.password)
        self.about = formatter.substr(self.about, 20, True)
        super(UserProfile, self).save()

    class Meta:
        verbose_name = u'用户信息'
        verbose_name_plural = u'用户信息'


class UserProfileAdmin(object):
    list_display = ('id', 'username', 'sex', 'email', 'phone','addtime_format')
    list_display_links = ('username','email', 'sex')
    list_per_page = ADMIN_PAGE_SIZE
    search_fields = ['username', 'email']
    list_filter = ['username', 'email']

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'


# Note model
class Note(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    message = models.TextField(verbose_name='消息')
    addtime = models.DateTimeField(verbose_name='发布时间', auto_now=True)
    category = models.ForeignKey(Category, verbose_name='来源')
    user = models.ForeignKey(UserProfile, verbose_name='发布者')

    def __unicode__(self):
        return self.message

    def message_short(self):
        return formatter.substr(self.message, 30)

    def addtime_format_admin(self):
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')

    def category_name(self):
        return self.category.name


    def save(self):
        self.message = formatter.content_tiny_url(self.message)
        self.message = html.escape(self.message)
        self.message = formatter.substr(self.message, 140)
        super(Note, self).save()

    class Meta:
        verbose_name = u'消息'
        verbose_name_plural = u'消息'

    def get_absolute_url(self):
        return APP_DOMAIN + 'message/%s/' % self.id


class NoteAdmin(object):
    list_display = ('id', 'user_name', 'message_short', 'addtime_format_admin', 'category_name')
    list_display_links = ('id', 'message_short')
    search_fields = ['message']
    list_per_page = ADMIN_PAGE_SIZE
    list_filter = ['user']

    class Meta:
        verbose_name = u'消息'
        verbose_name_plural = u'消息'


xadmin.site.register(Note, NoteAdmin)
xadmin.site.register(Category, CategoryAdmin)
xadmin.site.register(UserProfile, UserProfileAdmin)


