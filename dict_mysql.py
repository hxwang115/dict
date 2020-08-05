"""
数据库操作模块
自定义数据库类
"""
import pymysql
import hashlib


class Database:
    def __init__(self, host='localhost',
                 port=3306,
                 user='root',
                 password='unique',
                 database=None,
                 charset='utf8'):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.charset = charset
        self.connect_database()  # 连接数据库

    def connect_database(self):
        self.db = pymysql.connect(host=self.host,
                                  port=self.port,
                                  user=self.user,
                                  password=self.password,
                                  charset=self.charset,
                                  database=self.database)

    def create_cursor(self):
        """
        创建游标
        :return:
        """
        self.cur = self.db.cursor()

    def close(self):
        """
        关闭数据库
        :return:
        """
        self.db.close()

    def login_up(self, name, password):  # 注册函数
        # 密码加密
        hash = hashlib.md5()
        hash.update(password.encode())
        password_1 = hash.hexdigest()
        # 查询用户是否存在
        sql = "select * from user where name='%s'" % name
        self.cur.execute(sql)
        if self.cur.fetchall():
            return '用户名存在,请重新注册'
        # 插入数据
        sql = "insert into user(name,password) values(%s,%s)"
        try:
            self.cur.execute(sql, [name, password_1])
            self.db.commit()
            return 'ok'
        except Exception as e:
            self.db.rollback()
            return e

    def login_in(self, name, password):
        hash = hashlib.md5()
        hash.update(password.encode())
        password_1 = hash.hexdigest()
        # 查询用户是否存在
        sql = "select name,password from user where name='%s'" % name
        self.cur.execute(sql)
        msg = self.cur.fetchone()
        if not msg:
            return '用户不存在,请重新输入或注册'
        if msg[1] == password_1:
            return 'ok'
        elif msg[1] != password_1:
            print(msg)
            return '密码错误'

    def search(self,dict):
        """
        查词处理
        :param dict:
        :return:
        """
        # 查找单词意思
        sql = "select mean from words where word=%s"
        self.cur.execute(sql,[dict])
        re = self.cur.fetchone()
        if not re:
            return '未找到单词'
        else:
            return re[0]
    def insert_record(self,name,dict):
        sql = "insert into hist(name,word) values(%s,%s)"
        try:
            self.cur.execute(sql, [name, dict])
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return e
    # 查询10条历史记录
    def select_record(self,name):
        sql = "select name,word,time from hist where name=%s order by time desc limit 10"
        self.cur.execute(sql,[name])
        re = self.cur.fetchall()
        return re

if __name__ == '__main__':
    db = Database(database='dict')
    db.create_cursor()
    print(db.select_record("789"))
