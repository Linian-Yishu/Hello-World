import requests
from lxml import etree


#获取几页
page = 1
url = 'https://www.qiushibaike.com/8hr/page/' + str(page)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}

try:
    response = requests.get(url, headers=headers)
    res = response.text

    html = etree.HTML(res)
    result = html.xpath('//div[contains(@id,"qiushi_tag")]')#contains 选择包含某些字符
    # print(result)
    for site in result:
        item = {}

        item['imgUrl'] = site.xpath('./div/a/img/@src')[0].encode('utf-8')
        item['username'] = site.xpath('./div/a/h2')[0].text.strip()
        item['content'] = site.xpath('.//div[@class="content"]/span')[0].text.strip()
        item['vote'] = site.xpath('//i')[0].text
        item['comments'] = site.xpath('//i')[1].text
        print(item)

except Exception as e:
    print(e)