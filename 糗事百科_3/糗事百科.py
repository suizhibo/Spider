# -*-coding:utf-8 -*-

import queue
import random
import threading
import time

import requests
from bs4 import BeautifulSoup

headers = {
    '''User-Agent''': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'''
}

proxy_pool = []

# 下载页面
def download_html(url):
    try:
        proxy = random.choice(proxy_pool)
        rep = requests.get(url, headers=headers, proxies=proxy)
        rep.raise_for_status()
        rep.encoding = rep.apparent_encoding
        return rep.content.decode()
    except Exception as e:
        print(e)
        return


# 解析列表页html页面
def parse_html(html, article_id_list):
    if html:
        soup = BeautifulSoup(html, 'lxml')
        articles = soup.find_all('div', class_='article')
        for article in articles:
            id = article.find('a', class_='contentHerf').get('href')
            article_id_list.put(id)


class ParseInfo(threading.Thread):
    def __init__(self, urlqu):
        threading.Thread.__init__(self)
        self.thread_num = self.getName()
        self.q = urlqu

    def run(self) -> None:
        self.parse_info_html()

    # 解析详情页
    def parse_info_html(self):
        while True:
            time.sleep(0.5)  # 线程休息0.5s
            article_id = self.q.get()
            # print(self.thread_num, article_id)
            if article_id is None:
                self.q.task_done()
                break
            url = 'https://www.qiushibaike.com%s' % article_id
            html = None
            try:
                proxy = random.choice(proxy_pool)  # 选择代理
                rep = requests.get(url, headers=headers, proxies=proxy)
                rep.raise_for_status()
                rep.encoding = rep.apparent_encoding
                html = rep.content.decode(errors='ignore')
            except Exception as e:
                print(e)
                pass
            if html:
                with open(self.thread_num + '.txt', 'a+', encoding='utf-8') as f:
                    soup = BeautifulSoup(html, 'lxml')
                    author = soup.find(
                        'span', attrs={'class': 'side-user-name'}).get_text().replace('\n', '')
                    div_tag = soup.find('div', class_='col1 new-style-col1')
                    title = div_tag.find(
                        'h1', class_='article-title').get_text().replace('\n', '')
                    stats_div_tag = div_tag.find('div', class_='stats')
                    time_ = stats_div_tag.find(
                        'span', class_='stats-time').get_text().replace('\n', '')
                    vote = stats_div_tag.find(
                        'span', class_='stats-vote').get_text().replace('\n', '')
                    content = div_tag.find(
                        'div', class_='content').get_text().replace(
                        '\n', '')
                    f.write(author + title + time_ + vote + content + '\n')
            self.q.task_done()


def load_proxy_pool():
    global proxy_pool
    with open('proxy.txt', 'rb') as f:
        for proxy in f.readlines():
            re = proxy.decode('utf-8').strip().split('_')
            proxy_pool.append({re[0]: re[0] + "://" + re[1] + ':' + re[2]})


if __name__ == '__main__':
    # 加载proxy_pool
    load_proxy_pool()

    article_id_list = queue.Queue(maxsize=1000)
    base_url = 'https://www.qiushibaike.com/text/page/%d/'
    depth = 10  # 爬取深度

    for i in range(1, depth):
        url = base_url % i
        html = download_html(url)
        # print(url)
        parse_html(html, article_id_list)
    # 设置线程退出信号
    article_id_list.put(None)
    article_id_list.put(None)
    article_id_list.put(None)
    article_id_list.put(None)
    threads = [
        ParseInfo(article_id_list),
        ParseInfo(article_id_list),
        ParseInfo(article_id_list),
        ParseInfo(article_id_list),
    ]
    for t in threads:
        t.start()
    article_id_list.join()
