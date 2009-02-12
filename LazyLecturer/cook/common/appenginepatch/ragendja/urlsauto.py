# -*- coding: utf-8 -*-
"""
Imports urlpatterns from apps, so we can have nice plug-n-play installation. :)
"""
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('')

for app in settings.INSTALLED_APPS:
    if app == 'ragendja':
        continue
    try:
        urlpatterns += __import__(app + '.urlsauto', {}, {}, ['']).urlpatterns
    except ImportError:
        pass
