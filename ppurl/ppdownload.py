#!/usr/local/bin/python
#coding:utf-8

import requests, threading, Image, json, re
from bs4 import BeautifulSoup
from ftplib import FTP
from pymongo import Connection

def show_image(path):
    image = Image.open(path)
    image.show()

def download(name, url):
    m = re.match(r'ftp://free:(.*)@www.ppurl.com(.*)', url)
    password = m.group(1)
    path = m.group(2)
    suffix = url.split('.')[-1]
    name = name + '.' + suffix

    print 'begin to download', name
    ftp = FTP('www.ppurl.com')
    ftp.login(user='free',passwd=password) 
    ftp.retrbinary('RETR %s' % path, open(name,'wb').write)  
    print 'download finished'


conn = Connection()
db_book = conn.dev.ppbook

host = 'http://www.ppurl.com'
url = 'http://www.ppurl.com/2013/04/two-scoops-of-django.html'
loginurl = host + '/login/'

data = {'loginname':'yingyu010','loginpass':'123456'}
print 'login...'
r = requests.post(loginurl,data=data,allow_redirects=False)
cookies = r.cookies
#print cookies

books = db_book.find().limit(10) #每个账号每天只能下载10本书
for book in books:
    print 'begin to get download link for', book['name']
    r = requests.get(book['url'],cookies=cookies)
    #print r.text
    soup = BeautifulSoup(r.text)

    skey_input = soup.find('input',{'name':'skey'})
    skey = skey_input.get('value')

    captcha = soup.find('img',{'alt':u'验证码'})
    #print captcha
    capurl = host + captcha.get('surl')

    r = requests.get(capurl,cookies=cookies)
    cap_cookies = r.cookies
    #print r.cookies
    #print r.status_code
    #print r.headers
    with open('cap.png', 'wb') as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)


    t = threading.Thread(target=show_image, args=('cap.png',))
    t.start()
    captcha = raw_input('validation code:')
    print captcha

    data = {}
    data['skey'] = skey
    data['captcha'] = captcha
    r = requests.post(host+'/captcha', data=data, cookies=cap_cookies)
    print r.text
    j = json.loads(r.text)
    print j['status']
    if j['status'] == '1':
        print j['data']
        download(book['name'], j['data'])
