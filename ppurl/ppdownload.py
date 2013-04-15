#!/usr/local/bin/python
#coding:utf-8

import requests, threading, json, re
from ftplib import FTP
from pymongo import Connection
from datetime import datetime,date,time


conn = Connection()
db_book = conn.dev.ppbook

#localpath = '~/Downloads/temp/'
localpath = ''

books = db_book.find({'downurl':{'$exists':True},'status':0,'urldate':{'$gt':datetime.combine(date.today(),time(0,0,0))}})
for book in books:
    print book
    url = book['downurl']
    m = re.match(r'ftp://free:(.*)@www.ppurl.com(.*)', url)
    password = m.group(1)
    path = m.group(2)
    suffix = url.split('.')[-1]
    name = localpath + '[' + book['cate'] + ']' + book['name'] + '.' + suffix

    print 'begin to download', name   #皮皮书屋带宽有限，单线程就ok
    ftp = FTP('www.ppurl.com')
    ftp.login(user='free',passwd=password) 
    ftp.retrbinary('RETR %s' % path, open(name,'wb').write)  #TODO 增加检查文件是否完整
    print 'download finished'

