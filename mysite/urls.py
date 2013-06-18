from django.conf.urls import patterns, include, url
from mysite.views import index, getGraph

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$',index),
                       url(r'^ajax_get_json/$', getGraph, name="ajax_get_json"),
                  
)
