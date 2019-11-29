import pandas as pd
import config
from fit_transform import ICF, UCF, FM, CB
from preprocessing import load_database, data_process
from evaluate import evaluate
import rec_master


def manage(recall_name):
    # print("start...")
    # 预处理文件
    load_database.Preprocess().process_user_data()  # 用户画像
    user_item_rating = load_database.Preprocess().process_ratings_data()  # user-item-rating
    goods_labels = load_database.Preprocess().process_items_data()  # item属性
    # load_database.Preprocess().process_follow_data()  # 关注推荐
    user_label_score = load_database.Preprocess().user_label_score(user_item_rating)  # user标签偏好分数
    # load_database.Preprocess().user_view_log()  # 浏览历史

    # 整理模型数据
    data_process.data_process()

    # 数据切分
    file_name = config.DATA_PATH.format("process_data", "sh_ratings.csv")
    # train, test = data_process.train_test_split(fileName)
    train = data_process.train_split(file_name)

    # 模型调用
    # 基于邻域的协同过滤
    UCF.run(train)
    ICF.run(train)

    # 基于隐语义模型的推荐

    # 基于内容的推荐
    # train = pd.read_csv(config.DATA_PATH.format("model_data", 'rating_matrix.csv'), index_col=0)
    # CB.run(train)

    # 测评
    # evaluate.recall_master(train, test, recommend)
    # evaluate.precision(train, test, recommend)
    # evaluate.coverage(train, test, recommend)
    # evaluate.popularity(train, test, recommend)

    # 召回排序
    rec_master.recall_master(goods_labels, user_label_score, recall_name)

