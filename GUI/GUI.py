#! /usr/bin/
# -*-coding:utf-8-*-
#
#   create Jan 07, 2017 11:24:43 PM

import os
import sys
import time
from tkinter import *
#pandastable import Table
from pandastable import Table


# from click.decorators import command
import qrcode
import urllib.request
import requests
import json
import re
# from click.decorators import command
# sqlalchemy
from sqlalchemy import Column,String,create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from docutils.nodes import image
from collections import __main__




form = Tk()
form.geometry("900x650+1563+143")
form.title("SelfCheck")
# top = Toplevel()
# top.geometry("900x650+1563+143")
# top.title("SelfCheck")
# # top.attributes("-topmost",1)
# top.wm_attributes("-topmost",1)#让Toplevel 显示在最上层 


font3 = "-family {Microsoft YaHei UI} -size 9 -weight "  \
    "normal -slant roman -underline 0 -overstrike 0"
font5 = "-family 楷体 -size 16 -weight bold -slant roman "  \
    "-underline 0 -overstrike 0"
font7 = "-family 楷体 -size 22 -weight bold -slant roman "  \
    "-underline 0 -overstrike 0"
font8 = "-family 楷体 -size 22 -weight normal -slant roman "  \
            "-underline 0 -overstrike 0"    
font9 = "-family 楷体 -size 14 -weight normal -slant roman "  \
            "-underline 0 -overstrike 0"

       
path = 'table/'
name = 'Untitled 1.csv'



class mysql_connet():
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://root:root@192.168.1.11:3306/product_barcode?charset=utf8',echo=True)
#         self.code = '-'
#         self.product_name = '-'
#         self.price = '-'
#         self.num = '-'
    def find_product(self,barcode):
        self.connect = self.engine.connect()
        self.resu = self.connect.execute("select barcode,product_name,saleprice from product_info where barcode="+barcode) 
        r = self.resu.fetchone()
        code = r['barcode']
        product_name = r['product_name']
        price = r['saleprice']     
        self.resu.close()
        print(code,product_name,price)
        return [code,product_name,price]



order_num = 0 
class request_info ():
    
    def __new__(cls,*args,**kwargs):
        
        if not hasattr(cls,'_sgl'):
            cls._sgl = super().__new__(cls,*args,**kwargs)
        return cls._sgl
        
    def __init__(self):
        self.User_Id = '-' 
        self.Merchant_ID = '-'
        self.order_num = 0 
        self.order_status = '-' 
        self.create_time = ''
#         self.client = '-'
    
    def test_login(self,username,password):
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64)AppleWebKit/537.36 (KHTML, like Gecko)Chrome/45.0.2454.93 Safari/537.36',
                    'Origin':"http://192.168.1.11:8000",
                  } 
        self.client = requests.session() 
        url = 'http://192.168.1.11:8000/login/' 
      
        coki = self.client.get(url)  #第一次访问
        
        coki = self.client.get(url,headers=headers) #第二次访问才有cookie   
        print(coki.request.headers)

        csrftoken = coki.cookies['csrftoken']

        Cookie = 'csrftoken='+csrftoken

        
        data = {'username': username,
                'password':password,
                'csrfmiddlewaretoken':csrftoken,
                'source_url':'',
                    }
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64)\
                    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36',
                    'Cookie':Cookie,
                   }
        r = self.client.post(url,data=data,headers=headers) #这里是登录 
        print(r)
    def create_new_order(self):
       
        order = self.client.get('http://192.168.1.11:8000/neworder/')
        print(order.text)
        order_info = eval(order.text)
        self.User_Id = order_info['User_Id']#这里时是没有用户ID 
        self.Merchant_ID = order_info['Merchant_ID']
        self.order_num = order_info['order_num']
        self.order_status = order_info['order_status']
        self.create_time = order_info['create_time']
       
        print(self.User_Id,self.Merchant_ID ,self.order_num,self.order_status,self.create_time,)
        createQR(self.Merchant_ID,self.order_num,self.order_status)
    # ask this order have new info no price  
    #在这用条码，去本地数据库查询并写入.csv 文件      
    def request_newinfo(self):
        """
                突然停掉会报错
                AttributeError: 'str' object has no attribute 'get'
        """
        if type(self.client) is 'str':
            pass
        else:
            newinfo = self.client.get('http://192.168.1.11:8000/ask_new_info/?order_num='+str(self.order_num))
#         except :
#             pass
        
        list_info = eval(newinfo.text)
        write_info = []
        total_price = 0
        #条形码,商品名称,单  价,数    量,小   计
        #一行一行的写入文件中去
        
        for product_info in list_info:
            #ask product_name and price have values
            self.order_status = product_info['order_status']    
            self.User_Id = product_info["User_ID"]
