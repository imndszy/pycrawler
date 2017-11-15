#
#**************************************************************************
#*                                                                        *
#*          General Purpose Hash Function Algorithms Library              *
#*                                                                        *
#* Author: Arash Partow - 2002                                            *
#* URL: http://www.partow.net                                             *
#* URL: http://www.partow.net/programming/hashfunctions/index.html        *
#*                                                                        *
#* Copyright notice:                                                      *
#* Free use of the General Purpose Hash Function Algorithms Library is    *
#* permitted under the guidelines and in accordance with the MIT License. *
#* http://www.opensource.org/licenses/MIT                                 *
#*                                                                        *
#**************************************************************************
#
import time

def RSHash(key):
    a    = 378551
    b    =  63689
    hash =      0
    for i in range(len(key)):
        hash = hash * a + ord(key[i])
        a = a * b
        a &= ((1 << 32) - 1)
        hash &= ((1 << 32) - 1)
    return hash


def JSHash(key):
    hash = 1315423911
    for i in range(len(key)):
      hash ^= ((hash << 5) + ord(key[i]) + (hash >> 2))
    return hash


def PJWHash(key):
   BitsInUnsignedInt = 4 * 8
   ThreeQuarters     = long((BitsInUnsignedInt  * 3) / 4)
   OneEighth         = long(BitsInUnsignedInt / 8)
   HighBits          = (0xFFFFFFFF) << (BitsInUnsignedInt - OneEighth)
   hash              = 0
   test              = 0

   for i in range(len(key)):
     hash = (hash << OneEighth) + ord(key[i])
     test = hash & HighBits
     if test != 0:
       hash = (( hash ^ (test >> ThreeQuarters)) & (~HighBits));
   return (hash & 0x7FFFFFFF)


def ELFHash(key):
    hash = 0
    x    = 0
    for i in range(len(key)):
      hash = (hash << 4) + ord(key[i])
      x = hash & 0xF0000000
      if x != 0:
        hash ^= (x >> 24)
      hash &= ~x
    return hash


def BKDRHash(key):
    seed = 131 # 31 131 1313 13131 131313 etc..
    hash = 0
    for i in range(len(key)):
      hash = (hash * seed) + ord(key[i])
    return hash


def SDBMHash(key):
    hash = 0
    for i in range(len(key)):
      hash = ord(key[i]) + (hash << 6) + (hash << 16) - hash
    return hash


def DJBHash(key):
    hash = 5381
    for i in range(len(key)):
       hash = ((hash << 5) + hash) + ord(key[i])
    return hash


def DEKHash(key):
    hash = len(key)
    for i in range(len(key)):
      hash = ((hash << 5) ^ (hash >> 27)) ^ ord(key[i])
    return hash


def BPHash(key):
    hash = 0
    for i in range(len(key)):
       hash = hash << 7 ^ ord(key[i])
    return hash


def FNVHash(key):
    fnv_prime = 0x811C9DC5
    hash = 0
    for i in range(len(key)):
      hash *= fnv_prime
      hash ^= ord(key[i])
    return hash


def APHash(key):
    hash = 0xAAAAAAAA
    for i in range(len(key)):
      if ((i & 1) == 0):
        hash ^= ((hash <<  7) ^ ord(key[i]) * (hash >> 3))
      else:
        hash ^= (~((hash << 11) + ord(key[i]) ^ (hash >> 5)))
    return hash

if __name__ == "__main__":
    url = u'http://iip.nju.edu.cn/index.phpntoquery=amp%253Breturnto%3D%25E7%2589%25B9%25E6%25AE%258A%253A%25E7%2594%25A8%25E6%2588%25B7%25E7%2599%25BB%25E5%25BD%2595%26amp%253Breturntoquery%3Damp%25253Breturnto%253D%2525E7%252589%2525B9%2525E6%2525AE%25258A%25253A%2525E7%252594%2525A8%2525E6%252588%2525B7%2525E7%252599%2525BB%2525E5%2525BD%252595%2526amp%25253Breturntoquery%253Damp%2525253Bamp%2525253Breturnto%25253D%252525E7%25252589%252525B9%252525E6%252525AE%2525258A%2525253A%252525E7%25252594%252525A8%252525E6%25252588%252525B7%252525E7%25252599%252525BB%252525E5%252525BD%25252595%252526amp%2525253Bamp%2525253Breturntoquery%25253Damp%252525253Breturnto%2525253D%25252525E7%2525252589%25252525B9%25252525E6%25252525AE%252525258A%252525253A%25252525E7%2525252594%25252525A8%25252525E6%2525252588%25252525B7%25252525E8%25252525B4%25252525A1%25252525E7%252525258C%25252525AE%252525252FLhy'

    hash_list = [RSHash, JSHash, PJWHash, ELFHash, BKDRHash,
                 SDBMHash, DJBHash, DEKHash, BPHash, FNVHash, APHash]
    for hash_func in hash_list:
        start = time.time()
        value = hash_func(url)
        end = time.time() - start
        print(hash_func.func_name, end, len(str(value)))
