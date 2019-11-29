import pandas as pd
import numpy as np
import random
import config


def data_process():
    # user * item评分矩阵
    rating_data = pd.read_csv(config.DATA_PATH.format("process_data", "sh_ratings.csv"))
    # print("Loading data...")
    user_id = rating_data['user_id'].unique()
    item_id = rating_data['goods_id'].unique()
    rating_matrix = np.zeros([len(user_id), len(item_id)])
    rating_matrix = pd.DataFrame(rating_matrix, index=user_id, columns=item_id)
    # print("Converting data...")
    count = 0
    user_num = len(user_id)
    for uid in user_id:
        user_rating = rating_data[rating_data['user_id'] == uid].drop(['user_id'], axis=1)
        user_rated_num = len(user_rating)

        for row in range(0, user_rated_num):
            item_id = user_rating['goods_id'].iloc[row]
            rating_matrix.loc[uid, item_id] = user_rating['rating'].iloc[row]

        count += 1
        if count % 100 == 0:
            completed_percentage = round(float(count) / user_num * 100)
            # print("Completed %s" % completed_percentage + "%")

    rating_matrix.to_csv(config.DATA_PATH.format("model_data", 'rating_matrix.csv'))

    # 处理标签数据
    # print("Loading data...")
    items_data = pd.read_csv(config.DATA_PATH.format("process_data", 'sh_item.csv'))
    items_num = len(items_data)

    # 创建item的分类特征
    # print("Creating the feature of labels")
    # 得到该商品数据集中分类的类别列表
    labels_list = set()
    for label in items_data['labels']:
        labels_list = labels_list | set(label.split('|'))

    # 给每个类别创建一个维度加到原商品数据集中
    labels_list = list(labels_list)
    for label in labels_list:
        items_data[label] = np.zeros([items_num, 1])

    count = 0
    for j in range(0, items_num):
        item_labels = items_data.loc[j, 'labels'].split('|')
        for k in item_labels:
            items_data.loc[j, k] = 1

        count += 1
        if count % 1000 == 0:
            completed_percentage = round(float(count) / items_num * 100)
            # print("Completed %s" % completed_percentage + "%")

    items_data.set_index('goods_id', inplace=True)
    items_data.drop(['goods_name', 'labels'], axis=1, inplace=True)
    items_data.to_csv(config.DATA_PATH.format("model_data", 'items_feature.csv'))


def load_file(filename):
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:  # 去掉文件第一行的title
                continue
            yield line.strip('\r\n')
    # print('Load %s success!' % filename)


def train_test_split(fileName, pivot=0.75):
    train = {}
    test = {}
    train_len = 0
    test_len = 0
    for line in load_file(fileName):
        user, goods, rating, timestamp = line.split(',')
        if random.random() < pivot:
            train.setdefault(user, {})
            train[user][goods] = rating
            train_len += 1
        else:
            test.setdefault(user, {})
            test[user][goods] = rating
            test_len += 1
    # print('Split trainingSet and testSet success!')
    # print('TrainSet = %s' % train_len)
    # print('TestSet = %s' % test_len)
    return train, test


def train_split(fileName):
    train = {}
    for line in load_file(fileName):
        user, goods, rating = line.split(',')
        train.setdefault(user, {})
        train[user][goods] = rating
    # print('Split trainingSet and testSet success!')
    # print('TrainSet = %s' % len(train))
    return train
