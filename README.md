
>这篇文章记录了我对 Django Rest API 接口进行自动化测试的过程。对接执行POST，DELETE，PUT，GET请求，会对系统中的数据进行增删改查，每执行一次增删改操作后，系统中的数据就会发生变化，为了解决这个问题，需要在每次执行接口请求之前对数据进行初始化，故本篇文章侧重于对接口测试过程中数据的处理，结合unnittest+Requests+Jenkins形成一个完整的接口自动化测试框架。

- 代码已上传至我的github，地址：

https://github.com/wuyongsheng/Restful_Api_Test

###  用到的一些工具、模块及作用
- Django：提供待测试的API接口
- Requests：用来发起HTTP请求
- Pymysql：对接口测试的数据进行操作
- Unittest：单元测试框架，对测试结果进行断言
- logging：python的日志模块，对测试执行过程进行记录，方便定位问题
- PyYAML: python的Yaml库，用来存放初始化数据
- BSTestRunner：用来成产测试报告，对测试报告进行美化
- Jenkins：持续集成工具，可设置测试过程定期执行或者手动执行

### 测试脚本目录结构
目录结构及各文件的作用

![目录结构.jpg](https://upload-images.jianshu.io/upload_images/12273007-b1831951b175b714.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

### 测试过程

#### 搭建Django rest api 环境
基本的搭建的过程这里面不做介绍，这里介绍数据库迁移过程。

在Django自带的数据库是Sqllite3，要将数据库迁移到MySQL方便操作。需要注意的是Django 2.1.X版本不支持MySQL 5.5以下的版本，我之前用的是5.5的版本，迁移时报了错，在网上查了，是因为版本不兼容。

使用如下命令进行数据库迁移：

- python manage.py makemigrations api
- python manage.py migrate

迁移完成后，需要创建一个超级管理员账号进行登录，使用如下命令：

- python manage.py createsuperuser

创建超级管理员账号后，我们就可以用超级管理员账号登录Django了，登录后的界面如下（访问地址：http://127.0.0.1:8009/ ，端口号可以自己指定）：

![Django.jpg](https://upload-images.jianshu.io/upload_images/12273007-af58bcc83a845f3a.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

在浏览器地址栏输入：

http://127.0.0.1:8009/users/  可以返回系统中所有用户信息，用户信息包含url，username，email，groups字段，返回信息格式如下：

```
GET /users/
HTTP 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

[
    {
        "url": "http://127.0.0.1:8009/users/1/",
        "username": "wysh1",
        "email": "wysh555@163.com",
        "groups": "http://127.0.0.1:8009/groups/1/"
    },
    {
        "url": "http://127.0.0.1:8009/users/2/",
        "username": "wysh2",
        "email": "wysh2@qq.com",
        "groups": "http://127.0.0.1:8009/groups/2/"
    },
    {
        "url": "http://127.0.0.1:8009/users/3/",
        "username": "wysh3",
        "email": "wysh3@qq.com",
        "groups": "http://127.0.0.1:8009/groups/3/"
    },
    {
        "url": "http://127.0.0.1:8009/users/5/",
        "username": "wysh5",
        "email": "wysh5@qq.com",
        "groups": "http://127.0.0.1:8009/groups/5/"
    },
    {
        "url": "http://127.0.0.1:8009/users/6/",
        "username": "wysh6",
        "email": "wysh5@163.com",
        "groups": "http://127.0.0.1:8000/groups/2/"
    }
]
```
在浏览器地址栏输入：

http://127.0.0.1:8009/groups/  可以返回系统中所有用户组信息，用户信息包含 url，name 字段，返回信息格式如下：
```
GET /groups/
HTTP 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

[
    {
        "url": "http://127.0.0.1:8009/groups/2/",
        "name": "Boss"
    },
    {
        "url": "http://127.0.0.1:8009/groups/3/",
        "name": "wysh_group3"
    },
    {
        "url": "http://127.0.0.1:8009/groups/4/",
        "name": "wysh_group4"
    },
    {
        "url": "http://127.0.0.1:8009/groups/5/",
        "name": "wysh_group5"
    },
    {
        "url": "http://127.0.0.1:8009/groups/6/",
        "name": "Pm"
    }
]
```
在 MySQL 数据库中，django_restful存放的是数据库迁移后，Django系统的数据，如下图所示：

![MySQL.jpg](https://upload-images.jianshu.io/upload_images/12273007-9a1e15103c106c89.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

其中 api_user 和 api_group 存放的是上面接口中用户和用户组的信息，以下的接口操作也是针对用户和用户组进行操作，api_user表如下：

![user表.jpg](https://upload-images.jianshu.io/upload_images/12273007-3993b085cd848145.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


###  测试脚本介绍

- mysql_action.py：进行数据库的初始化操作，代码如下：

```
from pymysql import connect
import yaml
import logging


class DB():
    def __init__(self):
        logging.info('==================init data===============')
        logging.info('connect db...')
        self.conn = connect(host='127.0.0.1', user='root', password='123456', db='django_restful')

    def clear(self, table_name):
        logging.info('clear db...')
        clear_sql = 'truncate ' + table_name + ';'
        with self.conn.cursor() as cursor:
            cursor.execute('set foreign_key_checks=0;')
            cursor.execute(clear_sql)
        self.conn.commit()

    def insert(self, table_name, table_data):
        logging.info('inser data...')
        for key in table_data:
            table_data[key] = "'" + str(table_data[key]) + "'"

        key = ','.join(table_data.keys())
        value = ','.join(table_data.values())

        logging.info(key)
        logging.info(value)

        insert_sql = 'insert into ' + table_name + '(' + key + ')' + 'values' + '(' + value + ')'
        logging.info(insert_sql)

        with self.conn.cursor() as cursor:
            cursor.execute(insert_sql)
        self.conn.commit()

    def close(self):
        logging.info('close db')
        self.conn.close()
        logging.info('=============init finished!============')

    def init_data(self, datas):
        for table, data in datas.items():
            self.clear(table)
            for d in data:
                self.insert(table, d)
        self.close()


if __name__ == '__main__':
    db = DB()
    # db.clear('api_user')
    # db.clear('api_group')
    # user_data={'id':1,'username':'wysh','email':'wysh@qq.com'}
    # db.insert('api_user',user_data)
    # db.close()

    f = open('datas.yaml', 'r')
    datas = yaml.load(f)
    db.init_data(datas)
```

- test_django_restful.py：对不同类型的接口请求（post，put，get，delete）进行单元测试，代码如下：


```
import requests
import unittest
from  mysql_action import DB
import yaml
import logging

class UserTest(unittest.TestCase):
    def setUp(self):
        self.base_url='http://127.0.0.1:8009/users'
        self.auth=('wysh','123456')


    def test_001_get_user(self):
        logging.info('test_001_get_user')
        r=requests.get(self.base_url+'/1/',auth=self.auth)
        result=r.json()

        self.assertEqual(result['username'],'wysh1')
        self.assertEqual(result['email'],'wysh1@qq.com')

    def test_002_add_user(self):
        logging.info('test_002_add_user')
        form_data={'username':'wysh6','email':'wysh5@163.com','groups':'http://127.0.0.1:8000/groups/2/'}
        r=requests.post(self.base_url+'/',data=form_data,auth=self.auth)
        result=r.json()

        self.assertEqual(result['username'],'wysh6')
        self.assertEqual(result['email'],'wysh5@163.com')

    #
    def test_003_update_user(self):
        logging.info('test_003_update_user')
        form_data={'email':'wysh555@163.com'}
        r=requests.patch(self.base_url+'/1/',data=form_data,auth=self.auth)
        result=r.json()

        self.assertEqual(result['email'],'wysh555@163.com')

    def test_004_delete_user(self):
        logging.info('test_004_delete_user')
        r=requests.delete(self.base_url+'/4/',auth=self.auth)

        self.assertEqual(r.status_code,204)

    def test_005_no_auth(self):
        logging.info('test_005_no_auth')
        r=requests.get(self.base_url)
        result=r.json()

        self.assertEqual(result['detail'],'Authentication credentials were not provided.')


class GroupTest(unittest.TestCase):
    def setUp(self):
        self.base_url='http://127.0.0.1:8009/groups'
        self.auth=('wysh','123456')


    def test_001_group_wysh(self):
        logging.info('test_001_group')
        r=requests.get(self.base_url+'/1/',auth=self.auth)
        result=r.json()

        self.assertEqual(result['name'],'wysh_group1')

    def test_002_add_group(self):
        logging.info('test_002_add_group')
        form_data={'name':'Pm'}
        r=requests.post(self.base_url+'/',data=form_data,auth=self.auth)
        result=r.json()

        self.assertEqual(result['name'],'Pm')

    def test_003_update_group(self):
        logging.info('test_003_update_group')
        form_data={'name':'Boss'}
        r=requests.patch(self.base_url+'/2/',data=form_data,auth=self.auth)
        result=r.json()

        self.assertEqual(result['name'],'Boss')

    def test_004_delete_group(self):
        logging.info('test_004_delete_group')
        r=requests.delete(self.base_url+'/1/',auth=self.auth)
        self.assertEqual(r.status_code,204)

if __name__ == '__main__':
    db=DB()
    f=open('datas.yaml','r')
    datas=yaml.load(f)
    db.init_data(datas)
    unittest.main()
```

- data.yaml：以yaml格式存放接口初始数据，方便读取，代码如下：

```
import requests
import unittest
from  mysql_action import DB
import yaml
import logging

class UserTest(unittest.TestCase):
    def setUp(self):
        self.base_url='http://127.0.0.1:8009/users'
        self.auth=('wysh','123456')


    def test_001_get_user(self):
        logging.info('test_001_get_user')
        r=requests.get(self.base_url+'/1/',auth=self.auth)
        result=r.json()

        self.assertEqual(result['username'],'wysh1')
        self.assertEqual(result['email'],'wysh1@qq.com')

    def test_002_add_user(self):
        logging.info('test_002_add_user')
        form_data={'username':'wysh6','email':'wysh5@163.com','groups':'http://127.0.0.1:8000/groups/2/'}
        r=requests.post(self.base_url+'/',data=form_data,auth=self.auth)
        result=r.json()

        self.assertEqual(result['username'],'wysh6')
        self.assertEqual(result['email'],'wysh5@163.com')

    #
    def test_003_update_user(self):
        logging.info('test_003_update_user')
        form_data={'email':'wysh555@163.com'}
        r=requests.patch(self.base_url+'/1/',data=form_data,auth=self.auth)
        result=r.json()

        self.assertEqual(result['email'],'wysh555@163.com')

    def test_004_delete_user(self):
        logging.info('test_004_delete_user')
        r=requests.delete(self.base_url+'/4/',auth=self.auth)

        self.assertEqual(r.status_code,204)

    def test_005_no_auth(self):
        logging.info('test_005_no_auth')
        r=requests.get(self.base_url)
        result=r.json()

        self.assertEqual(result['detail'],'Authentication credentials were not provided.')


class GroupTest(unittest.TestCase):
    def setUp(self):
        self.base_url='http://127.0.0.1:8009/groups'
        self.auth=('wysh','123456')


    def test_001_group_wysh(self):
        logging.info('test_001_group')
        r=requests.get(self.base_url+'/1/',auth=self.auth)
        result=r.json()

        self.assertEqual(result['name'],'wysh_group1')

    def test_002_add_group(self):
        logging.info('test_002_add_group')
        form_data={'name':'Pm'}
        r=requests.post(self.base_url+'/',data=form_data,auth=self.auth)
        result=r.json()

        self.assertEqual(result['name'],'Pm')

    def test_003_update_group(self):
        logging.info('test_003_update_group')
        form_data={'name':'Boss'}
        r=requests.patch(self.base_url+'/2/',data=form_data,auth=self.auth)
        result=r.json()

        self.assertEqual(result['name'],'Boss')

    def test_004_delete_group(self):
        logging.info('test_004_delete_group')
        r=requests.delete(self.base_url+'/1/',auth=self.auth)
        self.assertEqual(r.status_code,204)

if __name__ == '__main__':
    db=DB()
    f=open('datas.yaml','r')
    datas=yaml.load(f)
    db.init_data(datas)
    unittest.main()
```
-  log.conf：日志配置文件，代码如下：

```
[loggers]
keys=root,infoLogger

[logger_root]
level=DEBUG
handlers=consoleHandler,fileHandler

[logger_infoLogger]
handlers=consoleHandler,fileHandler
qualname=infoLogger
propagate=0

[handlers]
keys=consoleHandler,fileHandler

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=form02
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=form01
args=('./logs/runlog.log', 'a')

[formatters]
keys=form01,form02

[formatter_form01]
format=%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s

[formatter_form02]
format=%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s

```
- run.py：程序的入口，代码如下：

```
import unittest
from BSTestRunner import BSTestRunner
import time,yaml
from mysql_action import DB
import logging.config

CON_LOG='log.conf'
logging.config.fileConfig(CON_LOG)
logging=logging.getLogger()


db=DB()
f=open('datas.yaml','r')
datas=yaml.load(f)
db.init_data(datas)

test_dir='.'
report_dir='./reports'

discover=unittest.defaultTestLoader.discover(test_dir,pattern='test_django_restful.py')

now=time.strftime('%Y-%m-%d %H_%M_%S')
report_name=report_dir+'/'+now+' test_report.html'

with open (report_name,'wb') as f:
    runner=BSTestRunner(stream=f,title='Vincent API Test Report',description='Vincent Django Restful API Test Report')
    logging.info('=========Start API Test=============')
    runner.run(discover)
    
```
### 程序执行

运行run.py，会调用数据初始化、单元测试、日志、测试报告生成模块，测试报告生成在reports目录下，打开测试包括，会显示各个单元测试用例执行结果，如下图：

![report.jpg](https://upload-images.jianshu.io/upload_images/12273007-890e43dbd5992c97.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

打开logs目录下的日志文件，会显示程序执行过程中的日志记录，如下图：

![日志.jpg](https://upload-images.jianshu.io/upload_images/12273007-b51651f7ded06ee2.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


###  Jenkins集成

打开Jenkins持续集成平台，我们可以自动定时执行自动化任务，通过邮件发送测试报告，这样会有效提高测试效率

创建名称为：wysh_interface_tes 的任务，在构建中选择执行Windows批处理命令，输入如下内容：
```
d:
cd D:\django_restful\api\interface_wysh
E:\Python\Python36-32\python3.exe run.py

```
如下图所示：

![windows批处理.jpg](https://upload-images.jianshu.io/upload_images/12273007-2f85c4660eb5a0d6.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

构建过程如下图所示：

![Jenkins.jpg](https://upload-images.jianshu.io/upload_images/12273007-b7daf4aea05d1fac.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

构建完成后，同样也会在 reports 目录下生成相应的测试报告。





