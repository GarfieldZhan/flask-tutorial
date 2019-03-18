# 视图函数

from flask import render_template, redirect, request, url_for, flash
from flask_login import  login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie

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
            flash("Login success.")
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
        flash("Item updated")
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

