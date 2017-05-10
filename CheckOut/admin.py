#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2016/12/31
@author: wu
"""

from django.contrib import admin
from  .models import *
# Register your models here.

# admin.site.register(User)
@admin.register(User)
class Muser(admin.ModelAdmin):
    list_display = ('id','username','user_category','regist_data')

@admin.register(order)
class ManageOrder(admin.ModelAdmin):
    list_display = ('id','order_status','create_data','Merchant_ID','User_ID')

@admin.register(product_single)
class ProductSingle(admin.ModelAdmin):
  list_display = ('id','barcode','product_name','User_ID','Merchant_ID',
                  'order_num','price','num',
                  )
