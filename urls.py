#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
import apps.questions.views as views

urlpatterns = patterns('',
    url(r'^questions$',             views.questions),
    url(r'^questions/(?P<pk>\d+)$', views.questions),
    url(r'^submissions$',           views.submissions)
)
