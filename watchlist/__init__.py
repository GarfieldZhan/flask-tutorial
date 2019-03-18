# 包构造文件，创建程序实例
import os
import sys

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

#判断系统类型并做出前缀的改变
WIN = sys.platform.startswith('win')
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)
app.config['SECRET_KEY']='dev' # app.secrect_key = 'dev'
# windows系统sqlite:///，其他系统sqlite:////
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

#在扩展类实例化之前加载配置
db = SQLAlchemy(app)
# 实例化扩展类之外，还要实现一个“用户加载回调函数”
login_manager = LoginManager(app)  # 实例化扩展类

@login_manager.user_loader
def load_user(user_id):    # 创建用户加载回调函数，用户ID作为参数
    from watchlist.models import User
    user = User.query.get(int(user_id))  # 用ID作为User模型的主键查询对应的用户
    return user

login_manager.login_view = 'login' # 未登录用户访问需要登录的网站，则重定向到login
# 使用login_manager.login_message来定义错误提示消息

#注册一个上下文处理器函数，使得user在模板上下文中可用
@app.context_processor
def inject_user():
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)  #等同于返回{'user':user}

from watchlist import errors,commands,views