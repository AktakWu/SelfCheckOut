#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2016/12/31
@author: wu
"""

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# 用户模型.
# 采用的继承方式扩展用户信息（本系统采用）
class User(models.Model):

    user_category_CHOICES = (
        ('M','Merchant'),
        ('C','Customer'),
        ('T','Terminal'),
        ('A','Staff'),
    )
    username =models.CharField(max_length=100,blank=True,null=False,verbose_name="用户名")
    password = models.CharField(max_length=20,blank=True,null=False,verbose_name='密码')
    avatar = models.ImageField(upload_to='avatar/%Y/%m', default='avatar/default.png',
                              max_length=200, blank=True,null=True, verbose_name='用户头像')
    email = models.EmailField(max_length=100,blank=True,null=True,verbose_name="邮箱")
    mobile = models.CharField(max_length=11,blank=True,null=True,verbose_name="手机号")
    user_category = models.CharField(max_length=1,choices=user_category_CHOICES,default='C',
                                     verbose_name='用户类型')
    regist_data = models.DateTimeField(auto_now_add=True)

    class Mate:
        verbose_name = '用户'
        ordering = ('-id')

    def __str__(self):
        return self.username

# 订单模型
class order(models.Model):
    # 用ID代代替订单号
    # ordernum = models.IntegerField(verbose_name='订单号')
    order_status_CHOICES = (
        ('FD', 'Finished'),
        ('TO', 'TimeOut'),
        ('PF', 'PayFailed'),
        ('NL', 'Normal')
    )
    create_data = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    User_ID = models.CharField(max_length=100, default="-",verbose_name='用户ID',
                               blank=True, null=True)
    Merchant_ID = models.CharField(max_length=100, verbose_name='商家ID', blank=True, null=False)
    order_status = models.CharField(max_length=5,choices=order_status_CHOICES,verbose_name=
                                    '订单状态')

    class Meta:
        db_table = '订单'

    def __str__(self):
        return str(self.id)

#商品流水单
class product_single(models.Model):
    #id 用来做流水号
    barcode = models.IntegerField(null=False,verbose_name='条形码',)
    product_name = models.CharField(max_length=100,verbose_name='商品名称',blank=True,
                                    default="-",null=True)
    User_ID = models.CharField(max_length=100,default="-",verbose_name='用户ID',
                               blank=True,null=True)
    Merchant_ID = models.CharField(max_length=100,verbose_name='商家ID',blank=True,null=False)
    price = models.FloatField(default=0,null=True, verbose_name="单价") #充许后面修改
    num = models.IntegerField(default=0,verbose_name='数量')
    create_data = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    order_num = models.ForeignKey(order,verbose_name='订单号',null=False)
    def get_subtotal(self):
        return (self.price * self.num)

    class Meta:
        db_table = '商品流水单'

    def __str__(self):
        return str(self.barcode)




