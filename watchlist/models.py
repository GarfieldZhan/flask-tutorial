# 模型类
from watchlist import db
from werkzeug.security import generate_password_hash,check_password_hash  # 用于生成和校验passwd
from flask_login import  UserMixin

#使用模型类创建数据表，用户信息,
class User(db.Model,UserMixin):   #表名是user，自动处理成小写
    #UserMixin由Flask-Login提供，继承这个类会拥有几个判断认证属性的方法，current_user.is_authenticated在用户登录时会返回True
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    passwd_hash = db.Column(db.String(128))

    def set_passwd(self,passwd):
        self.passwd_hash = generate_password_hash(passwd)

    def check_passwd(self,passwd):
        return check_password_hash(self.passwd_hash,passwd)

#电影信息
class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))