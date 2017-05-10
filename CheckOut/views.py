#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2016/12/31
@author: wu
"""
# from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt  #取消csrf_exempt 验证

from django.shortcuts import render,HttpResponsePermanentRedirect,HttpResponse,redirect
from .froms import LoginForm,UserForm
from .models import User,order,product_single
import json

# Create your views here.

def index(request):
    username = request.COOKIES.get('username','')
    return  render(request,'index.html',locals())


#@csrf_exempt
def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            print(login_form)
            if login_form.is_valid():
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = User.objects.filter(username__exact = username,password__exact =
                                           password)
                if user:
                    response = HttpResponsePermanentRedirect('/index/')
                    response.set_cookie('username',username,3600)
                    return response
                else:
                    return HttpResponsePermanentRedirect('/login/')
    except Exception as e :
        print(e)
    return render(request,'login.html',locals())

def do_regist(request):
    if request.method == 'POST':
        userform = UserForm(request.POST)
        if userform.is_valid():
            user = User.objects.create(username = userform.cleaned_data['username'],
                                        password = userform.cleaned_data['password'],
                                        email = userform.cleaned_data['email'],
                                        user_category = userform.cleaned_data['user_category'])
            user.save()
            return HttpResponsePermanentRedirect('regist success!!')
    else:
        userform = UserForm()
    return render(request,'regist.html',locals())


def do_logout(request):
    response = HttpResponse('logout!!')
    response.delete_cookie('username')
    return render(request,'index.html')

#终端请求的地方
def create_order(request):
    #先判断有没有登录,查看cookie。里的定单状态
    username = request.COOKIES.get('username', '')
    if username:
        #，是不是商家或终端，注意，这得得出来的是一个列表
        user = User.objects.filter(username=username)
        print(user.values_list())
        if 'M' in user.values_list()[0]:
            #生成最新的单号
            order_new = order.objects.create(Merchant_ID=username,order_status='NL')
            # print(order_new)
            # 取出最新单号进行，返还终端，然后终端
            # 其实这里可以order_num = order.objects.all().order_by('-id')[0:1].values() 就可以返回了
            order_num = order.objects.all().order_by('-id')[0:1].values_list()[0]
            new_order_detal = {'order_num':order_num[0],
                               'create_time':str(order_num[1]), # 定单生成时间不成转成json，不传   返回用split 分割
                               'User_Id':'xxx',   #'order_num[2]是空的null，在终端不好处理改成传成，'xxx' 0 或不传,
                               'Merchant_ID':order_num[3],
                               'order_status':order_num[4],
                               }
            #以json 的格工返回
            print(new_order_detal)
            # print(type(new_order_detal))
            return HttpResponse(json.dumps(new_order_detal)) #返回在终端进行处理
        else:
            return redirect('/logout/')
    else:
        return redirect('/login/')

#在正常订单下创建商品流水号信息
def add_product(request):
    try:
        barcode = request.GET.get("barcode",'')
        order_num = request.GET.get("order_num",'')
        merchant = request.GET.get("merchant",'')
        num = request.GET.get("num",'')
        username = request.COOKIES.get('username', '')
        order_status = request.GET.get("order_status",'')

        custmor_order = order.objects.get(id=order_num) #id是唯一的就是定单
        print(custmor_order.order_status)
        #把正常情况下订单userID 的空白项给填上用户的信息
        if order_num and custmor_order.order_status == 'NL'and custmor_order.User_ID == '-' :
            custmor_order.User_ID = username
            custmor_order.save()
        if order_status == 'FD':
            print('改变订单状态')
            custmor_order.order_status = order_status
            custmor_order.save()

        #在正常订单下创建流水号信息
        if barcode and custmor_order.order_status == 'NL':
            #先判断这次的订单下有没有相同的信息而且要注意订单号
            try:
                product_add = product_single.objects.get(barcode=barcode,order_num=order_num)
            except:
                product_add = product_single.objects.filter(barcode=barcode,order_num=order_num)
            print(product_add)
            if product_add:
                product_add.num = product_add.num+int(num)  #相同条码就加起来
                product_add.save()
            else:
                 product_add = product_single.objects.create(barcode=barcode,
                                                             User_ID = username,
                                                             Merchant_ID = merchant,
                                                             num = num,
                                                             order_num = custmor_order,#这里必须放实例对像
                                                             )
            #显示要购买的商品
        product_list = product_single.objects.filter(order_num=order_num)
        # print('查看'+str(product_list.values_list()))
        # print(type(product_list.values()))
        # print('查看' + str(product_list.values()))
        # print(json.dumps(product_list.values()))

        # return HttpResponse(json.dumps(product_list.values()),content_type="text")
        #product_list.values() 不能直接变成为JSON格式。是因为里有DATATIME

        # 把buy_list 变成Json 格式返回[{'':'',},{'':'',}]
        product_json=[]
        product_mate={}
        for product in product_list.values():
            print(product)
            product_mate ={"id":product['id'],
                           "barcode":product['barcode'],
                           "product_name":product['product_name'],
                           "price":product['price'],
                           "num":product['num'],
                           }
            product_json.append(product_mate)
        # print(json.dumps(product_json))
        return HttpResponse(json.dumps(product_json), content_type="appliction/josn")
    except Exception as e:
        print(e)
    return render(request,'index.html',locals())



# 这里是终端访问的模块，添加价格信息模块，带着订单号信息进行请求的。
# 不断的询问此单下是否有新的流水信息产生,应该不用带上用户的ID 因为
# 查询的是某个订单号下面的。

def ask_new_info(request):
    try:
        order_num = request.GET.get("order_num", '')
        if order_num:
            #为了防止，有时添加的是重复的，形码，终端无法显示正确的数据信息，所以要全部找出来。不能只找出价格为空的。
            # product_list = product_single.objects.filter(order_num = order_num,price__isnull = True)
            product_list = product_single.objects.filter(order_num=order_num)
            product_json = []
            # product_mate = {}
            custmor_order = order.objects.get(id=order_num)  # id是唯一的就是定单

            for product in product_list.values():
                # print(product)
                product_mate = {"id": product['id'],
                                "barcode": product['barcode'],
                                "product_name": product['product_name'],
                                "price": product['price'],
                                "num": product['num'],
                                "User_ID":product['User_ID'],
                                "order_num":order_num,
                                "order_status":custmor_order.order_status,
                                }
                product_json.append(product_mate)
            print(json.dumps(product_json))
            return HttpResponse(json.dumps(product_json), content_type="appliction/josn")
    except Exception as e:
        print(e)

def pageaddprice(request):

    return render(request,'test_add_price.html')

#这里订单号要带上，为了防止加到别还没请求的订单下面 terminal or merchant
def add_info(request):
    try:
        barcode = request.GET.get("barcode", '')
        price = request.GET.get("price", '')
        product_name = request.GET.get("product_name",'')
        order_num = request.GET.get("order_num",'')
        print('商品名称：'+product_name+"价格："+price+barcode+order_num)
        if price and barcode and product_name and order_num:
            add_info = product_single.objects.get(order_num=order_num,
                                                  barcode=barcode)

            add_info.price = price
            add_info.product_name = product_name
            add_info.save()
            print('难到这里不执行吗？')
        if order_num != '':
            product_list = product_single.objects.filter(order_num=order_num)
            product_json = []
            # product_mate = {}
            for product in product_list.values():
                # print(product)
                product_mate = {"id": product['id'],
                                "barcode": product['barcode'],
                                "product_name": product['product_name'],
                                "price": product['price'],
                                "num": product['num'],
                                "User_ID": product['User_ID'],
                                "order_num": order_num,
                                }
                product_json.append(product_mate)
        print(json.dumps(product_json))
        return HttpResponse(json.dumps(product_json), content_type="appliction/josn")

        return  HttpResponse("这是成功的！")
    except Exception as e:
        return HttpResponsePermanentRedirect(e)


def appscan(request):

    return render(request,'webappscan.html')