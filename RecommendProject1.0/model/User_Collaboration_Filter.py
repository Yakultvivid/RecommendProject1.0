import math
from operator import itemgetter
import config


class UserCF:
    def __init__(self):
        self.n_sim_user = config.N_SIM_USER
        self.n_rec_item = config.TOP_N
        self.user_sim_matrix = {}  # 用户相似度矩阵
        self.item_count = 0

        self.train = {}  # {user_id: {item_id: rating, item_id: rating}, user_id: {...}}

    def load_train(self, train):
        self.train = train

    def calc_user_sim(self):
        # 倒排表 item_user = {item1: (user1, user2), item2: (user3, ...), ...}
        item_user = {}
        for user, items in self.train.items():
            for item in items.keys():  # 当前用户评分过的item
                item_user.setdefault(item, set())
                item_user[item].add(user)
        print("倒排表中商品数量: {}".format(len(item_user)))  # 所有被操作过的item数量

        for item, users in item_user.items():  # item当前商品 users评分过当前商品的用户们
            for u in users:
                for v in users:
                    self.user_sim_matrix.setdefault(u, {})
                    self.user_sim_matrix[u].setdefault(v, 0)
                    self.user_sim_matrix[u][v] += 1  # {user1:{user2:2次, user3:1次}, user2:{user1:1次...}, ...}
        print("Similarity matrix ...")
        for u, relates_users in self.user_sim_matrix.items():
            for v, count in relates_users.items():
                self.user_sim_matrix[u][v] = round(count / math.sqrt(len(self.train[u]) * len(self.train[v])), 4)
                # 相似度 = 评分交集 与 各自评分商品数的乘积开方 的 比值
        return self.user_sim_matrix

    def recommend(self, user):
        k = self.n_sim_user
        n = self.n_rec_item
        rank = {}
        watched_item = self.train[user]

        for v, wuv in sorted(self.user_sim_matrix[user].items(), key=itemgetter(1), reverse=True)[0: k]:
            # v 当前用户, wuv 相似度
            for item in self.train[v]:  # 当前用户的评分物品集
                if item in watched_item:  # 判断目标用户是否评分过
                    continue
                else:
                    rank.setdefault(item, 0)
                    rank[item] += wuv
                rank[item] = round(rank[item], 4)

        return dict(sorted(rank.items(), key=itemgetter(1), reverse=True)[0: n])
