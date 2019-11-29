import time
import redis
import json
import config
import manage

# 此处为要执行的任务
print(time.strftime('%Y-%m-%d %X', time.localtime()))
recall_name = config.DATA_PATH.format("recall_master", "AAA.json")
manage.manage(recall_name)

# 缓存
pool = redis.ConnectionPool(host='127.0.0.1', password="kokomachine", port=6379)
redis_base = redis.Redis(connection_pool=pool)
with open(recall_name, 'rb') as f:
    dic = json.load(f)
for user, goods_rating in dic.items():
    for goods, rating in goods_rating.items():
        redis_base.hset(name=user, key=goods, value=rating)
        if user == "82049":
            print(goods, rating)
with open(config.DATA_PATH.format("recall_master", "log.txt"), "a") as fw:
    fw.writelines("redis 更新时间：" + time.strftime('%Y-%m-%d %X', time.localtime()))

