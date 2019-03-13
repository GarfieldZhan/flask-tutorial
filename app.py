from flask import Flask, render_template, redirect, flash, request, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click
from werkzeug.security import generate_password_hash,check_password_hash  # 用于生成和校验passwd
# Flask-Login提供一个current_user变量，注册这个函数后，若用户已登录，current_user变量的值会是当前用户的用户模型类记录
# current_user可在模板上下文中直接使用
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

#判断系统类型并做出前缀的改变
WIN = sys.platform.startswith('win')
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)

# windows系统sqlite:///，其他系统sqlite:////
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

app.config['SECRET_KEY']='dev' # app.secrect_key = 'dev'



# 实例化扩展类之外，还要实现一个“用户加载回调函数”
login_manager = LoginManager(app)  # 实例化扩展类


@login_manager.user_loader
def load_user(user_id):    # 创建用户加载回调函数，用户ID作为参数
    user = User.query.get(int(user_id))  # 用ID作为User模型的主键查询对应的用户
    return user

login_manager.login_view = 'login' # 未登录用户访问需要登录的网站，则重定向到login
# 使用login_manager.login_message来定义错误提示消息

#在扩展类实例化之前加载配置
db = SQLAlchemy(app)

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

#编写自定义命令完成自动执行数据库表操作
@app.cli.command()  #注册为命令
@click.option('--drop',is_flag=True,help='Create after drop.')  #设置选择项
def initdb(drop):
    """Initialize the db"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialized db") #输出提示信息

#自定义命令行生成管理员账号
@app.cli.command()
@click.option('--username',prompt=True,help='The username used to login')     #prompt?
@click.option('--passwd',prompt=True ,hide_input=True ,confirmation_prompt=True,help='The passwd used to login')
def admin(username,passwd):
    """Generate the admin account"""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo("Update the admin account")
        user.username = username
        user.set_passwd(passwd)
    if user is None:
        click.echo("Create the admin account")
        user = User(username=username,name='Admin')
        user.set_passwd(passwd)
        db.session.add(user)
    db.session.commit()
    click.echo('Done')

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

#登陆函数
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        passwd = request.form.get('passwd')

        if not username or not passwd:
            flash("Invalid input")
            return redirect(url_for('login'))

        user = User.query.first()
        if  username == user.username and user.check_passwd(passwd):
            login_user(user)
            flash("Login sucess.")
            return redirect(url_for('index'))
        flash("Invalid  username or password")
        return redirect(url_for('login'))

    return render_template('login.html')

#登出函数
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Goodbye")
    return redirect(url_for('index'))

@app.route('/settings', methods = ['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated!')
        return redirect(url_for('index'))
    return render_template('settings.html')

@app.route('/',methods=['POST','GET'])
#@login_required 因为新建条目的函数需要同时处理显示index页面的get请求和新建电影条目的post请求,因此在post请求中处理权限过滤
def index():
   # user = User.query.first()  #读取第一个用户
   # 新增电影条目
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash("Not authenticaed")
            return redirect(url_for('index'))
        title = request.form.get('title')
        year = request.form.get('year')
        #验证数据
        if not title or not year or len(year) > 4 or len(title) > 60:  #在inut中进行验证不可靠，服务器中追加验证
            flash("Invalid input")
            return redirect(url_for('index'))
        movie = Movie(title=title,year=year)
        db.session.add(movie)
        db.session.commit()
        flash("Item created")
        return redirect(url_for('index'))
    movies = Movie.query.all()  #读取所有的电影
    return render_template('index.html',movies=movies)

#编辑电影条目
@app.route('/movie/edit/<int:movie_id>',methods=['POST','GET'])
@login_required
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
@login_required
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
