# _*_ coding: utf-8 _*_
from __future__ import absolute_import, unicode_literals
import os
# import django
from celery import Celery
# from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shejiao.settings')
# django.setup()
app = Celery('shejiao')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request:{0!r}'.format(self.request))