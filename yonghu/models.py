# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import  models
from django.contrib import admin
from django.utils import timesince, html
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import AbstractUser

from tinymce.models import HTMLField
from utils import formatter, function
from shejiao.settings import *
import PIL
from StringIO import StringIO
import six
import time

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    e_name = models.CharField(verbose_name='事件名', max_length=20)
    e_address = models.CharField(verbose_name='事件地址', max_length=50)
    e_balance = models.CharField(verbose_name='余额', max_length=20)
    attr = models.CharField(verbose_name='事件属性', choices=(('col',u'国内大学'),('for',u'国外大学'), ('gam', u'游戏'), ('sta', u'明星'), ('sto', u'股票'), ('boo', u'读书'), ('spo', u'体育'), ('car', u'车'), ('mus', u'音乐'), ('mov', u'电影')),max_length=20, null=True, blank=True)
    # account = models.ManyToManyField(UserProfile,verbose_name='参与用户',blank=True)


    def __unicode__(self):
        return self.e_name

    def addtime_format(self):
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')

    class Meta:
        verbose_name = u'事件信息'
        verbose_name_plural = u'事件信息'


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'e_name', 'e_address', 'e_balance')
    list_display_links = ('e_name',)
    # list_per_page = ADMIN_PAGE_SIZE

    class Meta:
        verbose_name = '事件信息'
        verbose_name_plural = '事件信息'

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


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    list_per_page = ADMIN_PAGE_SIZE
    search_fields = ['name']
    list_filter = ['name']

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'

# User model
class UserProfile(AbstractUser):
    id = models.AutoField(primary_key=True)

    userip = models.CharField(verbose_name='登录IP', max_length=20, default='', blank=True)
    # username = models.CharField(verbose_name='用户名', max_length=20)
    # password = models.CharField(verbose_name='密码', max_length=100)
    # email = models.EmailField(verbose_name='邮箱')
    gender = models.CharField(verbose_name='性别',choices=(('m',u'男'),('f',u'女')), max_length=5,null=True, blank=True)
    phone = models.CharField(verbose_name='电话', max_length=20, default='', blank=True)
    # area = models.ForeignKey(Area,verbose_name='地区')
    face = models.ImageField(verbose_name='头像', upload_to='face/%Y/%m/%d', default='', blank=True)
    url = models.CharField(verbose_name='个人主页', max_length=200, default='', blank=True)
    about = models.TextField(verbose_name='个性签名', max_length=1000, default='', blank=True)
    addtime = models.DateTimeField(verbose_name='注册时间', auto_now=True)
    friend = models.ManyToManyField("self", verbose_name='朋友')
    associate = models.ManyToManyField(Event, verbose_name='关联事件', max_length=50, blank=True)

    def __unicode__(self):
        return self.username

    def addtime_format(self):
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')

    # def save(self, modify_pwd=True):
    #     if modify_pwd:
    #         self.password = function.md5_encode(self.password)
    #     self.about = formatter.substr(self.about, 20, True)
    #     super(UserProfile, self).save()

    class Meta:
        verbose_name = u'用户信息'
        verbose_name_plural = u'用户信息'


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'gender', 'email', 'phone','addtime_format')
    list_display_links = ('username','email', 'gender')
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
    message = HTMLField(verbose_name='消息')
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


class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'message_short', 'addtime_format_admin', 'category_name')
    # list_display_links = ('id', 'message_short')
    # search_fields = ['message']
    # list_per_page = ADMIN_PAGE_SIZE
    # list_filter = ['user']

    class Meta:
        verbose_name = u'消息'
        verbose_name_plural = u'消息'


admin.site.register(Note, NoteAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Event, EventAdmin)

