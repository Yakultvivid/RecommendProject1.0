import time
from model.Item_Collaboration_Filter import ItemCF
import json
import config


def run(train):
    # 基于邻域的协同过滤
    start = time.time()
    item_cf = ItemCF()
    item_cf.load_train(train)
    item_cf.calc_item_sim()

    recommend = {}
    for user in train.keys():
        rec = item_cf.recommend(user)
        recommend[user] = rec

    with open(config.DATA_PATH.format("recommend", "icf_recommend.json"), "w") as fw:
        json.dump(recommend, fw, ensure_ascii=False, indent=4)

    print('ICF - Cost time: %f' % (time.time() - start))
    return recommend
