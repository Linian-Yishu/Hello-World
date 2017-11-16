import requests
from urllib.parse import urlencode
import os
import re
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}


def GetFistPage(kw, pn):
    '''获取列表页'''
    data = {
        'kw': kw,
        'ie': 'utf_8',
        'pn': pn
    }
    url = 'http://tieba.baidu.com/f?' + urlencode(data)
    print(url)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except RequestException:
        print("出现异常")
        return None


def parser_firstPage(html, pagelists):
    '''解析页面 获得单个帖子的名字，url'''
    re_href = re.compile('<a href="(/p/\d+?)".+?title="(.+?)"', re.S)
    re_titles = re.findall(re_href, html)
    print(re_titles)
    for i in range(len(re_titles)):
        pagelists.append({
            'title': re_titles[i][1],
            'url': re_titles[i][0]
        })
    return pagelists


def GetPersonPage(pagelist):
    '''获取帖子详情页面'''
    url = 'http://tieba.baidu.com' + pagelist['url']
    print(url, pagelist['title'])
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.text
    except RequestException:
        return None


def PersonPage(html):
    '''获得发帖的 名字 和内容'''
    concentlist = []
    soup = BeautifulSoup(html, 'lxml')
    page_infos = soup.find("div", {"id": "j_p_postlist"})
    for page_info in page_infos.children:
        if page_info.find(class_='d_name'):
            concentlist.append(
                {
                    'name': page_info.find(class_='d_name').text.strip(),
                    'content': page_info.find('cc').text.strip()
                }
            )
        else:
            continue
    return concentlist


def SaveComputer(pagelist, info):
    '''保存到本地'''
    path = "D:\\baidu\\"
    root = pagelist['title'] + '.txt'
    paths = path + root
    if not os.path.exists(path):
        os.mkdir(path)
    if not os.path.isdir(paths):
        try:
            with open(paths, 'w', encoding='utf-8') as f:
                f.write(
                    '帖子标题：' + pagelist['title'] + '\t' +
                    '帖子链接：' + 'http://tiebai.baidu.com' + pagelist['url'] + '\n\n\n' +
                    '=============================================================='+ '\n'
                )
                f.close()
            with open(paths, 'a', encoding='utf-8') as f:
                for i in range(len(info)):
                    f.write(
                        '\n' + info[i]['name'] + ":"+ '\n' + info[i]['content']+ '\n'
                        '----------------------------------------------------------\n'
                    )
        except OSError:
            print("可能有特殊字符，写入失败")


def main():
    '''主函数'''
    pagelists = []
    page_kw = input("请输入你要爬取的贴吧名称")
    page_pn = input("请输入你要爬取的最大页数")
    page_pn = (int(page_pn) - 1) * 50
    for page_MaxNum in range(0, page_pn + 1, 50):
        html = GetFistPage(page_kw, page_MaxNum)  # 获取页面
        parser_firstPage(html, pagelists)

    for pagelist in pagelists:
        html = GetPersonPage(pagelist)
        info = PersonPage(html)
        print(99, info)
        SaveComputer(pagelist, info)


if __name__ == '__main__':
    main()
