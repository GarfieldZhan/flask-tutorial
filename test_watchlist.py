import unittest
from watchlist import app, db
from watchlist.models import User, Movie
from watchlist.commands import forge, initdb

class WatchlistTestCase(unittest.TestCase):
    #在测试之前设定
    def setUp(self):
        # 更新配置
        app.config.update(
            # 开启测试模式
            TESTING=True,
            # 使用内存型数据库，不会干扰已存在数据库，且速度快
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        # 创建数据库和表
        db.create_all()
        # 创建测试数据，一个用户，一个电影条目
        user = User(name='Test',username='test')
        user.set_passwd('123')
        movie = Movie(title='Test Movie Title',year='2019')
        # 使用add_all一次添加多个模型实例，传入列表
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()   # 创建测试客户端，模拟客户端请求
        self.runner = app.test_cli_runner()   # 创建测试命令运行器，触发自定义命令

    # 在测试之后做清理工作
    def tearDown(self):
        db.session.remove()  # 清除数据库会话
        db.drop_all()    # 删除数据库表

    # 测试程序实例是否存在
    def test_app_exists(self):
        self.assertIsNotNone(app)

    # 测试是否处于测试模式
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    # 测试客户端
    # 测试404页面
    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertEqual(response.status_code, 200)

    # 辅助方法，用于登录用户
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            passwd='123'
        ), follow_redirects=True)   # follow_redirects=True跟随重定向

    # 测试创建条目
    def test_create_item(self):
        self.login()

        # 测试成功创建条目
        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('New Movie', data)
        self.assertIn('Item created', data)

         # 测试创建条目,但是电影标题为空
        response = self.client.post('/', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created', data)
        self.assertIn('Invalid input', data)

        # 测试创建条目,但是年份为空
        response = self.client.post('/', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created', data)
        self.assertIn('Invalid input', data)

    # 测试更新条目
    def test_update_item(self):
        self.login()

        # 测试更新页面
        response = self.client.get('movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie Title', data)
        self.assertIn('2019', data)

        # 测试更新条目操作
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated', data)
        self.assertIn('New Movie Edited', data)

        # 测试更新条目操作,但是电影标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated', data)
        self.assertIn('Invalid input', data)

        # 测试更新条目操作,但是年份为空
        response = self.client.post('/movie/edit/1', data=dict(
            title='New Movie Edited Again',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated', data)
        self.assertNotIn('New Movie Edited Again', data)
        self.assertIn('Invalid input', data)

    # 测试删除数据
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted', data)
        self.assertNotIn('Test Mpvie Title', data)

    ## 测试认证相关功能
    # 测试登陆保护
    def  test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('<form method="POST">', data)

    # 测试登录
    def  test_login(self):

        response = self.client.post('/login', data=dict(
            username='test',
            passwd='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success', data)
        self.assertIn('Logout', data)
        self.assertIn('Edit', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('<form method="POST">', data)

    # 测试错误密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            passwd='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success', data)
        self.assertIn('Invalid  username or password', data)

    # 测试错误用户名登录
        response = self.client.post('/login', data=dict(
            username='test1',
            passwd='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success', data)
        self.assertIn('Invalid  username or password', data)

    # 测试空用户名登录
        response = self.client.post('/login', data=dict(
            username='',
            passwd='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success', data)
        self.assertIn('Invalid input', data)

    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('<form method="POST">', data)

    # 测试设置
    def test_settings(self):
        self.login()

        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Your name', data)
        self.assertIn('Settings', data)

        # 测试更新设置
        response = self.client.post('/settings', data=dict(
            name='zjf'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('zjf', data)
        self.assertIn('Settings updated', data)

        # 测试更新设置
        response = self.client.post('/settings', data=dict(
            name=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input', data)
        self.assertNotIn('Settings updated', data)

    # 测试命令,使用self.test_cli_runner()

    #  测试虚拟数据
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done', result.output)
        self.assertNotEqual(Movie.query.count(),0)

    # 测试初始化数据
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized db', result.output)

    # 测试生成管理员账户
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username', 'zjf', '--passwd', '123'])
        self.assertIn('Create the admin account', result.output)
        self.assertIn('Done', result.output)
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username, 'zjf')
        self.assertTrue(User.query.first().check_passwd('123'))

    # 测试更新管理员账户
    def test_admin_command_update(self):

        result = self.runner.invoke(args=['admin', '--username', 'garfield', '--passwd', '456'])
        self.assertIn('Update the admin account', result.output)
        self.assertIn('Done', result.output)
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username, 'garfield')
        self.assertTrue(User.query.first().check_passwd('456'))

if __name__ == '__main__':
    unittest.main()



