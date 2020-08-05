"""
用 TCP套接字建立网络连接
"""
from socket import *
import signal, sys,time
from multiprocessing import Process
from dict_mysql import Database

# 全局变量
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST, PORT)
db = Database(database='dict')


def login_up(c, data):
    """
    注册函数
    :param c:
    :param data: 接受的客户端的消息
    :return:
    """
    name = data.split(' ')[1]
    password = data.split(' ')[2]
    re = db.login_up(name, password)
    if re == 'ok':
        c.send(b'ok')
    else:
        c.send(re.encode())


def sign_in(c, data):
    """
    登录函数
    :param c:
    :param data: 客户端发送的用户名和密码
    :return:
    """
    name = data.split(' ')[1]
    password = data.split(' ')[2]
    re = db.login_in(name, password)
    if re == 'ok':
        c.send(b'ok')
    else:
        c.send(re.encode())


def search(c, data):
    name = data.split("_")[1]
    dict = data.split("_")[2]
    re = db.search(dict)  # 接收函数执行后的结果
    c.send(re.encode())
    db.insert_record(name, dict)

# 查历史记录
def select_record(c, data):
    name = data.split(' ')[1]
    re = db.select_record(name)
    if not re:
        c.send(b'fault')
        time.sleep(0.01)
    else:
        for i in re:
            c.send(i[:1].encode())
            time.sleep(0.1)
        c.send(b'##')


def request(c):
    """
    循环接收消息,处理消息
    :param c: 套接字
    :return:
    """
    db.create_cursor()  # 每个子进程创建游标
    while True:
        data = c.recv(1024).decode()
        if not data or data == 'OUT':
            c.close()
            sys.exit()
        elif data.split(' ')[0] == 'UP':
            login_up(c, data)  # 执行注册函数
        elif data.split(' ')[0] == 'IN':
            sign_in(c, data)  # 执行登录函数
        elif data.split('_')[0] == 'S':
            search(c, data)  # 执行查词函数
        elif data.split(' ')[0] == "R":
            select_record(c, data)


# 搭建网络模型
def main():
    socfd = socket()
    socfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socfd.bind(ADDR)
    socfd.listen(3)
    # 处理僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    # 循环等待客户端连接
    print("listen the port 8888")
    while True:
        try:
            c, addr = socfd.accept()
            print("connect from ...", addr)
        except KeyboardInterrupt:
            socfd.close()
            db.close()  # 关闭数据库
            sys.exit('服务端退出')  # 退出进程
        except Exception as e:
            print(e)
            continue
        # 为客户端创建子进程
        p = Process(target=request, args=(c,))
        p.daemon = True  # 父进程退出时子进程也退出
        p.start()  # 启动进程


# 搭建网络
if __name__ == '__main__':
    main()
