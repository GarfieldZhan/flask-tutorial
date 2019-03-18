# 命令函数
import click
from watchlist import db,app
from watchlist.models import User,Movie

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
    else:
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