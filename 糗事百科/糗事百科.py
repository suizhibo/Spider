# -*-coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup

headers = {
    '''User-Agent''': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'''
}

# 下载html
def download_html(url):
    try:
        rep = requests.get(url, headers=headers)
        rep.raise_for_status()
        rep.encoding = rep.apparent_encoding
        return rep.content.decode()
    except IOError:
        return

# 解析html页面
def parse_html(html,result_list):
    soup = BeautifulSoup(html,'lxml')
    articles = soup.find_all('div', class_='article')
    for article in articles:
        result = []
        #作者名称
        author = article.find('div',class_='author').find('h2').get_text().replace(' ','').replace('\n','')
        #好笑数
        stats_vote = article.find('span',class_='stats-vote').find('i',class_='number').get_text().replace(' ','').replace('\n','')
        #内容简介
        content = article.find('div',class_='content').get_text().replace(' ','').replace('\n','')
        result.extend([author,stats_vote,content])
        result_list.append(result)




if __name__ == '__main__':
    # 存放用户名，日期，内容
    result_list = []
    base_url = 'https://www.qiushibaike.com/text/page/%d/'
    depth = 10  # 爬取深度
    for i in range(1, depth):
        url = base_url % i
        html = download_html(url)
        parse_html(html,result_list)
    # 保存结果
    with open('result.txt', 'a+', encoding='utf-8') as f:
        for txt in result_list:
            f.write(','.join(txt)+'\n')
