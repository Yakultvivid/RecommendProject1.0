import time
from model.User_Collaboration_Filter import UserCF
import config
import json
from operator import itemgetter


def run(train):
    # 基于邻域的协同过滤
    start = time.time()
    user_cf = UserCF()
    user_cf.load_train(train)
    user_sim_matrix = user_cf.calc_user_sim()

    match_res = {}

    # 遍历用户列表
    recommend = {}
    for user in train.keys():
        # 保存 match 值
        match_value = sorted(user_sim_matrix[user].items(), key=itemgetter(1), reverse=True)[0: config.MATCH_TOP_USER]
        match_res[user] = match_value

        rec = user_cf.recommend(user)
        recommend[user] = rec

    with open(config.DATA_PATH.format("match_value", "match_value.json"), "w") as fw:
        json.dump(match_res, fw, ensure_ascii=False, indent=4)

    with open(config.DATA_PATH.format("recommend", "ucf_recommend.json"), "w") as fw:
        json.dump(recommend, fw, ensure_ascii=False, indent=4)

    print('UCF - Cost time: %f' % (time.time() - start))

    return recommend
