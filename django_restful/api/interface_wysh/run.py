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