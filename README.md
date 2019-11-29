# RecommendProject1.0
RecommendMaster-Match
data
    match_value
        match_value.csv 用户相似度(前20)
    model_data
        items_feature.csv item特征矩阵
        rating_matrix.csv user-item矩阵
    process_data
        item.csv item标签
        rating.csv user-item-rating数据
    recommend
        模型召回
            ucf_recommend.json
            icf_recommend.json
        关注召回
        推送召回
evaluate
    evaluate.py 模型评测
        recall
        precision
        coverage
        popularity
fit_transform 模型调用
    CB.PY
    ICF.PY
    LFM.PY
    UCF.PY
model 模型脚本
    Content_based_recommendation.py
    Item_Collaboration_Filter.py
    Latent_Factor_Model.py
    User_Collaboration_Filter.py
preprocessing
    data_process.py
    load_database.py
config.py 配置
manage.py 主调文件
project.txt 说明
recall_master.py 召回排序
test.py 调试脚本
