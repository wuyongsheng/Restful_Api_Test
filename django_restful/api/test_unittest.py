import requests
import unittest

class UserTest(unittest.TestCase):
    def setUp(self):
        self.base_url='http://127.0.0.1:8009/users/'
        self.auth=('administrator','wysh1025362683')

    # def test_get_user(self):
    #     r=requests.get(self.base_url+'2',auth=self.auth)
    #     result=r.json()
    #
    #     self.assertEqual(result['username'],'wysh2')
    #     self.assertEqual(result['email'],'wysh2@qq.com')

    def test_add_user(self):
        form_data={'username':'wysh7','email':'wysh7@qq.com','groups':'http://127.0.0.1:8009/groups/1/'}
        r=requests.post(self.base_url,data=form_data,auth=self.auth)
        result=r.json()
        print(result)
        self.assertEqual(result['username'],'wysh7')

    # def test_delete_user(self):
    #     r=requests.delete(self.base_url+'3',auth=self.auth)
    #
    #     self.assertEqual(r.status_code,204)

    def  test_update_user(self):
        form_data={'email':'wysh4444@qq.com'}
        r=requests.patch(self.base_url+'4/',auth=self.auth,data=form_data)
        result=r.json()
        # print(r)

        self.assertEqual(result['email'],'wysh4444@qq.com')

    # def test_no_auth(self):
    #     r=requests.get(self.base_url)
    #     result=r.json()
    #
    #     self.assertEqual(result['detail'],'Authentication credentials were not provided.')



    if  __name__=='__main__':
        unittest.main()

