import threading
import requests
from urllib import request
from lxml import etree
import os
import re
from queue import Queue
import random

class Producer(threading.Thread):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
    }
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Producer,self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue
    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()
            self.parse_page(url)
    # 解析起始网页获得详情页的url
    def parse_page(self,url):
        response = requests.get(url,headers=self.headers)
        text = response.text
        html = etree.HTML(text)
        lis = html.xpath("//div[@class='mainleft']//li")
        for li in lis:
            title = li.xpath(".//h2/a/@title")
            link = li.xpath(".//a/@href")[0]
            print("详情页的地址：%s" % link)
            self.parse_pic(link)


    # 解析详情页
    def parse_pic(self,link):
        response = requests.get(link, headers=self.headers)
        text = response.text
        html = etree.HTML(text)
        title = html.xpath("//div[@class='mainleft']//h1/text()")[0]
        print(title)
        # 创建文件夹路径
        path = os.path.join(os.path.dirname(os.path.dirname('__file__')), '表情包')
        if not os.path.exists(path):
            os.mkdir(path)
        title_path = os.path.join(path, title)
        if not os.path.exists(title_path):
            os.mkdir(title_path)
        ps = html.xpath("//div[@id='post_content']/p")
        for p in ps:
            pic_url = p.xpath(".//img/@src")[0]
            print("图片的地址：%s"% pic_url)

            pic_name = pic_url.split('.')[-1]
            gfe = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nene']
            name = str(random.choice(gfe))
            title = name + '.' + pic_name
            self.img_queue.put((pic_url,title,title_path))


class Consumer(threading.Thread):
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Consumer,self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty() and self.img_queue.empty():
                break
            pic_url,title,title_path = self.img_queue.get()
            request.urlretrieve(pic_url, title_path + '/' + title)



def main():
    page_queue = Queue(16)
    img_queue = Queue(100)
    for x in range(1,16):
        url = 'http://www.bbsnet.com/%d' % x
        page_queue.put(url)

    for x in range(2):
        t = Producer(page_queue,img_queue)
        #print("线程：%s"% threading.current_thread())
        t.start()
    for x in range(2):
        t = Consumer(page_queue, img_queue)
        #print("线程：%s" % threading.current_thread())
        t.start()
    print(threading.enumerate())
if __name__ == '__main__':
    main()