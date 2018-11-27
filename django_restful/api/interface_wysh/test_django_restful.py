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