#             order_num = product_info["order_num"]
            if product_info["product_name"] == "-" and product_info["price"] == 0:
               ask_sql = mysql_connet()
               result = ask_sql.find_product(str(product_info["barcode"]))
               product_info["product_name"]= result[1]
               product_info["price"] = result[2]
               print(result[1])
               #向服务器add price
               add = self.client.get('http://192.168.1.11:8000/add_info/?price='+str(product_info["price"])+'&product_name='+product_info["product_name"]+'&order_num='+str(self.order_num)+'&barcode='+str(product_info["barcode"])) #order_num
                                
            lit_total =  product_info["num"]*product_info["price"]
            print(lit_total)
            total_price = total_price+lit_total
            write_info.append(str(product_info["barcode"])+","+ 
                             product_info["product_name"]+","+ 
                             str(product_info["price"])+","+ 
                             str(product_info["num"])+","+ 
                             str(lit_total)+"\n"
                            )
            
        #write the first and last row
        write_info.insert(0,"条形码,商品名称,单  价,数    量,小   计 \n")
        write_info.append(",   ,   ,总　　计,"+str(total_price)+" \n")
        #保存文件  
        print('写入文件 '+write_info[1])   
        SaveToFile(path,name,write_info)
        
        
        
    
def SaveToFile(path,name,words_list):
    if path != '':
        if not os.path.exists(path):
            os.makedirs(path)
    file = open(path+name,'w')
    for i in range(0,len(words_list)):
        file.write(words_list[i])
    file.close()
    
    
#qrcode 二维码生成
def createQR(Merchant_ID,order_num,order_status):
    global img2
    q = qrcode.main.QRCode()
    q.add_data(Merchant_ID+"+"+str(order_num)+"+"+order_status)
    q.make()
    m = q.make_image()
    m.save('tey.png') 
    img2 = PhotoImage(file="tey.png")

ask = request_info()
ask.test_login(username='darunfa5',password='123456')   

# def dis_order_info():
#     
#     ask.request_newinfo()
#     if ask.User_Id != '' or ask.User_Id != 'xxx':
#         top.destroy()        
#     pt.importCSV('table/Untitled 1.csv')
#     form.after(200, dis_order_info)


Frame1 = Frame(form)
Frame1.place(relx=0.02, rely=0.26, relheight=0.7, relwidth=0.96)
Frame1.configure(relief=GROOVE)
Frame1.configure(borderwidth="2")
Frame1.configure(relief=GROOVE)
Frame1.configure(background="#d9d9d9")
Frame1.configure(highlightbackground="#d9d9d9")
Frame1.configure(highlightcolor="black")
Frame1.configure(width=865)

pt = Table(Frame1)
pt.show()

def request_dis_form():
    ask.request_newinfo()
    
    #后重启
    print(ask.order_status)
    if ask.order_status != 'NL':
        clean_ask() #清除ASK 类的参数。
        
        topAPP = Top_Toplevel()#重新创建一个界面。
        topAPP.frist_step() #显示第一个面页。
        form.update()
        form.deiconify()

# 清空前面显示的所有参数 这里为什么要这样做，是因为，把ASK请求写成了单例模式
def clean_ask():
    ask.User_Id = '-' 
    ask.Merchant_ID = '-'
    ask.order_num = 0 
    ask.order_status = '-' 
    ask.create_time = ''
    ask.client = '-'  #完成后报错是没有任何问题的。
    write_info=[]
    write_info.insert(0,"条形码,商品名称,单  价,数    量,小   计 \n")
    write_info.append(",   ,   ,总　　计,"+" \n")
    SaveToFile(path,name,write_info)


class greetings():
    def __init__(self):
        self.greeting = Toplevel()
        self.greeting.geometry("900x650+1563+143")
        self.greeting.title("SelfCheck")
        # top.attributes("-topmost",1)
        self.greeting.wm_attributes("-topmost",1)#让Toplevel 显示在最上层 
        self.i = 1
    def dis_greetings(self):    
          
        button = Button(self.greeting)
        button.configure(activebackground="#d9d9d9")
        button.place(relx=0.41, rely=0.43, height=88, width=199)
        button.configure(activeforeground="#000000")
        button.configure(background="#d9d9d9")
        button.configure(font=font5)
        button.configure(disabledforeground="#a3a3a3")
        button.configure(foreground="#000000")
        button.configure(highlightbackground="#d9d9d9")
        button.configure(highlightcolor="black")
        button.configure(pady="0")
        button.configure(text="成功付款，谢谢惠顾！")
        button.configure(width=199)
        self.greeting.after(1500, self.dis_greetings)
        
    def close(self):
        self.greeting.destroy()

    

