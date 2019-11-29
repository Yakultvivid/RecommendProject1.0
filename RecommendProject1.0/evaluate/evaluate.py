import math


def get_recommend(user, recommend):
    rank = {}
    for item, rating in recommend[user]:
        rank[item] = rating
    return rank


def recall(train, test, recommend):
    """ 召回率 """
    hit = 0
    all = 0
    for user in train.keys():
        tu = test[user]
        rank = get_recommend(user, recommend)
        for item, rating in rank.items():
            if item in tu:
                hit += 1
        all += len(tu)
    res = hit / (all * 0.1)
    print("召回率: {}".format(res))
    return res


def precision(train, test, recommend):
    """ 准确率 """
    hit = 0
    all = 0
    for user in train.keys():
        tu = test[user]
        rank = get_recommend(user, recommend)
        n = len(rank)
        for item, rating in rank.items():
            if item in tu:
                hit += 1
        all += n
    res = hit / (all * 0.1)
    print("准确率: {}".format(res))
    return res


def coverage(train, test, recommend):
    """ 覆盖率 """
    recommend_items = set()
    all_items = set()
    for user in train.keys():
        for item in train[user].keys():
            all_items.add(item)
        rank = get_recommend(user, recommend)
        for item, rating in rank.items():
            recommend_items.add(item)
    res = len(recommend_items) / (len(all_items) * 1.0)
    print("覆盖率: {}".format(res))
    return res


def popularity(train, test, recommend):
    item_popularity = dict()  # {item: 评分用户总数, item2: ...}
    for user, items in train.items():
        for item in items.keys():
            if item not in item_popularity:
                item_popularity[item] = 0
            item_popularity[item] += 1
    ret = 0
    n = 0
    for user in train.keys():
        rank = get_recommend(user, recommend)
        for item, rating in rank.items():
            ret += math.log(1 + item_popularity[item])
            n += 1
    ret /= n * 1.0
    print("新颖度: {}".format(ret))
    return ret
