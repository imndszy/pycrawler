# -*- coding:utf-8 -*- 
# author: szy
# time: 2017/11/8 14:03
# email: shizhenyu96@gmail.com
import re
import time
import Queue
import requests
import urllib
import threading
import logging
import signal
import chardet
from datetime import datetime
from urlparse import urlparse, urlunparse, urljoin
from posixpath import normpath


from db import create_engine, with_connection, insert, update
from config import *
from url_manager import BloomFilterRedis, CrawlerContextManager

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    filename="crawler.log", level=logging.INFO)


def before_crawl():
    create_engine(SETTINGS['MYSQL_USER'],
                  SETTINGS['MYSQL_PASSWORD'],
                  SETTINGS['MYSQL_DBNAME'],
                  SETTINGS['MYSQL_SERVER'], charset='utf8')
    update("""
                CREATE TABLE IF NOT EXISTS `{}`(
                    `id` INT (10) UNSIGNED NOT NULL AUTO_INCREMENT ,
                    `url` VARCHAR (1000) NOT NULL ,
                    `domain` VARCHAR (100) NOT NULL ,
                    `html` LONGTEXT NULL ,
                    `language` VARCHAR (8) NULL ,
                    `encode` VARCHAR (20) NULL ,
                    `http_code` INT (4) NOT NULL ,
                    `wrong_reason` VARCHAR (1000) NULL ,
                    `useful` TINYINT (1) NOT NULL ,
                    `AddTime` DATETIME NULL ,
                    `UpdateTime` DATETIME NULL ,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY (`url`)
                )ENGINE=InnoDB DEFAULT CHARSET=utf8
            """.format(TABLE_NAME))


def init_crawl_queue(crawler_txt_mgr):
    crawl_queue = Queue.Queue()
    if crawler_txt_mgr.urls_in_set():
        urls = crawler_txt_mgr.get_urls()
        crawler_txt_mgr.delete_older_urls()
    else:
        urls = SEED_URL_SET
    for i in urls:
        crawl_queue.put(i)
    return crawl_queue


def init_crawl_status(crawler_txt_mgr):
    return crawler_txt_mgr.get_crawler_status()


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


class NJUCrawler(threading.Thread):

    crawler_txt_mgr = CrawlerContextManager()
    crawl_queue = init_crawl_queue(crawler_txt_mgr)
    logging.info("URL队列初始化完成~")
    start_update = init_crawl_status(crawler_txt_mgr)
    logging.info("爬虫状态初始化完成~")
    bloom_filter = BloomFilterRedis(REDIS_KEY['URL_FILTER'])
    kill_now = False
    logging.info("开始爬取~")

    def __init__(self):
        threading.Thread.__init__(self)

    @classmethod
    def exit_crawler(cls, signum, frame):
        raise ServiceExit

    @with_connection
    def run(self):
        while True:
            if NJUCrawler.kill_now:
                logging.info("线程{}结束爬取".format(threading.currentThread().getName()))
                return
            if not NJUCrawler.crawl_queue.empty():
                new_url = NJUCrawler.crawl_queue.get(block=True)
                if NJUCrawler.start_update:
                    time.sleep(SLEEP_TIME)
                self.handle_url(new_url)
                NJUCrawler.crawl_queue.task_done()
            else:
                if not NJUCrawler.start_update:
                    logging.info("抓取队列已空， 已开启更新模式~")
                    NJUCrawler.start_update = True
                for seed_url in SEED_URL_SET:
                    NJUCrawler.crawl_queue.put(seed_url)

    def handle_url(self, new_url):
        if new_url is None:
            return
        if NJUCrawler.exist(new_url):
            if NJUCrawler.start_update:
                new_urls = self.update_url(new_url)
            else:
                new_urls = set()
        else:
            new_urls = self.add_url(new_url)
        if not new_urls:
            return
        urls = set()
        if not NJUCrawler.start_update:
            for i in new_urls:
                if not NJUCrawler.exist(i):
                    urls.add(i)
        else:
            urls = new_url
        for url in urls:
            NJUCrawler.crawl_queue.put(url, block=True)

    def add_url(self, url):
        NJUCrawler.bloom_filter.insert(url)
        param = DB_PARAM.copy()
        param['url'] = url
        param['UpdateTime'] = datetime.now()
        param['AddTime'] = datetime.now()
        param['domain'] = get_domain(url)
        try:
            result = requests.get(url, allow_redirects=False, timeout=TIME_OUT)
            param['http_code'] = result.status_code
            if result.status_code != 200:
                return self.handle_unusual(url, result, param)
            else:
                if not verify_response(result):
                    param['wrong_reason'] = "该链接指向的不是html页面，是文件"
                    insert(TABLE_NAME, **param)
                    return set()
                param['html'] = result.text
                param['encode'] = result.encoding
                if result.encoding == "ISO-8859-1":
                    param['encode'] = chardet.detect(result.content)['encoding']
                param['useful'] = 1
                insert(TABLE_NAME, **param)
                return parse_html(url=url, html=result.text)
        except Exception as e:
            param['http_code'] = 1
            param['wrong_reason'] = str(e.args)
            insert(TABLE_NAME, **param)


    @classmethod
    def exist(cls, url):
        return cls.bloom_filter.contain(url)


    def update_url(self, url):
        """
        如果有redirect_url参数，表示更新原内容为新页面
        :param url:
        :param redirect_url:
        :return:
        """
        param = DB_PARAM.copy()
        param['url'] = url
        param['UpdateTime'] = datetime.now()
        param['domain'] = get_domain(url)
        try:
            result = requests.get(url, allow_redirects=False, timeout=TIME_OUT)
            param['http_code'] = result.status_code
            if result.status_code != 200:
                return self.handle_unusual(url, result, param)
            else:
                if not verify_response(result):
                    return set()
                param['html'] = result.text
                param['encode'] = result.encoding
                if result.encoding == "ISO-8859-1":
                    param['encode'] = chardet.detect(result.content)['encoding']
                param['useful'] = 1
                count = update("UPDATE {} SET UpdateTime = ?, http_code = ?, html = ?, "
                       "encode = ?, useful = ? WHERE url = ?".format(TABLE_NAME),
                       param['UpdateTime'], result.status_code, result.text,
                       result.encoding, 1, url)
                if count == 0:
                    param["AddTime"] = param["UpdateTime"]
                    insert(TABLE_NAME, **param)
                return parse_html(url=url, html=result.text)
        except Exception as e:
            param['http_code'] = 1
            param['wrong_reason'] = str(e.args)
            count = update("UPDATE {} SET UpdateTime = ?, http_code = ?, wrong_reason= ? WHERE url = ?".format(TABLE_NAME),
                           param['UpdateTime'], 1, param['wrong_reason'], url)
            if count == 0:
                param["AddTime"] = param["UpdateTime"]
                insert(TABLE_NAME, **param)
            return set()

    def handle_unusual(self, url ,response, param):
        NJUCrawler.bloom_filter.insert(url)
        if response.status_code in (307, 302, 301):
            redirect_url = response.headers.get("Location", "")
            if redirect_url:
                redirect_url = fill_link(url, redirect_url)
                if not verify_domain(get_domain(redirect_url)):
                    return set()
                if NJUCrawler.exist(redirect_url):
                    return self.update_url(redirect_url)
                else:
                    return self.add_url(redirect_url)
            else:
                param["wrong_reason"] = "重定向链接但未返回Location"
        elif response.status_code in (400, 404):
            param["wrong_reason"] = "无效的url，找不到该页面"
        elif response.status_code in (500, 503):
            param["wrong_reason"] = "服务器出错"
        elif response.status_code in (403):
            param["wrong_reason"] = "无访问权限"
        else:
            param["wrong_reason"] = "未知http状态码"
        insert(TABLE_NAME, **param)
        return set()


