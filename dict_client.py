"""
tcp 客户端
协议 UP 表示注册请求
    IN 表示登录请求
    OUT 表示退出请求
    F 表示查词请求
"""
from socket import *
import getpass, sys

# 服务端地址
ADDR = ('127.0.0.1', 8888)
# 套接字,全局量
s = socket()
s.connect(ADDR)


def second_interface(name):
    """
    二级界面
    :return:
    """
    while True:
        print("""
        =================
        +   1.查词       +
        +   2.查词记录    +
        +   3.注销       +
        =================
        """)
        cmd = input("请输入命令:")
        if cmd == '1':
            search(name)  # 查词函数
        elif cmd == '2':
            select_record(name) # 查询历史记录


# 查历史记录
def select_record(name):

    msg = "R %s"%name
    s.send(msg.encode())
    while True:
        data = s.recv(512).decode()
        if data == "##":
            break
        elif data == "fault":
            print("您没有历史记录")
            break
        print(data)




# 登录函数
def do_sign_in():
    name = input("请输入用户名:")
    password = getpass.getpass("请输入密码:")
    msg = "IN %s %s" % (name, password)
    s.send(msg.encode())  # 发送到服务器
    data = s.recv(128).decode()  # 接收反馈
    if data == "ok":
        print("登录成功")
        second_interface(name)  # 进入二级界面
    else:
        print(data)


# 用户注册
def do_sign_up():
    while True:
        name = input("请输入用户名:")
        password = getpass.getpass("请输入密码:")
        password_1 = getpass.getpass("请再次输入密码:")
        if password != password_1:
            print("两次密码不一致")
            continue
        if ' ' in name or ' ' in password:
            print('用户名和密码不能有空格')
            continue
        msg = "UP %s %s" % (name, password)
        s.send(msg.encode())  # 发送给服务器
        data = s.recv(128).decode()  # 接受反馈
        if data == 'ok':
            print('注册成功')
        else:
            print(data)
        return


# 查词处理
def search(name):
    while True:
        dict = input("请输入单词:")
        # 退出查单词
        if dict == "##":
            break
        s.send(("S_%s_%s" % (name,dict)).encode())
        data = s.recv(2048).decode()
        print(dict,':',data)




# 搭建网络
def main():
    while True:
        print("""
        ===================
        +     1.登录       +
        +     2.注册       +
        +     3.注销       +
        ===================
        """)
        cmd = input("输入命令:")
        """
        1.表示登录
        2.表示注册
        3.表示客户端断开连接"""
        if cmd == '1':
            do_sign_in()  # 进行登录
        elif cmd == '2':
            do_sign_up()  # 进行注册
        elif cmd == '3':
            s.send(b'OUT')
            sys.exit("bye")
        else:
            print("请输入正确选项")


if __name__ == '__main__':
    main()
