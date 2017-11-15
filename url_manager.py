# -*- coding:utf-8 -*- 
# author: szy
# time: 2017/11/8 15:57
# email: shizhenyu96@gmail.com
import redis
from config import SETTINGS, REDIS_KEY
import GeneralHashFunctions


class BloomFilterRedis(object):

    hash_list = ["RSHash", "JSHash", "PJWHash", "ELFHash", "BKDRHash",
                 "SDBMHash", "DJBHash", "DEKHash"]

    def __init__(self, key, host=SETTINGS['REDIS_SERVER'], port=SETTINGS['REDIS_PORT'], hash_list=hash_list):
        # redis-bitmap的key
        self.key = key
        # redis连接信息
        self.pool = redis.ConnectionPool(host=host, port=port, db=SETTINGS['REDIS_DB'])
        self.handle = redis.StrictRedis(connection_pool=self.pool, charset='utf-8')
        self.handle.setbit(self.key, 1, 0)
        # 哈希函数列表
        self.hash_list = hash_list

    @classmethod
    def random_generator(cls, hash_value):
        '''
        将hash函数得出的函数值映射到[0, 2^32-1]区间内
        '''
        return hash_value % (1 << 28)

    def insert(self, item):
        '''
        更新bitmap
        '''
        for hash_func_str in self.hash_list:
            # 获得到hash函数对象
            hash_func = getattr(GeneralHashFunctions, hash_func_str)
            # 计算hash值
            hash_value = hash_func(item)
            # 将hash值映射到[0, 2^32]区间
            real_value = BloomFilterRedis.random_generator(hash_value)
            # bitmap中对应位置为1
            if self.handle.getbit(self.key, real_value) == 0:
                self.handle.setbit(self.key, real_value, 1)

    def contain(self, item):
        '''
        检查是否存在
        :return: bool
        '''
        for hash_func_str in self.hash_list:
            # 获得到hash函数对象
            hash_func = getattr(GeneralHashFunctions, hash_func_str)
            # 计算hash值
            hash_value = hash_func(item)
            # 将hash值映射到[0, 2^32]区间
            real_value = BloomFilterRedis.random_generator(hash_value)
            # bitmap中对应位是0，说明此条目为新的条目
            if self.handle.getbit(self.key, real_value) == 0:
                return False
            # 当所有hash值在bitmap中对应位都是1，说明此条目重复，返回True
        return True


class CrawlerContextManager(object):

    def __init__(self):
        self.handle = redis.StrictRedis(host=SETTINGS['REDIS_SERVER'],
                                        port=SETTINGS['REDIS_PORT'],
                                        db=SETTINGS['REDIS_DB'])

    def urls_in_set(self):
        """
        check if there are urls in redis's set which initiated in last crawler's execution
        :return:yes->True, no->False
        """
        count = self.handle.scard(REDIS_KEY['URL_PERSISTENCE'])
        if count == 0:
            return False
        else:
            return True

    def get_urls(self):
        """get urls saved in set"""
        if not self.urls_in_set():
            return set()
        return self.handle.smembers(REDIS_KEY['URL_PERSISTENCE'])

    def get_crawler_status(self):
        status = self.handle.get(REDIS_KEY['SPIDER_STATUS'])
        if status is None:
            return 0
        elif status == "1":
            return False
        else:
            return True

    def save_urls_to_redis(self, urls):
        for i in urls:
            self.handle.sadd(REDIS_KEY['URL_PERSISTENCE'], i)

    def delete_older_urls(self):
        self.handle.delete(REDIS_KEY['URL_PERSISTENCE'])

    def save_status(self, start_update):
        if start_update:
            self.handle.set(REDIS_KEY['SPIDER_STATUS'], 2)
        else:
            self.handle.set(REDIS_KEY['SPIDER_STATUS'], 1)
