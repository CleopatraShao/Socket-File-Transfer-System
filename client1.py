#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#client

import tkinter as tk#采用Tkinter进行窗口视窗设计
import tkinter.messagebox
import pickle

import socket
import os
import hashlib
import sys

try:
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)#生成socket连接对象
except:
    print("400: Fail to create socket.")
    sys.exit()

ip_port =("127.0.0.1", 6543)
try:
    client.connect(ip_port)#进行连接
    print("Succeed to connect to the server.")
except:
    print("401: Problems in IP or port.")
    sys.exit()

      
def get_func():
    def get_files():
        filename = file_name.get()
        filedir = file_path.get()
        content = "get" + " " + filename + " " + filedir
        client.send(content.encode("utf-8"))

        server_response = client.recv(1024)
        file_size = int(server_response.decode("utf-8"))
        if file_size==-1:
            tkinter.messagebox.showerror('402', 'No such file in server.')
            
        else:
            #接受文件
            client.send("Ready to recieve".encode("utf-8"))
        
               
            f = open(filedir+'/'+filename, "wb")
            received_size = 0
            m = hashlib.md5()

            while received_size < file_size:
                size = 0
                if file_size - received_size > 1024: #分批接收数据
                    size = 1024
                else:  #当为最后一次接收时
                    size = file_size - received_size

                data = client.recv(size)
                data_len = len(data)
                received_size += data_len

                m.update(data)
                f.write(data)

            f.close()

            # md5值校验
            md5_sever = client.recv(1024).decode("utf-8")
            md5_client = m.hexdigest()
            if md5_sever == md5_client:
                mes = 'Header received:' + str(file_size) + "   Size actually recieved:" + str(received_size) + "  MD5 check pass"
                tkinter.messagebox.showinfo('Successfully Get!', mes)
            else:
                tkinter.messagebox.showerror('Error', 'MD5 check failed.')
 
        window_get.destroy()
 
    #定义窗口上的窗口
    window_get = tk.Toplevel(window)
    window_get.geometry('300x200')
    window_get.title('Get Files from Server')#窗口标题——用于展示功能
 
    file_name = tk.StringVar() #将输入的注册名赋值给变量
    
    tk.Label(window_get, text='File Name: ').place(x=10, y=10)  # 将file name放置在坐标（10,10）处
    entry_file_name = tk.Entry(window_get, textvariable=file_name)  # 创建一个注册名的entry，变量为new_name
    entry_file_name.place(x=130, y=10)
 
    file_path = tk.StringVar()
    tk.Label(window_get, text='File Path: ').place(x=10, y=50)
    entry_file_path = tk.Entry(window_get, textvariable=file_path)
    entry_file_path.place(x=130, y=50)
 
    
    btn_comfirm = tk.Button(window_get, text='OK', command=get_files)
    btn_comfirm.place(x=180, y=120)
    
    
def put_func():
    def put_files():
        filedir = file_path.get()
        content = "put" + " "  + filedir
        
        
        if os.path.isfile(filedir):
            client.send(content.encode("utf-8"))
            
            header = os.stat(filedir).st_size
            client.send(str(header).encode("utf-8"))

            client.recv(1024) 
            m = hashlib.md5()
            f = open(filedir, "rb")
            for line in f:
                client.send(line)
                m.update(line)
            f.close()

            # 发送md5值进行校验
            md5 = m.hexdigest()
            client.send(md5.encode("utf-8"))

            server_response = client.recv(1024)
            tkinter.messagebox.showinfo('OK', str(server_response.decode("utf-8")))

        else:
            tkinter.messagebox.showerror('403', 'No such file in client')

        window_put.destroy()
    window_put = tk.Toplevel(window)
    window_put.geometry('300x200')
    window_put.title('Put Files to Server')#窗口标题——用于展示功能
 
    
 
    file_path = tk.StringVar()
    tk.Label(window_put, text='File Path: ').place(x=10, y=50)
    entry_file_path = tk.Entry(window_put, textvariable=file_path)
    entry_file_path.place(x=130, y=50)
 
    btn_comfirm = tk.Button(window_put, text='OK', command=put_files)
    btn_comfirm.place(x=180, y=120)
    
    
    
def ask_dir_func():
    def ask_dir_of_files():
        filename = file_name.get()
        content = "ask_dir" + " " + filename
        client.send(content.encode("utf-8"))
        
        server_response = client.recv(1024)
        filedir = str(server_response.decode("utf-8"))
        if filedir == "No such file":
            tkinter.messagebox.showerror('404', 'No such file in server or no right to visit its directory')
            print ("404: No such file in server or no right to visit its directory")
        elif len(filename) !=0:
            a = "The directory  of " + filename + " is " + filedir
            print (a)
            tkinter.messagebox.showinfo('OK', a)
        else:
            a = "The directories and files of current path are: " + filedir
  
            tkinter.messagebox.showinfo('OK', a)
        window_ask.destroy()
    window_ask = tk.Toplevel(window)
    window_ask.geometry('300x200')
    window_ask.title('List All Directories or Ask File Directory')#窗口标题——用于展示功能
 
    
 
    file_name = tk.StringVar()
    tk.Label(window_ask, text='File Name: ').place(x=10, y=50)
    entry_file_path = tk.Entry(window_ask, textvariable=file_name)
    entry_file_path.place(x=130, y=50)
 
    btn_comfirm = tk.Button(window_ask, text='OK', command=ask_dir_of_files)
    btn_comfirm.place(x=180, y=120)
        
if True:
    #建立图形界面窗口
    window = tk.Tk()
    
    #给可视化窗口起名
    window.title('客户与服务器间的文件传输协议')
    
    #设置窗口的大小
    window.geometry('500x300')#需要注意的是，这里的x为字母x
    
    #向窗口中插入背景图片
    canvas = tk.Canvas(window, width=500, height=200)
    image_file = tk.PhotoImage(file='background.gif')
    image = canvas.create_image(250, 0, anchor='n',image=image_file)
    canvas.pack(side='top')
    tk.Label(window, text='请根据需求选择以下功能',font=('微软雅黑', 15)).pack()

    #展示本文件传输协议的三大功能，用户通过鼠标按键选择对应功能
    btn_get = tk.Button(window, text='获取文件(get)', command=get_func, bg='lightcyan')
    btn_get.place(x=100, y=240)
    btn_put = tk.Button(window, text='存放文件(put)', command=put_func, bg='lightcyan')
    btn_put.place(x=200, y=240)
    btn_ask = tk.Button(window, text = '查询文件目录(ask_dir)', command=ask_dir_func, bg='lightcyan')
    btn_ask.place(x=300, y=240)
    
    #窗口循环显示，这样用户才能够多次操作
    window.mainloop()
client.close()


# In[ ]:





# In[ ]:





# In[ ]:




