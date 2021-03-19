# Socket-File-Transfer-System

## 实验简述

设计一个简单的文件传输协议，并完成以下功能：

**基本功能**

1. 实现客户与服务器之间的文件传递——get、put

2. 实现客户可查询服务器存放文件的目录

3. 实现客户可自定义文件存放的目录

4. 图形界面

**附加功能**

1. 多线程操作

2. 对传输文件进行md5校验，提升传输协议安全性

3. 客户可查询目录下所有文件

## 代码实现

为了实现客户与服务器之间的文件传递，需要从server和client两方分别进行考虑，因此创建两个代码文件，分别为server和client（后续实现多线程时会创建多个client，这将在多线程部分进行说明）。

在实现具体功能之前，首先需要对socket进行配置，绑定IP地址和端口号，同时设置最大允许连接数，并且各个连接和server的通信遵循FIFO原则：

```python
    server.bind(('127.0.0.1', 6543))#配置soket，绑定IP地址和端口号
    server.listen(5)#设置最大允许连接数，各连接和server的通信遵循FIFO原则
    print( "Server is listenting port 8001, with max connection 5")
```

在client中则需要尝试进行连接

```python
ip_port =("127.0.0.1", 6543)
try:
    client.connect(ip_port)#进行连接
    print("Succeed to connect to the server.")
except:
    print("401: Problems in IP or port.")
    sys.exit()
```

如果建立连接之后，这一连接在设定的时间内无数据传来，则返回`time out`

```python
    except socket.timeout:  
        print('time out')  
```

### get功能

首先通过`if`判断句进行功能的选择以及相应功能的实现，并且定义两个变量`file_name(文件名)`以及`file_dir(文件所在路径)`

```python
if cmd == "get":
	file_name = data.decode("utf-8").split(" ")[1]
	file_dir = data.decode("utf-8").split(" ")[2]
```

随后采用`os.path.isfile`判断文件是否存在，如果服务器端没有响应，那么就返回头部-1

```python
	if os.path.isfile(file_name):
	else:
		head = -1
		conn.send(str(head).encode("utf-8"))
```

而如果文件存在，则首先显示发送文件的大小，我这里将文件大小作为头部

```python
                    head = os.stat(file_name).st_size  #获取文件大小       
                    conn.send(str(head).encode("utf-8"))  # 发送数据长度
                    print("Head sent：", head)
```

随后开始发送文件的内容，首先进行接受确认

```python
                    conn.recv(1024)#接收确认
```

随后发送数据

```python
                    m = hashlib.md5()
                    file_sent = open(file_name, "rb")
                    for line in file_sent:
                        conn.send(line)#发送数据
                        m.update(line)
                    file_sent.close()
```

最后生成md5码并发送，方便进行后续校验：

```python
                    md5 = m.hexdigest()
                    conn.send(md5.encode("utf-8"))  # 发送md5值
                    print("md5:", md5)
```

以上是server中的功能代码，而在client中，可以通过定义函数get_files()来实现client方如何接受file。

首先获取客户输入的信息

```python
        filename = file_name.get()
        filedir = file_path.get()
        content = "get" + " " + filename + " " + filedir
        client.send(content.encode("utf-8"))
```

随后开始接受长度（我将长度作为文件头部），如果接收到的为-1，那么直接返回错误，表示服务器中找不到这一文件

```python
        server_response = client.recv(1024)
        file_size = int(server_response.decode("utf-8"))
        if file_size==-1:
            tkinter.messagebox.showerror('402', 'No such file in server.')
```

如果不是-1，那么就可以开始接受文件

```python
        else:
            #接受文件
            client.send("Ready to recieve".encode("utf-8"))
        
            f = open(filedir+'/'+filename, "wb")
```

这里定义了变量`received_size`并初始化为0，用来实时展示接受了多少文件的数据，方便后续debug

```python
            received_size = 0
            m = hashlib.md5()
```

当`received_size`小于`file_size`时，需要进行接受。为了解决粘包问题，这里采用多次准确接受部分数据的方式(在这里我设置为1024)。

```python
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
```

最后进行md5校验，根据md5码是否相同来判断接受的文件是否安全正确

```python
            md5_sever = client.recv(1024).decode("utf-8")
            md5_client = m.hexdigest()
            if md5_sever == md5_client:
                mes = 'Header received:' + str(file_size) + "   Size actually recieved:" + str(received_size) + "  MD5 check pass"
                tkinter.messagebox.showinfo('Successfully Get!', mes)
            else:
                tkinter.messagebox.showerror('Error', 'MD5 check failed.')
```

### put功能

依然通过`if`条件进行判断

```python
            if cmd =="put":
                file_dir = data.decode("utf-8").split(" ")[1]
                server_response = conn.recv(1024)
                file_size = int(server_response.decode("utf-8"))
            
                print("Head received：", file_size)
```

put和get的代码基本相同，只是一个为接受文件内容，一个为发送文件内容。接收文件内容也是通过1024作为阈值大小分步进行接受，这里直接给出代码，通过比较可以发现基本是相同的

```python
                conn.send("Ready to receive".encode("utf-8"))
                file_name = os.path.split(file_dir)[-1]
                file_received = open(file_name, "wb")
                actual_received_size = 0
                m = hashlib.md5()

                while actual_received_size < file_size:
                    size_single_time = 0
                    if file_size - actual_received_size > 1024:
                        size_single_time = 1024
                    else:
                         size_single_time = file_size - actual_received_size

                    data = conn.recv(size_single_time)
                    data_len = len(data)
                    actual_received_size += data_len
                    print("Already Received：", int(actual_received_size * 100 / file_size), "%")

                    m.update(data)
                    file_received.write(data)

                file_received.close()

                print("Actual size of received file:", actual_received_size)
```

最后进行md5码校验，校验代码与get功能的相同

```python
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
```

在client中则通过定义put_files()函数实现相应功能，代码与get基本相同

```python
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
```

### ask_dir功能

这里我实现了以下两个功能：

1. 客户可以查询服务器存放文件的目录
2. 客户可以查询目录下存放的所有文件

依然通过if条件判断句进行功能判断

```python
            if cmd == "ask_dir":
                try:
                    filename = data.decode("utf-8").split(" ")[1]
                except:
                    filename = ''
```

这里考虑到实际情况，为了方便用户的操作，定义：如果用户直接输入回车，即没有输入路径，则直接返回当前所在目录下的所有文件和文件名：

```python
                if len(filename) == 0:
                    filedir = os.listdir()#如果缺省文件名，那么返回当前所在目录下的所有文件和文件名
                else:
                    filedir = GetFile(os.getcwd(),filename )
                conn.send(str(filedir).encode("utf-8"))
```

由于需要获取当前目录下所有的文件和文件名，因此采用函数递归的方式进行查找，这里我定义了GetFile()函数

```python
def GetFile(pre_path,filename ):#获取当前路径下的所有文件
    
    allFile=os.listdir(pre_path)
    
    for eachFile in allFile:
        
        if eachFile==filename:
            return str(pre_path)#输出其路径
        
        elif os.path.isdir(pre_path+os.sep+eachFile):#如果文件是一个文件夹，那么需要进行递归操作
            try:
                GetFile(pre_path+os.sep+eachFile, filename)
            except:
                continue
    res = "Fail to find file! Not existed!"
    return res
```

之后在client中定义ask_dir_of_files()函数，首先获取输入并判断输入是否正确。如果不存在，则返回报错

```python
        filename = file_name.get()
        content = "ask_dir" + " " + filename
        client.send(content.encode("utf-8"))
        
        server_response = client.recv(1024)
        filedir = str(server_response.decode("utf-8"))
        if filedir == "No such file":
            tkinter.messagebox.showerror('404', 'No such file in server or no right to visit its directory')
            print ("404: No such file in server or no right to visit its directory")
```

如果找到，则进行输出

```python
        elif len(filename) !=0:
            a = "The directory  of " + filename + " is " + filedir
            print (a)
            tkinter.messagebox.showinfo('Result', a)
        else:
            a = "The directories and files of current path are: " + filedir
```

### md5校验

md5码校验在前面的功能实现中已经包含了，这里直接贴出代码（以get为例）

server:

```python
                    md5 = m.hexdigest()
                    conn.send(md5.encode("utf-8"))
                    print("md5:", md5)
```

client:

```python
            md5_sever = client.recv(1024).decode("utf-8")
            md5_client = m.hexdigest()
            if md5_sever == md5_client:
                mes = 'Header received:' + str(file_size) + "   Size actually recieved:" + str(received_size) + "  MD5 check pass"
                tkinter.messagebox.showinfo('Successfully Get!', mes)
            else:
                tkinter.messagebox.showerror('Error', 'MD5 check failed.')
```

## 多线程