def dis_form():
    
    request_dis_form()
    pt.importCSV('table/Untitled 1.csv')
    
    Label1 = Label(form)
    Label1.place(relx=0.04, rely=0.02, height=73, width=807)
    Label1.configure(activebackground="#f9f9f9")
    Label1.configure(activeforeground="#ff8040")
    Label1.configure(background="#d9d9d9")
    Label1.configure(disabledforeground="#a3a3a3")
    Label1.configure(font=font8)
    Label1.configure(foreground="#000000")
    Label1.configure(highlightbackground="#d9d9d9")
    Label1.configure(highlightcolor="black")
    Label1.configure(text='''超市通自助结帐系统''')
    
    Label2 = Label(form)
    Label2.place(relx=0.02, rely=0.18, height=43, width=117)
    Label2.configure(background="#d9d9d9")
    Label2.configure(disabledforeground="#a3a3a3")
    Label2.configure(font=font9)
    Label2.configure(foreground="#000000")
    Label2.configure(text='''购物单号：''')
    Label2.configure(width=117)
    
    Label3 = Label(form)
    Label3.place(relx=0.14, rely=0.18, height=43, width=147)
    Label3.configure(activebackground="#f9f9f9")
    Label3.configure(activeforeground="black")
    Label3.configure(background="#d9d9d9")
    Label3.configure(disabledforeground="#a3a3a3")
    Label3.configure(font=font9)
    Label3.configure(foreground="#000000")
    Label3.configure(highlightbackground="#d9d9d9")
    Label3.configure(highlightcolor="black")
    Label3.configure(text=ask.order_num)
    
    Label4 = Label(form)
    Label4.place(relx=0.52, rely=0.18, height=43, width=117)
    Label4.configure(activebackground="#f9f9f9")
    Label4.configure(activeforeground="black")
    Label4.configure(background="#d9d9d9")
    Label4.configure(disabledforeground="#a3a3a3")
    Label4.configure(font=font9)
    Label4.configure(foreground="#000000")
    Label4.configure(highlightbackground="#d9d9d9")
    Label4.configure(highlightcolor="black")
    Label4.configure(text='''消费用户：''')
    
    Label5 = Label(form)
    Label5.place(relx=0.66, rely=0.18, height=43, width=157)
    Label5.configure(activebackground="#f9f9f9")
    Label5.configure(activeforeground="black")
    Label5.configure(background="#d9d9d9")
    Label5.configure(disabledforeground="#a3a3a3")
    Label5.configure(font=font9)
    Label5.configure(foreground="#000000")
    Label5.configure(highlightbackground="#d9d9d9")
    Label5.configure(highlightcolor="black")
    Label5.configure(text=ask.User_Id)
    form.after(1000,dis_form)




class Top_Toplevel():
    def __init__(self): 
        self.top = Toplevel()
        self.top.geometry("900x650+1563+143")
        self.top.title("SelfCheck")
        # top.attributes("-topmost",1)
        self.top.wm_attributes("-topmost",1)#让Toplevel 显示在最上层 
    def control_request(self):
        
        print('这里是查看有没有order_num：'+str(ask.order_num)+"商家名称："+ask.Merchant_ID)
        if ask.order_num == 0 or ask.order_num =='':
            ask.test_login(username='darunfa5',password='123456')     
            ask.create_new_order()
    #       
                               
        if ask.User_Id != '-':
            ask.request_newinfo()
        else:
            self.top.destroy()   
            dis_form()
        
    def display_qrcode(self):
        
        self.control_request()
          
        disqr = Label(self.top)
        disqr.place(relx=0.37, rely=0.31, height=290, width=290)
        disqr.configure(activebackground="#f9f9f9")
        disqr.configure(activeforeground="black")
        disqr.configure(background="#d9d9d9")
        disqr.configure(disabledforeground="#a3a3a3")
        disqr.configure(foreground="#000000")
        disqr.configure(highlightbackground="#d9d9d9")
        disqr.configure(highlightcolor="black")
        disqr.configure(image=img2)
        
        Label2 = Label(self.top)
        Label2.place(relx=0.31, rely=0.08, height=93, width=387)
        Label2.configure(activebackground="#f9f9f9")
        Label2.configure(activeforeground="black")
        Label2.configure(background="#d9d9d9")
        Label2.configure(disabledforeground="#a3a3a3")
        Label2.configure(font=font5)
        Label2.configure(foreground="#000000")
        Label2.configure(highlightbackground="#d9d9d9")
        Label2.configure(highlightcolor="black")
        Label2.configure(text='''请打开APP扫描二维码''')
        print('查看消费用户名：'+ask.User_Id)
        if ask.User_Id == 'xxx':
            self.top.after(1000, self.display_qrcode)         #1秒钟刷新
        else:
            self.top.destroy()
            dis_form() 
         
    def frist_step(self):
        button = Button(self.top)
        button.configure(activebackground="#d9d9d9")
        button.place(relx=0.41, rely=0.43, height=88, width=199)
        button.configure(activeforeground="#000000")
        button.configure(background="#d9d9d9")
        button.configure(command=self.display_qrcode) #这里是主页面调用的函数
        button.configure(font=font5)
        button.configure(disabledforeground="#a3a3a3")
        button.configure(foreground="#000000")
        button.configure(highlightbackground="#d9d9d9")
        button.configure(highlightcolor="black")
        button.configure(pady="0")
        button.configure(text="自助结账")
        button.configure(width=199)

   
#不断询问更新1s
if __name__=="__main__": 
    topAPP = Top_Toplevel()
    topAPP.frist_step() 
    form.mainloop()
   
   
    
    
    
    
    
    