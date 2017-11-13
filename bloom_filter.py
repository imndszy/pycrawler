# -*- coding:utf-8 -*- 
# author: szy
# time: 2017/11/8 15:57
# email: shizhenyu96@gmail.com
import redis
import GeneralHashFunctions


class BloomFilterRedis(object):

    hash_list = ["RSHash", "JSHash", "PJWHash", "ELFHash", "BKDRHash",
                 "SDBMHash", "DJBHash", "DEKHash"]

    def __init__(self, key, host='127.0.0.1', port=6379, hash_list=hash_list):
        # redis-bitmap的key
        self.key = key
        # redis连接信息
        self.pool = redis.ConnectionPool(host=host, port=port, db=1)
        self.handle = redis.StrictRedis(connection_pool=self.pool, charset='utf-8')
        self.handle.setbit(self.key, 1, 0)
        # 哈希函数列表
        self.hash_list = hash_list

    @classmethod
    def random_generator(cls, hash_value):
        '''
        将hash函数得出的函数值映射到[0, 2^32-1]区间内
        '''
        return hash_value % (1 << 24)

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
        flag = True
        for hash_func_str in self.hash_list:
            # 获得到hash函数对象
            hash_func = getattr(GeneralHashFunctions, hash_func_str)
            # 计算hash值
            hash_value = hash_func(item)
            # 将hash值映射到[0, 2^32]区间
            real_value = BloomFilterRedis.random_generator(hash_value)
            # bitmap中对应位是0，说明此条目为新的条目
            if self.handle.getbit(self.key, real_value) == 0:
                flag = False
            # 当所有hash值在bitmap中对应位都是1，说明此条目重复，返回True
        return flag