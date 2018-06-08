"""shejiao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# -*- coding: utf-8 -*-
#from django.conf.urls.defaults import *
from django.conf.urls import patterns, url, include
#from django.contrib import admin
from yonghu.feed import RSSRecentNotes,RSSUserRecentNotes
import shejiao, django
import yonghu.views
import django.contrib.syndication.views
import django.views.static
import django.conf.urls
import django.conf.urls.i18n
from django.conf import settings
from django.conf.urls.static import static
import xadmin
import captcha

xadmin.autodiscover()

rss_feeds = {
    'recent': RSSRecentNotes,
}

rss_user_feeds = {
    'recent': RSSUserRecentNotes,
}

urlpatterns = [
    url(r'^$',yonghu.views.index),
    url(r'^user/$',yonghu.views.index),
    # url(r'^user/(?P<_username>[a-zA-Z\-_\d]+)/$',tmitter.mvc.views.index_user, name= "tmitter-mvc-views-index_user"),
    # url(r'^user/(?P<_email>[a-zA-Z\-_\-.\-@\d]+)/$',yonghu.views.index_user_page, name= "shejiao-yonghu-views-index_user"),
    url(r'^friends/(?P<_email>[a-zA-Z\-_\-.\-@\d]+)/$',yonghu.views.url_list, name= "shejiao-yonghu-views-url_list"),

    url(r'^users/$',yonghu.views.users_list,name= "yonghu.views.users_list"),
    url(r'^signin/$',yonghu.views.signin, name="signin"),
    url(r'^signout/$',yonghu.views.signout),
    url(r'^signup/$',yonghu.views.signup),
    url(r'^settings/$',yonghu.views.settings, name ='shejiao-yonghu-views-settings'),
    url(r'^edit/$',yonghu.views.edit, name ='shejiao-yonghu-views-edit'),
    url(r'^changepassword/$',yonghu.views.changepassword, name ='shejiao-yonghu-views-changepassword'),
    url(r'^forgetpwd/$', yonghu.views.forgetpwd, name='shejiao-yonghu-views-forgetpwd'),
    url(r'^message/(?P<_id>\d+)/$',yonghu.views.detail, name = "shejiao-yonghu-views-detail"),
    url(r'^message/(?P<_id>\d+)/delete/$',yonghu.views.detail_delete, name = "shejiao-yonghu-views-detail_delete"),
    url(r'^friend/add/(?P<_username>[a-zA-Z\-_\d]+)',yonghu.views.friend_add, name="shejiao-yonghu-views-friend_add"),
    url(r'^friend/remove/(?P<_username>[a-zA-Z\-_\d]+)',yonghu.views.friend_remove, name='shejiao.yonghu.views.friend_remove'),
    url(r'^api/note/add/',yonghu.views.api_note_add),
    # Uncomment this for admin:
    #url(r'^admin/(.*)',admin.site.urls),
    url(r'^xadmin/',xadmin.site.urls),
    url(r'^feed/rss/(?P<url>.*)/$', django.contrib.syndication.views.Feed, {'feed_dict': rss_feeds}),
    url(r'^user/feed/rss/(?P<url>.*)/$', django.contrib.syndication.views.Feed, {'feed_dict': rss_user_feeds}),
#    url(r'^statics/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^i18n/', django.conf.urls.i18n.i18n_patterns),
    url(r'^create_code_img/', yonghu.views.create_code_img),
    url(r'^friends/$', yonghu.views.search_friends , name="shejiao-yonghu-views-friends"),
]
