# 错误处理函数
from flask import render_template

from watchlist import app

@app.errorhandler(400) #使用errorhandle注册一个错误处理函数
def bad_request(e):   #e为异常对象
    return render_template('errors/400.html'),400   #返回模板和错误码，普通视图默认为200，所以不用写

@app.errorhandler(404) #使用errorhandle注册一个错误处理函数
def page_not_found(e):   #e为异常对象
    return render_template('errors/404.html'),404   #返回模板和错误码，普通视图默认为200，所以不用写

@app.errorhandler(500) #使用errorhandle注册一个错误处理函数
def internal_server_error(e):   #e为异常对象
    return render_template('errors/500.html'),500   #返回模板和错误码，普通视图默认为200，所以不用写

