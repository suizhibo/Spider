import threading
import time
from queue import Queue

import requests
from bs4 import BeautifulSoup

sem = threading.Semaphore(3)  # 设置爬虫的数
proxy_queue = Queue(10000)


class GetProxy(threading.Thread):
    def __init__(self, url, headers):
        threading.Thread.__init__(self)
        self.daemon = True
        self.url = url
        self.headers = headers
        self.thread_name = self.getName()
        self.proxy_list = []

    def run(self) -> None:
        self.get_proxy()

    def get_proxy(self):
        try:
            rep = requests.get(self.url, headers=self.headers)
            rep.raise_for_status()
            html = rep.content.decode()
            self.parse_html(html)
        except Exception as e:
            print(e)
            print(self.thread_name)

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'lxml')
        table_tag = soup.find('table', class_='table table-bordered table-striped')
        tbody_tag = table_tag.find('tbody')
        trs = tbody_tag.find_all('tr')
        for tr in trs:
            ip = tr.find('td', attrs={'data-title': 'IP'}).get_text()
            port = tr.find('td', attrs={'data-title': 'PORT'}).get_text()
            kind = tr.find('td', attrs={'data-title': '类型'}).get_text()
            proxy_queue.put([kind, ip, port])
        sem.release()


if __name__ == '__main__':

    headers = {
        'user-agent': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'''
    }
    base_url = 'https://www.kuaidaili.com/free/inha/{}'
    page_num = 5
    counts = (page_num - 1) * 15
    for i in range(1, page_num):
        url = base_url.format(i)
        sem.acquire()
        time.sleep(1)
        GetProxy(url, headers=headers).run()

    with open('proxy.txt', 'a+', encoding='utf-8') as f:
        while counts:
            proxy = proxy_queue.get()
            f.write('_'.join(proxy) + '\n')
            proxy_queue.task_done()
            counts -= 1
    proxy_queue.join()