def parse_html(url, html):
    match = re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')", html)
    match = pre_filter(match)
    new_urls = set()
    for link in match:
        link = fill_link(url, link)
        if not verify_link(url, link):
            continue
        else:
            new_urls.add(link)
    return new_urls


def fill_link(parent_url, link):
    link = link.strip()
    if link.startswith("http"):
        return link
    else:
        return link_join(parent_url, link)


def get_domain(url):
    query = urllib.splitquery(url)
    types = urllib.splittype(query[0])
    domain = urllib.splithost(types[1])
    return domain[0]


def verify_link(parent_url, link):
    """
    return False if link is invalid
    :param link: link
    :return: bool
    """
    query = urllib.splitquery(link)
    types = urllib.splittype(query[0])
    domain = urllib.splithost(types[1])
    if not verify_domain(domain[0]):
        return False
    if not domain[1] or "." not in domain[1]:
        return True
    paths = domain[1].split("/")
    suffix = ""
    for path in paths:
        if "." in path:
            suffix = path.split(".")[-1]
    if not suffix:
        return True
    suffix = suffix.lower()
    if suffix in COMMON_FILE_SUFFIX or suffix in OUTER_DOMAIN:
        return False
    # elif suffix in VALID_SUFFIX:
    #     return True
    # else:
    #     logging.info("suffix : {}, url : {}, parent_url : {}".format(suffix, link, parent_url))
    #     return False
    else:
        return True


def verify_domain(domain):
    for black_domain in BLACK_DOMAIN:
        if domain in black_domain:
            return False
    for allow_domain in ALLOWED_DOMAIN:
        if allow_domain in domain:
            return True
    return False


def link_join(parent_url, link):
    url = urljoin(parent_url, link)
    arr = urlparse(url)
    path = normpath(arr[2])
    return urlunparse((arr.scheme, arr.netloc, path, arr.params, arr.query, arr.fragment))


def verify_response(response):
    if not response:
        return False
    if 'text/html' in response.headers.get("Content-Type"):
        return True
    else:
        return False


def pre_filter(urls):
    """
    href 内容的过滤：去除 # ，javascript:;等等
    :param urls:
    :return:
    """
    valid_href = set()
    for i in urls:
        if "#" in i:
            i = i.split("#")[0]
            if not i:
                continue
        flag = False
        for pattern in INVALID_HREF_PATTERN:
            if pattern in i:
                flag = True
                break
        if flag:
            continue
        else:
            valid_href.add(i)
    return valid_href


def run_spider(thread_num = 8):
    before_crawl()
    threads = []
    for i in range(thread_num):
        thread = NJUCrawler()
        threads.append(thread)
        thread.start()
    return threads

def main(spider_num):
    threads = run_spider(spider_num)
    try:
        signal.signal(signal.SIGINT, NJUCrawler.exit_crawler)
        signal.signal(signal.SIGTERM, NJUCrawler.exit_crawler)
        while True:
            time.sleep(0.5)
    except ServiceExit:
        NJUCrawler.kill_now = True
        for thread in threads:
            thread.join()
        urls = set()
        while not NJUCrawler.crawl_queue.empty():
            urls.add(NJUCrawler.crawl_queue.get())
        ccm = CrawlerContextManager()
        ccm.save_urls_to_redis(urls)
        logging.info("当前URL队列已经持久化到redis")
        ccm.save_status(NJUCrawler.start_update)
        logging.info("当前爬取状态已经保存到redis")
        exit(0)


if __name__ == "__main__":
    main(2)
