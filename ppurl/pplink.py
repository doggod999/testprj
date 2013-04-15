#!/usr/local/bin/python
#coding:utf-8

import requests, threading, Image, json, re
from bs4 import BeautifulSoup
from ftplib import FTP
from pymongo import Connection
from datetime import datetime,date,time

def show_image(path):
    image = Image.open(path)
    image.show()

conn = Connection()
db_book = conn.dev.ppbook

num = 10

host = 'http://www.ppurl.com'
url = 'http://www.ppurl.com/2013/04/two-scoops-of-django.html'
loginurl = host + '/login/'

data = {'loginname':'yingyu010','loginpass':'123456'}
print 'login...'
r = requests.post(loginurl,data=data,allow_redirects=False)
cookies = r.cookies
#print cookies

books = db_book.find({'$or':[{'downurl':{'$exists':False}}, {'urldate':{'$lt':datetime.combine(date.today(),time(0,0,0))}, '$status':0}]}).limit(num) #书籍链接当天有效，不要太贪多
for book in books:
    print u'获取下载链接：', book['name']
    r = requests.get(book['url'],cookies=cookies)
    #print r.text
    soup = BeautifulSoup(r.text)

    skey_input = soup.find('input',{'name':'skey'})
    skey = skey_input.get('value')

    captcha = soup.find('img',{'alt':u'验证码'})
    #print captcha
    capurl = host + captcha.get('surl')

    while True:
        r = requests.get(capurl,cookies=cookies)
        cap_cookies = r.cookies
        #print r.cookies
        #print r.status_code
        #print r.headers
        with open('cap.png', 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        
        #显示验证码
        threading.Thread(target=show_image, args=('cap.png',)).start()
        captcha = raw_input('input validation code: ')

        data = {}
        data['skey'] = skey
        data['captcha'] = captcha
        r = requests.post(host+'/captcha', data=data, cookies=cap_cookies)
        #print r.text
        j = json.loads(r.text)
        print j['status'],j['msg']
        if j['status'] == '1':
            print j['data']
            book['downurl'] = j['data']
            book['status'] = 0
            book['urldate'] = datetime.now()
            db_book.save(book)
            break

