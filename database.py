"""
database.py - MySQL 连接与只读数据管理
职责：读取正式评论表、检测新数据；评论导入和变更统一经过审核工作台
"""

import pandas as pd
import os
from sqlalchemy import create_engine, text

# ==================== 数据库配置 ====================
DB_CONFIG = {
    'host':     'localhost',
    'port':     3306,
    'user':     'root',        # 改成你的MySQL用户名
    'password': '123456',            # 改成你的MySQL密码
    'database': 'tourism_db',
    'charset':  'utf8mb4'
}

CSV_PATH = r"D:\数据素养\standardized_final_v5.csv"

CSV_COLUMN_MAP = {
    '景点名称': 'spot_name',
    '评论内容': 'comment',
    '评分':     'sentiment_score',
    '用户名':   'user_name',
    '评论时间': 'comment_date',
}


class TourismDatabase:

    def __init__(self):
        self.engine = None
        self._connect()

    def _connect(self):
        try:
            url = (f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
                   f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
                   f"/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}")
            self.engine = create_engine(url, pool_recycle=3600, pool_pre_ping=True)
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("[DB] 数据库连接成功")
        except Exception as e:
            print(f"[DB][ERROR] 连接失败: {e}")
            self.engine = None

    def is_connected(self):
        if not self.engine:
            return False
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            self._connect()
            return self.engine is not None

    def get_total_count(self):
        if not self.is_connected():
            return 0
        try:
            with self.engine.connect() as conn:
                return conn.execute(text("SELECT COUNT(*) FROM comments")).scalar()
        except:
            return 0

    def get_latest_id(self):
        if not self.is_connected():
            return 0
        try:
            with self.engine.connect() as conn:
                val = conn.execute(text("SELECT COALESCE(MAX(id),0) FROM comments")).scalar()
                return val if val else 0
        except:
            return 0

    def has_new_data(self, current_count):
        db_count = self.get_total_count()
        if db_count > current_count:
            print(f"[DB] 新数据：数据库{db_count} > 当前{current_count}")
            return True, db_count
        return False, db_count

    def load_all_data(self):
        if not self.is_connected():
            return None
        try:
            df = pd.read_sql("SELECT * FROM comments ORDER BY id", self.engine)
            print(f"[DB] 加载 {len(df)} 条")
            return df
        except Exception as e:
            print(f"[DB][ERROR] 加载失败: {e}")
            return None

    def load_new_data(self, since_id=0):
        if not self.is_connected():
            return None
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(
                    text("SELECT * FROM comments WHERE id > :sid ORDER BY id"),
                    conn, params={'sid': since_id}
                )
            return df
        except Exception as e:
            print(f"[DB][ERROR] 增量加载失败: {e}")
            return None

    def init_from_csv(self, csv_path=None, force=False):
        """保留旧接口但禁止跳过审核流程或清空正式表。"""
        if force:
            raise RuntimeError('force=True 的清空重导已停用，避免误删正式评论。请使用 /review 导入并审核。')
        raise RuntimeError('直接 CSV 入库已停用。请在 /review 上传 CSV，审核完成后再发布。')

    def add_comment(self, spot_name, comment, sentiment_score,
                    user_name='', comment_date='', source='手动添加'):
        raise RuntimeError('直接写入评论已停用。请先创建审核批次并完成人工复核。')

    def batch_add_comments(self, df):
        raise RuntimeError('直接批量写入已停用。请先创建审核批次并完成人工复核。')


if __name__ == "__main__":
    db = TourismDatabase()
    if db.is_connected():
        print(f"当前数据库评论数：{db.get_total_count()}")
        print("CSV 导入和评论新增请从网页 /review 创建审核批次；本脚本不再清空或直接写入正式表。")
    else:
        print("数据库连接不可用。")
