# -*-coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup

headers = {
    '''User-Agent''': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'''
}


# 下载页面
def download_html(url):
    try:
        rep = requests.get(url, headers=headers)
        rep.raise_for_status()
        rep.encoding = rep.apparent_encoding
        return rep.content.decode()
    except IOError:
        return


# 解析列表页html页面
def parse_html(html, article_id_list):
    soup = BeautifulSoup(html, 'lxml')
    articles = soup.find_all('div', class_='article')
    for article in articles:
        id = article.find('a', class_='contentHerf').get('href')
        article_id_list.append(id)


# 解析详情页
def parse_info_html(article_id):
    url = 'https://www.qiushibaike.com%s' % article_id
    html = None
    try:
        rep = requests.get(url, headers=headers)
        rep.raise_for_status()
        rep.encoding = rep.apparent_encoding
        html = rep.content.decode()
    except IOError:
        pass
    if html:
        soup = BeautifulSoup(html, 'lxml')
        author = soup.find('span', attrs={'class': 'side-user-name'}).get_text().replace('\n', '')
        div_tag = soup.find('div', class_='col1 new-style-col1')
        title = div_tag.find('h1', class_='article-title').get_text().replace('\n', '')
        stats_div_tag = div_tag.find('div', class_='stats')
        time = stats_div_tag.find('span', class_='stats-time').get_text().replace('\n', '')
        vote = stats_div_tag.find('span', class_='stats-vote').get_text().replace('\n', '')
        content = div_tag.find('div', class_='content').get_text().replace('\n', '')
        return author, title, time, vote, content


if __name__ == '__main__':
    # 存放用户名，日期，内容
    result_list = []
    article_id_list = []
    base_url = 'https://www.qiushibaike.com/text/page/%d/'
    depth = 2  # 爬取深度
    for i in range(1, depth):
        url = base_url % i
        html = download_html(url)
        parse_html(html, article_id_list)
    # 保存在文件中
    with open('result.txt', 'a+', encoding='utf-8') as f:
        for id in article_id_list:
            result = parse_info_html(id)
            f.write(','.join(result) + '\n')
