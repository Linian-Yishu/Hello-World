import requests
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
import gevent
from gevent import monkey
import time
import random

def get_header():
    '''获取随机headers'''
    my_headers = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"

    ]
    randdom_header=random.choice(my_headers)
    headers = {
        'Host':'www.80s.tw',
        'User-Agent':randdom_header
    }
    return headers


def get_html(url):
    '''获取每页电影列表'''

    try:
        head = get_header()
        html = requests.get(url, headers=head, timeout=30)
        print(head)
        html.encoding = 'utf-8'
        html.raise_for_status()
        return html.text
    except BaseException as e:
        print('获取html列表失败，错误信息为', e)


def get_url(html):
    '''获取每页html文本电影连接'''
    try:
        soup = BeautifulSoup(html, "lxml")
        urlslist = soup.find('ul', class_='me1 clearfix')
        patten = re.compile('/movie/\d+')
        urls = re.findall(patten, str(urlslist))
        for url in urls:
            url = 'http://www.80s.tw' + url
            yield url
    except BaseException as e:
        print('获取url失败，错误信息为', e)


def get_info(url):
    '''获取每个电影详情内需要的数据'''
    try:
        date = {}
        html = get_html(url)
        soup = BeautifulSoup(html,"lxml")
        title = soup.find('h1', class_='font14w').text
        infos = soup.find('ul', class_='dllist1')
        patten = re.compile('href="(.*?)".+?src="(.*?)"', re.S)
        clist = re.findall(patten, str(infos))
        date['电影名称'] = title
        date['电影详情链接'] = url
        for a in set(clist):
            date['迅雷链接'] = a[0]
            date['磁力链接'] = a[1]
        return date
    except BaseException as e:
        print('获取下载连接出错，错误信息为：', e)


def main(pages):
    '''程序入口'''
    try:
        for page in pages:
            first_url = 'http://www.80s.tw/movie/list/-----p{}'.format(str(page))
            print('正在处理：{}'.format(first_url))
            html = get_html(first_url)
            # time.sleep(2)
            # print(html)
            for url in set(get_url(html)):
                print('正在保存链接：{}的数据'.format(url))
                date = get_info(url)
                movies.insert(date)
    except BaseException as e:
        print('主程序运行出错，错误信息为：', e)


if __name__ == '__main__':
    '''主程序'''
    # 数据库连接
    conn = MongoClient('127.0.0.1', 27017)
    db = conn.movies
    movies = db.movies
    urllist = list(range(411))
    # 多线程处理
    monkey.patch_all()
    jobs = []
    for x in range(41):
        job = None
        if x == 0:
            job = gevent.spawn(main, urllist[1:(x + 1) * 10])
        elif 0 < x < 40:
            job = gevent.spawn(main, urllist[x * 10 + 1:(x + 1) * 10])
        else:
            job = gevent.spawn(main, urllist[x * 10 + 1:411])
        jobs.append(job)
    gevent.joinall(jobs)
    # print(jobs)
    print('--------全部保存成功---------')
