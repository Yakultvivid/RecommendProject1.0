import pandas as pd
from sqlalchemy import create_engine
import json
import config
import warnings
warnings.filterwarnings("ignore")


class Preprocess:
    """
    process_user_data() 用户画像
    process_ratings_data() user-item-rating
    process_items_data() item标签
    process_follow_data() 关注推荐
    user_label_score()  # user标签偏好分数
    """
    test = {}

    def __init__(self):
        self.engine = create_engine('mysql+pymysql://{}:{}@{}:3306/{}'.format(
                config.USER, config.PASSWORD, config.HOST, config.DATABASE))

    def process_user_data(self):
        """
        用户个人信息表
        基础信息
            1.性别
            2.年龄
            3.生日
            4.星座
            5.地区
        偏好信息
            6.品类偏好    "男装/亲子..."   [品类1, 品类2, 品类3] 共计14 可选1-3
            7.基础偏好    "有房族/宝妈"  共计6 可选 1-6
            8.人生阶段    "学生党/上班族" 共计5 可选1
        购买属性
            9.类目偏好    "男士衬衫/厨房用品..." {类目: 次数, ...} 共计79
            10.价格偏好    "0-100/101-200"  {区间: 次数, ...} 共计4
        行为属性
            11.活跃阶段    "早间时刻/午间时刻" {时段: 次数, ...} 共计5
            12.浏览
            13.评论
            14.想买
            15.适合
            16.交易频率
        17.消费属性    "能省就省/理性消费" 共计4
        18.购买力     "5000以下/1w-2w" {标签: 次数, ...} 共计4
        19.商品喜好    "居家达人/女神必备" {标签: 次数, ...} 共计*
        """
        # print("用户画像 加载中...")

    def process_ratings_data(self):
        """
        用户评分信息 (sh_detail_log详情  sh_share_log分享  sh_user_want_buy想买 sh_order下单)
        rating = 购买次数 * 1.5 + 浏览次数 * 0.3 + 想买（is_deleted == 0） * 0.5 + 分享 * 0.8
        """
        # print("rating data 加载中...")
        # 查询语句
        sql_detail = "SELECT user_id, goods_id, COUNT(id) as  detail_count FROM sh_detail_log GROUP BY goods_id,user_id"
        sql_share = "SELECT user_id, goods_id, COUNT(id) as share_count FROM sh_share_log GROUP BY goods_id"
        sql_want = "SELECT user_id, wb_goods_id as goods_id, COUNT(id) as want_count FROM sh_user_want_buy " \
                   "WHERE is_deleted=0 GROUP BY user_id, wb_goods_id"
        sql_order = "SELECT user_id, wb_goods_id as goods_id, COUNT(id) as order_count FROM sh_order " \
                    "WHERE status >= 1 AND order_type = 2 GROUP BY goods_id,user_id"
        # read_sql_query数据库连接
        df_detail = pd.read_sql_query(sql_detail, self.engine)
        df_share = pd.read_sql_query(sql_share, self.engine)
        df_want = pd.read_sql_query(sql_want, self.engine)
        df_order = pd.read_sql_query(sql_order, self.engine)

        df_detail_share = df_detail.merge(df_share, on=["user_id", "goods_id"], how="outer")
        df_detail_share_want = df_detail_share.merge(df_want, on=["user_id", "goods_id"], how="outer")
        df = df_detail_share_want.merge(df_order, on=["user_id", "goods_id"], how="outer").fillna(0)
        df["user_id"] = df["user_id"].map(str)
        df["goods_id"] = df["goods_id"].map(str)
        df["rating"] = \
            df["detail_count"] * 0.3 + df["share_count"] * 0.8 + df["want_count"] * 0.5 + df["order_count"] * 1.5
        df["rating"] = round(df["rating"], 2)
        user_item_rating = df[["user_id", "goods_id", "rating"]]
        user_item_rating.to_csv(config.DATA_PATH.format("process_data", "sh_ratings.csv"), index=None)
        return user_item_rating

    def process_items_data(self):
        """
        商品信息 sh_wb_goods_info
            发布者id  pub_user_id
            商品id    id
            商品标题   goods_name
            一级分类   first_cat
            二级分类   second_cat
            商品价格   price
            快递费用   express_price
            商家描述   describe
            细节标签   labels
            is_deleted
        """
        # print("goods labels 加载中...")
        # sql = "SELECT id as goods_id, pub_user_id, goods_name, first_cat, second_cat, price, express_price, labels " \
        #       "FROM sh_wb_goods_info WHERE is_deleted=0"
        sql = "SELECT id as goods_id, pub_user_id, goods_name, labels FROM sh_wb_goods_info"
        goods_labels = pd.read_sql_query(sql, self.engine)
        goods_labels.goods_id = goods_labels["goods_id"].map(str)
        goods_labels.to_csv(config.DATA_PATH.format("process_data", "sh_item.csv"), index=None)
        return goods_labels

    def process_follow_data(self):
        """
        用户关注信息
        """
        # print("user-relation 加载中...")
        sql1 = "SELECT user_id, follow_user_id FROM sh_user_relation WHERE is_delete=0"
        df1 = pd.read_sql_query(sql1, self.engine)
        sql2 = "SELECT id as goods_id, pub_user_id as follow_user_id FROM sh_wb_goods_info WHERE is_deleted=0"
        df2 = pd.read_sql_query(sql2, self.engine)
        sh_user_relation = {}
        for _, row in df1.iterrows():
            user_id, follow_user = row["user_id"], row["follow_user_id"]
            user_id = str(user_id).split(".")[0]
            sh_user_relation.setdefault(user_id, {})
            try:
                for goods_id in df2[df2["follow_user_id"] == follow_user]["goods_id"]:
                    sh_user_relation[user_id].setdefault(str(goods_id), 0)
            except KeyError:
                continue
        with open(config.DATA_PATH.format("recommend", "relation_recommend.json"), "w") as fw:
            json.dump(sh_user_relation, fw, indent=4, ensure_ascii=False)

    def user_label_score(self, user_item_rating):
        # print("user-labels-rating 加载中...")
        user_label_score = {}
        goods_labels = self.process_items_data()
        for _, row in user_item_rating.iterrows():
            user_id, goods_id, rating = row["user_id"], row["goods_id"], row["rating"]
            try:
                labels = goods_labels[goods_labels["goods_id"] == goods_id]["labels"].values[0].split("|")
                for label in labels:
                    user_label_score.setdefault(user_id, {})
                    user_label_score[user_id].setdefault(label, 0)
                    user_label_score[user_id][label] += rating
            except IndexError:
                pass
                # print(goods_id, "商品已删除")
        return user_label_score

    # def user_view_log(self):
    #     """  浏览记录 """
    #     print("浏览记录加载中...")
    #     sql1 = "SELECT user_id, rec_id as goods_id FROM sh_user_view WHERE is_delete=0"
    #     df = pd.read_sql_query(sql1, self.engine)
    #     df[["user_id", "goods_id"]] = df[["user_id", "goods_id"]].applymap(str)
    #     user_view = {}
    #
    #     for _, row in df.iterrows():
    #         user_id, goods_id = row["user_id"], row["goods_id"]
    #         user_view.setdefault(user_id, [])
    #         user_view[user_id].append(goods_id)
    #     with open(config.DATA_PATH.format("model_data", "user_view"), "w") as fw:
    #         json.dump(user_view, fw)
