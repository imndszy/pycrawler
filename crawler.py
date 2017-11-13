# -*- coding:utf-8 -*- 
# author: szy
# time: 2017/11/8 14:03
# email: shizhenyu96@gmail.com
import re
import time
import requests
import urllib
import threading
import logging
from datetime import datetime
from urlparse import urlparse, urlunparse, urljoin
from posixpath import normpath


from db import create_engine, with_connection, insert, update
from config import *
from bloom_filter import BloomFilterRedis

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


class NJUCrawler(threading.Thread):

    lock = threading.Lock()
    crawl_queue = SEED_URL_SET
    bloom_filter = BloomFilterRedis(key="crawl")
    start_update = False
    logging.info("开始爬取~")

    def __init__(self):
        threading.Thread.__init__(self)

    @with_connection
    def run(self):
        while True:
            with NJUCrawler.lock:
                try:
                    new_url = NJUCrawler.crawl_queue.pop()
                except KeyError:
                    if not NJUCrawler.start_update:
                        logging.info("抓取队列已空， 已开启更新模式~")
                        NJUCrawler.start_update = True
                    NJUCrawler.crawl_queue = NJUCrawler.crawl_queue | SEED_URL_SET
                    new_url = None
            if NJUCrawler.start_update:
                time.sleep(SLEEP_TIME)
            if new_url is None:
                continue
            if NJUCrawler.exist(new_url):
                new_urls = self.update_url(new_url)
            else:
                new_urls = self.handle_url(new_url)
            if not new_urls:
                continue
            urls = set()
            for i in new_urls:
                if not NJUCrawler.exist(i):
                    urls.add(i)
            with NJUCrawler.lock:
                NJUCrawler.crawl_queue = NJUCrawler.crawl_queue | urls

    def handle_url(self, url):
        NJUCrawler.bloom_filter.insert(url)
        param = DB_PARAM.copy()
        param['url'] = url
        param['UpdateTime'] = datetime.now()
        param['AddTime'] = datetime.now()
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
                param['useful'] = 1
                count = update("UPDATE {} SET UpdateTime = ?, http_code = ?, html = ?, "
                       "encode = ?, useful = ? WHERE url = ?".format(TABLE_NAME),
                       param['UpdateTime'], result.status_code, result.text,
                       result.encoding, 1, url)
                if count == 0:
                    insert(TABLE_NAME, **param)
                return parse_html(url=url, html=result.text)
        except Exception as e:
            param['http_code'] = 1
            param['wrong_reason'] = str(e.args)
            count = update("UPDATE {} SET UpdateTime = ?, http_code = ?, wrong_reason= ? WHERE url = ?".format(TABLE_NAME),
                           param['UpdateTime'], 1, param['wrong_reason'], url)
            if count == 0:
                insert(TABLE_NAME, **param)
            return set()

    def handle_unusual(self, url ,response, param):
        if response.status_code in (307, 302, 301):
            redirect_url = response.headers.get("Location", "")
            if redirect_url:
                redirect_url = fill_link(url, redirect_url)
                if NJUCrawler.exist(redirect_url):
                    return self.update_url(redirect_url)
                else:
                    return self.handle_url(redirect_url)
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


def verify_link(parent_url, link):
    """
    return False if link is invalid
    :param link: link
    :return: bool
    """
    query = urllib.splitquery(link)
    types = urllib.splittype(query[0])
    domain = urllib.splithost(types[1])
    valid_domain = False
    for allow_domain in ALLOWED_DOMAIN:
        if allow_domain in domain[0]:
            valid_domain = True
            break
    if not valid_domain:
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
    elif suffix in VALID_SUFFIX:
        return True
    else:
        logging.info("suffix : {}, url : {}, parent_url : {}".format(suffix, link, parent_url))
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

    for t in threads:
        t.join()


if __name__ == "__main__":
    run_spider(16)
