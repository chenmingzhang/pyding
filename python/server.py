#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#!/usr/bin/env python3
# this code reads out everything in the system 
#-*- coding:utf-8 -*-
import hashlib
import threading
import json
from flask import Flask, request
import pymysql
from DBUtils.PooledDB import PooledDB
import pdb
import subprocess
import requests
from time import sleep,gmtime, strftime,localtime
from collections import OrderedDict

pool = PooledDB(pymysql, 5, host='localhost', user='root', passwd='', db='webhook', port=3306, charset='utf8')

app = Flask(__name__)

with open('title_parse.json') as f:
        tit = json.load(f, object_pairs_hook=OrderedDict)

with open('/home/yyh/pyding/credential/sales_list.json', 'r') as f:
        sales_list = json.load(f)

save_to_file=True

file_name= '../data/pizo.csv'
if save_to_file: fid= open(file_name,'a',0)

@app.route('/', methods=['GET', 'POST'])
def parse_request():
    if save_to_file: fid.write(strftime("%Y-%m-%d %H:%M:%S", localtime())+'\n'  )
    data = request.data.decode('utf-8')  # data is empty
    data_js = json.loads(request.data.decode('utf-8'))
    c=''
    column=u'：'
    next_line=u'\n'
    c+=tit['header']+next_line
    #if save_to_file: fid.write(data)  # not working
    if save_to_file: fid.write(str(data_js).encode('utf-8')+'\n')

    for tt1 in tit['title']:
        print tt1
        if (tt1 in data_js['data']) and tit['display'][tt1]=="True":
            if tit['type'][tt1]==u'string':
                c+=tit['title'][tt1]+column+data_js['data'][tt1]+tit['suffix'][tt1]+next_line
            if tit['type'][tt1]==u'number':
                print tt1 +'is number'
                try:
                    if data_js['data'][tt1]==None:
                        print tt1 +'is none'
                        data_js['data'][tt1]=0
                except Exception, e:
                    print 'can not pass data_jsdatatt1'
                    data_js['data'][tt1]=0
                    pass
                c+=tit['title'][tt1]+column+str(data_js['data'][tt1])+tit['suffix'][tt1]+next_line
            if tit['type'][tt1]==u'json':
                if tt1==u'_widget_1521767708321' :
                    c+=tit['title'][tt1] +column+ data_js['data'][tt1]['name']+tit['suffix'][tt1] + next_line 
    c+=tit['footer']

    sw_exclusion=False
    for subset in tit['exclusion']:
       if all(item in data_js['data'].items() for item in tit['exclusion'][subset].items()):
           sw_exclusion=True
           break
       

    payload_simple = '{"msgtype": "text", "text": { "content":"'+  c.encode('utf-8')+'" }}'
    print payload_simple
    #if save_to_file: fid.write(payload_simple+next_line)
    if save_to_file: fid.write(payload_simple+'\n')
    headers = {'content-type': 'application/json;charset=utf-8', 'Accept-Charset': 'UTF-8'}
    

    if sw_exclusion==False:
        for push_addr in sales_list["pushgroup"]:
            r= requests.post(sales_list["pushgroup"][push_addr], data=payload_simple, headers=headers)
            sleep(0.2)

    return 'success'



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3101)