```python
def child_connection(index, server, conn):#参考助教PPT上关于多线程的代码
    try:
        print("begin connection ", index)
        print("begin connection %d" % index)      
        conn.settimeout(500)    
        #获得一个连接，然后开始循环处理这个连接发送的信息     
        while True:
            data = conn.recv(1024)  #接收
            if not data:  
                print("Client is disconnected.")#客户端断开连接
                break

            print("Received command：", data.decode("utf-8"))
            cmd = data.decode("utf-8").split(" ")[0]
```

```python
            
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
```

## 图形界面

我采用了tkinter进行图形界面的设计。

首先设计总窗口（即展示三大功能，方便用户选择）。

第一步建立图形界面窗口，设置窗口大小并且给窗口起名

```python
    window = tk.Tk()
    
    window.title('客户与服务器间的文件传输协议')
    
    window.geometry('500x300')#需要注意的是，这里的x为字母x
```

为了让窗口看起来更加美观，在其中插入背景图片

```python
    canvas = tk.Canvas(window, width=500, height=200)
    image_file = tk.PhotoImage(file='background.gif')
    image = canvas.create_image(250, 0, anchor='n',image=image_file)
    canvas.pack(side='top')
```

在图片下方给出功能选择按钮，方便用户通过鼠标点击选择相应功能

```python
    tk.Label(window, text='请根据需求选择以下功能',font=('微软雅黑', 15)).pack()
	btn_get = tk.Button(window, text='获取文件(get)', command=get_func, bg='lightcyan')
    btn_get.place(x=100, y=240)
    btn_put = tk.Button(window, text='存放文件(put)', command=put_func, bg='lightcyan')
    btn_put.place(x=200, y=240)
    btn_ask = tk.Button(window, text = '查询文件目录(ask_dir)', command=ask_dir_func, bg='lightcyan')
    btn_ask.place(x=300, y=240)
```

最后，根据实际情况来说，用户需要多次进行不同的操作，因此需要让这个窗口循环显示，这样用户才能够不断进行后续的其他功能操作

```C
    window.mainloop()
```

之后就是设计各个不同功能下的窗口，功能很简单，这里以get功能为例详细介绍，后续的put以及ask_air直接贴出代码。

首先需要定义长在窗口上的窗口，设置窗口大小并且给出标题

```python
    window_get = tk.Toplevel(window)
    window_get.geometry('300x200')
    window_get.title('Get Files from Server')#窗口标题——用于展示功能
```

因为get功能需要得知文件名以及文件路径，因此给出两个输入框方便用户输入

```python
    file_name = tk.StringVar() #将输入的注册名赋值给变量
    
    tk.Label(window_get, text='File Name: ').place(x=10, y=10)  # 将file name放置在坐标（10,10）处
    entry_file_name = tk.Entry(window_get, textvariable=file_name)  # 创建一个注册名的entry，变量为new_name
    entry_file_name.place(x=130, y=10)#设置放置的坐标
 
    file_path = tk.StringVar()
    tk.Label(window_get, text='File Path: ').place(x=10, y=50)
    entry_file_path = tk.Entry(window_get, textvariable=file_path)
    entry_file_path.place(x=130, y=50)
```

最后为显示结果的窗口

```python
    btn_comfirm = tk.Button(window_get, text='OK', command=get_files)
    btn_comfirm.place(x=180, y=120)
```

put功能

```python
    window_put = tk.Toplevel(window)
    window_put.geometry('300x200')
    window_put.title('Put Files to Server')#窗口标题——用于展示功能
 
    
 
    file_path = tk.StringVar()
    tk.Label(window_put, text='File Path: ').place(x=10, y=50)
    entry_file_path = tk.Entry(window_put, textvariable=file_path)
    entry_file_path.place(x=130, y=50)
 
    btn_comfirm = tk.Button(window_put, text='OK', command=put_files)
    btn_comfirm.place(x=180, y=120)
```

ask_dir功能

```python
    window_ask = tk.Toplevel(window)
    window_ask.geometry('300x200')
    window_ask.title('List All Directories or Ask File Directory')#窗口标题——用于展示功能
 
    
 
    file_name = tk.StringVar()
    tk.Label(window_ask, text='File Name: ').place(x=10, y=50)
    entry_file_path = tk.Entry(window_ask, textvariable=file_name)
    entry_file_path.place(x=130, y=50)
 
    btn_comfirm = tk.Button(window_ask, text='OK', command=ask_dir_of_files)
    btn_comfirm.place(x=180, y=120)
```
