# coding: utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^send/$', views.send),
    url(r'^get_state/$', views.get_state),
]
