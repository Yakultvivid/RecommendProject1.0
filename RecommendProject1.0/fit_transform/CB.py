import time
import pandas as pd
from model import Content_based_recommendation
import config


def run(train):
    # 使用基于内容的推荐算法来估计评分
    items_feature = pd.read_csv(config.DATA_PATH.format("process_data", 'items_feature.csv'), index_col=0)
    start = time.time()
    count = 0
    total = float(train.shape[0])
    for idx, user in train.iterrows():
        unrated_index = user[user == 0].index.values
        rates_lst = []
        for item in unrated_index:
            rate_h = Content_based_recommendation.CB_recommend_estimate(user, items_feature, int(item))
            rates_lst.append(rate_h)
        train.loc[idx, unrated_index] = rates_lst
        count += 1
        if count % 100 == 0:
            percentage = round((count / total) * 100)
            print('Completed %d' % percentage + '%')
    train.to_csv(config.DATA_PATH.format("recommend", 'pre_ratings_CB.csv'))
    print('Content_based_recommendation - Cost time: %f' % (time.time() - start))
