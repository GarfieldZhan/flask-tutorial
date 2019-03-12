from flask import Flask,render_template,redirect
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click

#判断系统类型并做出前缀的改变
WIN = sys.platform.startswith('win')
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)

# windows系统sqlite:///，其他系统sqlite:////
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  #关闭对模型修改的监控

#在扩展类实例化之前加载配置
db = SQLAlchemy(app)

#使用模型类创建数据表，用户信息,
class User(db.Model):   #表名是user，自动处理成小写
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))

#电影信息
class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

#编写自定义命令完成自动执行数据库表操作
@app.cli.command()  #注册为命令
@click.option('--drop',is_flag=True,help='Create after drop.')  #设置选择项
def initdb(drop):
    """Initialize the db"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialized db") #输出提示信息

#自定义 生成虚拟数据并存入数据库 的命令
@app.cli.command()
def forge():
    """Generate fake data"""
    db.create_all()
    name = "Garfield Zhan"
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo("Done")



@app.route('/')
def index():
    user = User.query.first()  #读取第一个用户
    movies = Movie.query.all()  #读取所有的电影
    return render_template('index.html',user=user,movies=movies)


if __name__ == '__main__':
    app.run()
