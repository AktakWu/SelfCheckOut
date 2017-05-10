#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2016/12/31
@author: wu
"""

from django import forms

class LoginForm(forms.Form):
    '''
    登录Form
    '''
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Username",
                                "required":"required",}),max_length=50,error_messages=
                              {"required":"username不能为空",})
    password = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Password",
                                "required": "required",}), max_length=20, error_messages=
                               {"required": "password不能为空",})


class UserForm(forms.Form):
    """
    注册
    """
    user_category_CHOICES = (
        ('M', 'Merchant'),
        ('C', 'Customer'),
        ('T', 'Terminal'),
        ('A', 'Staff'),
    )

    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username",
                                "required": "required",}), max_length=50, error_messages=
                               {"required": "username不能为空",})
    password = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Password",
                                "required": "required",}), max_length=20, error_messages=
                               {"required": "password不能为空",})
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "Email",
                                "required": "required",}), max_length=20, error_messages=
                               {"required": "Email不能为空",})

    user_category = forms.ChoiceField(choices=user_category_CHOICES)
