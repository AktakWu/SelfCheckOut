#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2016/12/31
@author: wu
"""

from django.conf.urls import url
from CheckOut import views

urlpatterns = [
    url(r'^$',views.index,name='index'),
    url(r'^index/$',views.index,name='index'),
    url(r'^login/$',views.do_login, name='login'),
    url(r'^regist/$',views.do_regist, name='regist'),
    url(r'^logout/$',views.do_logout, name='logout'),
    url(r'^neworder/$',views.create_order,name='neworder'),
    url(r'^add_product/$',views.add_product,name='add_product'),
    url(r'^ask_new_info/$',views.ask_new_info,name='ask_new_info'),#
    url(r'^add_info/$',views.add_info,name="add_info"),
    url(r'testprice/$',views.pageaddprice,name='testprice'),
    url(r'^scan/$',views.appscan),
]