---
id: redis-bloom-filter-dump-and-load
title: "RedisBloom 模块布隆过滤器的导出与导入"
description: "介绍 RedisBloom 模块中用于导出和导入布隆过滤器的命令 BF.SCANDUMP 和 BF.LOADCHUNK，并提供一个 Python 脚本示例，用于实现布隆过滤器的数据迁移。"
date: 2025.11.09 10:26
categories:
    - Redis
    - Python
tags: [Redis, Data Structures, Python]
keywords: Redis, RedisBloom, Bloom Filter, BF.SCANDUMP, BF.LOADCHUNK, Data Migration, Python
cover: /contents/covers/redis-bloom-filter-dump-and-load.png
---

RedisBloom 模块为 Redis 提供了 [Bloom Filter](https://alphahinex.github.io/2025/10/26/redis-bloom-filter/) 数据结构，除了基本的创建、添加、查询等操作外，还提供了用来导出单个过滤器的 [BF.SCANDUMP](https://redis.io/docs/latest/commands/bf.scandump/) 命令，和导入命令 [BF.LOADCHUNK](https://redis.io/docs/latest/commands/bf.loadchunk/)。

# 官方文档 Example

## Syntax

```cli
BF.SCANDUMP key iterator
```

iterator 参数初始值为 0，表示从头开始导出，命令返回两个元素的数组：
1. 下一个迭代器值，如果再次为 0 则表示导出完成
2. 导出的数据块 

```cli
BF.LOADCHUNK key iterator data
```

## Examples

```cli
redis> BF.RESERVE bf 0.1 10
OK
redis> BF.ADD bf item1
1) (integer) 1
redis> BF.SCANDUMP bf 0
1) (integer) 1
2) "\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x02\x00\x00\x00\b\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x9a\x99\x99\x99\x99\x99\xa9?J\xf7\xd4\x9e\xde\xf0\x18@\x05\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x00"
redis> BF.SCANDUMP bf 1
1) (integer) 9
2) "\x01\b\x00\x80\x00\x04 \x00"
redis> BF.SCANDUMP bf 9
1) (integer) 0
2) ""
redis> DEL bf
(integer) 1
redis> BF.LOADCHUNK bf 1 "\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x00\x02\x00\x00\x00\b\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x9a\x99\x99\x99\x99\x99\xa9?J\xf7\xd4\x9e\xde\xf0\x18@\x05\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x00"
OK
redis> BF.LOADCHUNK bf 9 "\x01\b\x00\x80\x00\x04 \x00"
OK
redis> BF.EXISTS bf item1
(integer) 1
```

```python
chunks = []
iter = 0
while True:
    iter, data = BF.SCANDUMP(key, iter)
    if iter == 0:
        break
    else:
        chunks.append([iter, data])

# Load it back
for chunk in chunks:
    iter, data = chunk
    BF.LOADCHUNK(key, iter, data)
```

# 可用于布隆过滤器数据迁移的 Python 脚本

## Conda Env

```bash
$ conda create -n redisbloom python=3.12
$ conda activate redisbloom
$ pip install redis[hiredis]
$ pip list
Package    Version
---------- -------
hiredis    3.3.0
pip        25.2
redis      7.0.1
setuptools 80.9.0
wheel      0.45.1
```

## 备份脚本

`redis_bloom_backup.py`：

```python
import redis
import pickle
import argparse

def backup(key):
    r = redis.Redis(host='localhost', port=6379)

    chunks = []
    iter = 0
    while True:
        iter, data = r.bf().scandump(key, iter)
        if iter == 0:
            break
        else:
            chunks.append([iter, data])
    
    with open(f"dump_{key}.pkl", 'wb') as file:
        pickle.dump(chunks, file)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCANDUMP bloom filter to a file.")
    parser.add_argument("key", type=str, help="Key of bloom filter")

    args = parser.parse_args()

    backup(args.key)
```

```bash
$ python redis_bloom_backup.py "test:restore"
$ $ ls -alh dump_test:restore.pkl
-rw-rw-r-- 1 root root 2.1G 11月  8 15:51 dump_test:restore.pkl
```

> 即使未向过滤器中插入数据，创建好指定容量的过滤器后，导出时，数据文件也是 BF.INFO 的 Size 大小。

## 恢复脚本

`redis_bloom_restore.py`：

```python
import redis
import pickle
import argparse

def restore(dump_file, key):
    r = redis.Redis(host='localhost', port=6379)
    
    with open(dump_file, 'rb') as file:
        chunks = pickle.load(file)
    
    for chunk in chunks:
        iter, data = chunk
        r.bf().loadchunk(key, iter, data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LOADCHUNK bloom filter from a file.")
    parser.add_argument("dump_file", type=str, help="Dump file of bloom filter")
    parser.add_argument("key", type=str, help="Key of bloom filter")

    args = parser.parse_args()

    restore(args.dump_file, args.key)
```

```bash
$ python redis_bloom_restore.py dump_test:restore.pkl tmpbf
$ redis-cli bf.info tmpbf
 1) Capacity
 2) (integer) 1000000000
 3) Size
 4) (integer) 2157872304
 5) Number of filters
 6) (integer) 1
 7) Number of items inserted
 8) (integer) 999973866
 9) Expansion rate
10) (integer) 2
```

> 导入时，不能提前创建过滤器，否则会报错，直接向不存在的 key 中导入即可。