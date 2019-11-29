import time
from model import Matrix_Factorization
import json
import config


def run(train, test):
    start = time.time()

    # 使用矩阵分解算法来估计评分
    MF_estimate = Matrix_Factorization.MatrixFactorization(K=10, epoch=5)
    MF_estimate.fit(train)
    R_hat = MF_estimate.start()
    non_index = test.values.nonzero()
    pred_MF = R_hat[non_index[0], non_index[1]]
    actual = test.values[non_index[0], non_index[1]]

    # [P, Q] = Matrix_Factorization.CF_recommend_estimate(train, 1, [10, 17], 50)

    with open(config.DATA_PATH.format("recommend", "lfm_recommend.json"), "w") as fw:
        json.dump(rank, fw, ensure_ascii=False, indent=4)

    print('ICF - Cost time: %f' % (time.time() - start))
    return rank
