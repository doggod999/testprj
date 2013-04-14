#!/usr/local/bin/python
#coding: utf-8

import requests
from pymongo import Connection
from bs4 import BeautifulSoup

def check_item_exists(db,sid):
    '''Return true means exists'''
    f = db.find_one({'url':sid})
    if f == None:
        #print 'Not Exists'
        return False
    else:
        #print 'Exists'
        return True



conn = Connection()
db_cate = conn.dev.ppcate
db_book = conn.dev.ppbook

#抓取首页上的分类
data = {'loginname':'yingyu010','loginpass':'123456'}
r = requests.post('http://www.ppurl.com/login/',data=data)
#print r.status_code
if r.status_code == 200:
    soup = BeautifulSoup(r.text)
    tagdiv = soup.find('div',{'id':'tag-cloud'})
    tags = tagdiv.findAll('a')
    print len(tags)
    for tag in tags:
        cate = {}
        cate['name'] = tag.contents[0]
        cate['url'] = tag.get('href')
        print cate
        db_cate.save(cate)

#抓取分类结束，开始抓取书籍链接
categories = db_cate.find()

count = 0
for cate in categories:
    print cate
    page = 1
    while True:
        url = cate['url']+'/page/'+str(page)
        print url
        r = requests.get(url)
        #print r.text
        soup = BeautifulSoup(r.text)
        covers = soup.findAll('div',{'class':'cover'})
        
        if len(covers) == 0: #达到最后一页
            break
        else:
            for cover in covers:
                book = {}
                link = cover.find('a')
                book['url'] = link.get('href')
                book['name'] = link.get('title')
                book['cate'] = cate['name']
                if not check_item_exists(db_book, book):
                    print book
                    db_book.save(book)
                    count += 1

            page += 1


print 'Total books:',count
