from flask import Flask,render_template,redirect,flash,request,url_for
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

app.config['SECRET_KEY']='dev' #app.secrect_key = 'dev'

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

#注册一个上下文处理器函数，使得user在模板上下文中可用
@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)  #等同于返回{'user':user}

@app.route('/',methods=['POST','GET'])
def index():
   # user = User.query.first()  #读取第一个用户
   # 新增电影条目
    if request.method == 'post':
        title = request.form.get('title')
        year = request.form.get('year')
        #验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:  #在inut中进行验证不可靠，服务器中追加验证
            flash("Invalid input")
            return redirect(url_for('index'))
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.commit()
        flash("Item created")
        return render_template(url_for("index"))
    movies = Movie.query.all()  #读取所有的电影
    return render_template('index.html',movies=movies)

#编辑电影条目
@app.route('/movie/edit/<int:movie_id>',methods=['POST','GET'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == "POST":
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash("Invalid input")
            return redirect(url_for('edit',movie_id=movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash("Item created")
        return redirect(url_for("index"))
    return render_template('edit.html',movie=movie)

#删除电影条目
@app.route('/movie/delete/<int:movie_id>',methods=["POST"])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("Item deleted")
    return redirect(url_for("index"))

@app.errorhandler(404) #使用errorhandle注册一个错误处理函数
def page_not_found(e):   #e为异常对象
   # user = User.query.first()
    return render_template('404.html'),404   #返回模板和错误码，普通视图默认为200，所以不用写

if __name__ == '__main__':
    app.run()
