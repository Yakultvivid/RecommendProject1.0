import math
from operator import itemgetter
import config


class ItemCF:
    def __init__(self):
        self.n_sim_user = config.N_SIM_USER
        self.n_rec_item = config.TOP_N

        self.train = {}  # {user_id: {item_id: rating, item_id: rating}, user_id: {...}}

        self.item_sim_matrix = {}  # 用户相似度矩阵
        self.item_popular = {}
        self.item_count = 0

    def load_train(self, train):
        self.train = train

    def calc_item_sim(self):
        for user, items in self.train.items():
            for item in items:
                if item not in self.item_popular:
                    self.item_popular[item] = 0
                self.item_popular[item] += 1  # {m1: 当前商品被评分过的用户数量, m2: ...}

        self.item_count = len(self.item_popular)
        print("商品数量:{}".format(self.item_count))

        for user, items in self.train.items():
            for m1 in items:
                for m2 in items:
                    self.item_sim_matrix.setdefault(m1, {})
                    self.item_sim_matrix[m1].setdefault(m2, 0)
                    self.item_sim_matrix[m1][m2] += 1  # {m1:{m2:同现次数, m3...}, m2:{...}}
        print("Build co-rated users matrix success!")

        # 根据用户行为构建的商品相似度表
        for m1, related_items in self.item_sim_matrix.items():
            for m2, count in related_items.items():
                if self.item_popular[m1] == 0 or self.item_popular[m2] == 0:
                    self.item_sim_matrix[m1][m2] = 0
                self.item_sim_matrix[m1][m2] = count / math.sqrt(self.item_popular[m1] * self.item_popular[m2])
                # 相似度 = 目标商品和当前商品的同现次数 / 被几个用户评分的乘积的比值
        print('Calculate art similarity matrix success!')

    def recommend(self, user):
        k = self.n_sim_user
        n = self.n_rec_item
        rank = {}
        watched_items = self.train[user]

        for item, rating in watched_items.items():
            for related_item, w in sorted(self.item_sim_matrix[item].items(), key=itemgetter(1), reverse=True)[:k]:
                # w: item 与 related_item 的相似度
                if related_item in watched_items:
                    continue
                rank.setdefault(related_item, 0)
                rank[related_item] += w * float(rating)  # item与推荐商品的相似度 * 用户对当前item的评分

        return dict(sorted(rank.items(), key=itemgetter(1), reverse=True)[:n])
