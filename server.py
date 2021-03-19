#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#server

import socket
import os
import hashlib

import _thread

def GetFile(pre_path,filename ):#获取当前路径下的所有文件
    
    allFile=os.listdir(pre_path)
    
    for eachFile in allFile:#对每一个文件
        
        if eachFile==filename:
            return str(pre_path)#输出其路径
        
        elif os.path.isdir(pre_path+os.sep+eachFile):#如果文件是一个文件夹，那么需要进行递归操作
            try:#try-except可处理异常
                GetFile(pre_path+os.sep+eachFile, filename)
            except:
                continue
    res = "Fail to find file! Not existed!"
    return res
        

def child_connection(index, server, conn):#参考助教PPT上关于多线程的代码
    try:
        print("begin connection ", index)
        print("begin connection %d" % index)      
        conn.settimeout(5000)    
        #获得一个连接，然后开始循环处理这个连接发送的信息     
        while True:
            data = conn.recv(1024)  #接收
            if not data:  
                print("Client is disconnected.")#客户端断开连接
                break

            print("Received command：", data.decode("utf-8"))
            cmd = data.decode("utf-8").split(" ")[0]
        
        
            #get功能
            if cmd == "get":
                file_name = data.decode("utf-8").split(" ")[1]
                file_dir = data.decode("utf-8").split(" ")[2]
                
                if os.path.isfile(file_name):  # 判断文件存在

                    #显示发送文件的大小
                    head = os.stat(file_name).st_size  #获取文件大小       
                    conn.send(str(head).encode("utf-8"))  # 发送数据长度
                    print("Head sent：", head)

                    #发送文件内容
                    conn.recv(1024)#接收确认

                    m = hashlib.md5()
                    file_sent = open(file_name, "rb")
                    for line in file_sent:
                        conn.send(line)#发送数据
                        m.update(line)
                    file_sent.close()

                    #根据md5值校验
                    md5 = m.hexdigest()
                    conn.send(md5.encode("utf-8"))
                    print("md5:", md5)
                else:
                    head = -1#如果服务器端没有响应的文件就返回头部-1
                    conn.send(str(head).encode("utf-8"))
                    
            #put功能
            if cmd =="put":
                file_dir = data.decode("utf-8").split(" ")[1]
                server_response = conn.recv(1024)
                file_size = int(server_response.decode("utf-8"))
            
                print("Head received：", file_size)

                #接收文件内容
                conn.send("Ready to receive".encode("utf-8"))
                file_name = os.path.split(file_dir)[-1]
                file_received = open(file_name, "wb")
                actual_received_size = 0
                m = hashlib.md5()

                while actual_received_size < file_size:
                    size_single_time = 0
                    if file_size - actual_received_size > 1024:#分批接收
                        size_single_time = 1024
                    else:#最后一次接收
                         size_single_time = file_size - actual_received_size

                    data = conn.recv(size_single_time)#多次接收内容，接收大数据
                    data_len = len(data)
                    actual_received_size += data_len
                    print("Already Received：", int(actual_received_size * 100 / file_size), "%")

                    m.update(data)
                    file_received.write(data)

                file_received.close()

                print("Actual size of received file:", actual_received_size)

        # 3.md5值校验
                md5_sever = conn.recv(1024).decode("utf-8")
                md5_client = m.hexdigest()
                print("md5 of the server:", md5_sever)
                print("md5 of the client:", md5_client)
                if md5_sever == md5_client:
                    print("Succeed to check md5.Pass!")
                else:
                    print("Fail to check md5. Fail!")
                response = "100: Server successfully received.MD5 Check Pass!"  #传送成功的时候会发送确认信息告诉客户端
                
                conn.send(response.encode("utf-8"))  # 发送数据长度
                
            #查询服务器存放文件的目录
            if cmd == "ask_dir":
                try:
                    filename = data.decode("utf-8").split(" ")[1]
                except:
                    filename = ''
                if len(filename) == 0:
                    filedir = os.listdir()#如果缺省文件名，那么返回当前所在目录下的所有文件和文件名
                else:
                    filedir = GetFile(os.getcwd(),filename )
                conn.send(str(filedir).encode("utf-8"))
            
    except socket.timeout:  # 如果建立连接后，该连接在设定的时间内无数据发来，则time out       
        print('time out')   
    print("closing connection %d" % index)  # 当一个连接监听循环退出后，连接可以关掉
    conn.close()
    # 关闭连接，最后别忘了退出线程    
    _thread.exit_thread()
       
        
        
if __name__ == "__main__":
    
    print("Server is starting")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 6543))#配置soket，绑定IP地址和端口号
    server.listen(5)#设置最大允许连接数，各连接和server的通信遵循FIFO原则
    print( "Server is listenting port 8001, with max connection 5")
    
    index = 0
    while True:  # 循环轮询socket状态，等待访问
        
        conn, addr = server.accept()
        print("conn:", conn, "\naddr:", addr)
        
        index += 1       # 当获取一个新连接时，启动一个新线程来处理这个连接
        _thread.start_new_thread(child_connection, (index, server, conn))
        if index > 10:
            break
    server.close()


# In[ ]:





# In[ ]:




