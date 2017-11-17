import requests
from bs4 import BeautifulSoup
import re
import os
import threading
import queue

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}
lock = threading.Lock()


def getlists(url):
    '''
    获取东方财富页面
    '''
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except BaseException:
        print('获取股票列表页失败')


def getstocklist(html, listqueue):
    '''解析页面'''
    try:
        pat = r'http://quote.eastmoney.com/s[hz]\d{6}\.html'
        s_list = re.findall(pat, html)
        for sto in s_list:
            # lists.append(sto.split('/')[-1])
            listqueue.put(sto.split('/')[-1])
    except BaseException:
        print('股票正则匹配出错')


def getinfo(q):
    '''获取股票详情信息'''

    while not q.empty():

        try:
            # lock.acquire()
            id = q.get()
            url = 'https://gupiao.baidu.com/stock/' + id
            stock = {}
            html = getlists(url)
            soup = BeautifulSoup(html, 'lxml')
            stockinfo = soup.find('div', class_='stock-bets')
            title = stockinfo.text.split()[0]
            stock.update({'股票链接': url})
            stock.update({'股票名称': title})

            keylist = stockinfo.find_all('dt')
            vallist = stockinfo.find_all('dd')
            # print(keylist, vallist)
            for i in range(len(keylist)):
                key = keylist[i].text
                val = vallist[i].text
                stock[key] = val
            print(stock)

            # 保存
            lock.acquire()  # 先要获取锁
            saveinfo(stock, q)
            lock.release()  # 释放锁
        except BaseException as e:
            print(e)
        # finally:
        #     lock.release()


def saveinfo(stock, q):
    '''保存本地'''
    path = "D:/baidu/gupiao/"
    if not os.path.exists(path):
        os.mkdir(path)

    try:
        print('正在保存{}股票信息,当前还剩{}条记录未保存'.format(stock['股票名称'], q.qsize()))
        for key, value in stock.items():
            with open(path + 'gupiao2.txt', 'a') as f:
                f.write(key + ':' + value + '\t')
                f.close()
        with open(path + 'gupiao2.txt', 'a') as file:
            file.write('\n')
            file.write('-----------------------------------------------')
            file.write('\n\n')
            file.close()
    except BaseException:
        print('未收录当前股票')


def main():
    '''
    主程序
    '''
    stoke_url = 'http://quote.eastmoney.com/stocklist.html'
    html = getlists(stoke_url)  # 获取股票列表页面
    listqueue = queue.Queue()
    getstocklist(html, listqueue)  # 股票列表
    # print(listqueue.qsize())
    ta = threading.Thread(target=getinfo, args=(listqueue, ))
    tb = threading.Thread(target=getinfo, args=(listqueue, ))
    tc = threading.Thread(target=getinfo, args=(listqueue,))
    td = threading.Thread(target=getinfo, args=(listqueue,))

    ta.start()
    tb.start()
    tc.start()
    td.start()


if __name__ == '__main__':
    main()
