import json
import config
from operator import itemgetter


def recall_master(goods_labels, user_label_score, recall_name):
    recall = {}
    """
    召回排序
    关注推荐优先权重最高P0, M模型标签推荐P1, m模型推荐P2, 自定义推荐P3; 商品展示比例 1: 2: 2: 1
    """
    # 模型召回
    with open(config.DATA_PATH.format("recommend", "ucf_recommend.json"), "r") as fp:
        ucf = json.load(fp)
    with open(config.DATA_PATH.format("recommend", "icf_recommend.json"), "r") as fp:
        icf = json.load(fp)
    # 关注召回
    # with open(config.DATA_PATH.format("recommend", "relation_recommend.json"), "r") as fp:
    #     relation = json.load(fp)
    # 召回融合
    # users = set(list(ucf.keys()) + list(icf.keys()) + list(relation.keys()))
    # users = set(list(ucf.keys()) + list(icf.keys()))  # users = ucf.keys() = icf.keys()
    for user in ucf.keys():
        recall[user] = {}
        recall[user].update(icf[user])
        recall[user].update(ucf[user])
    print("{} users in recall".format(len(recall)))
    # 根据标签偏好排序
    for user in recall.keys():  # 当前用户
        for goods_id in recall[user].keys():  # 推荐给当前用户的商品
            goods_label = goods_labels[goods_labels["goods_id"] == goods_id]["labels"]  # 当前商品的标签
            label_rating = (ucf.get(user).get(goods_id, 0) + icf.get(user).get(goods_id, 0))*5  # 模型预测分数平均数的十倍
            for label in [label.split('|')[0] for label in goods_label]:  # 标签切分
                try:
                    rating = user_label_score[user][label]  # 在用户历史标签评分表中获取当前标签的分数
                    label_rating += rating  # 分数累加 即为当前用户对当前商品的评分
                except KeyError:
                    # 该用户可能有关注信息但没有行为数据 / 推荐的商品附带标签是用户未评分过的
                    # rating = (ucf.get(user).get(goods_id) + icf.get(user).get(goods_id)) / 2  # 模型预测分数平均数
                    pass

            recall[user][goods_id] = round(label_rating, 4)
            recall[user] = dict(sorted(recall[user].items(), key=itemgetter(1), reverse=True)[0: config.TOP_N])
        with open(recall_name, "w") as fw:
            json.dump(recall, fw)
    print("回合结束")
    # 投送召回

