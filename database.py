"""
database.py - 纯数据库导入与管理工具
职责：连接MySQL、原样导入CSV、读取数据、检测新数据
不做任何清洗，清洗全部交给 data_processor.py
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
        """从CSV原样导入，不做清洗"""
        if not self.is_connected():
            print("[DB][ERROR] 未连接")
            return 0

        path = csv_path or CSV_PATH
        if not os.path.exists(path):
            print(f"[DB][ERROR] 文件不存在: {path}")
            return 0

        current = self.get_total_count()
        if not force and current > 0:
            print(f"[DB] 已有 {current} 条，跳过（用 force=True 强制重导）")
            return current

        df = None
        for enc in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
            try:
                df = pd.read_csv(path, encoding=enc)
                break
            except:
                continue

        if df is None:
            print("[DB][ERROR] CSV读取失败")
            return 0

        print(f"[DB] CSV: {len(df)} 行, 列: {list(df.columns)}")

        df = df.rename(columns=CSV_COLUMN_MAP)
        if '序号' in df.columns:
            df = df.drop(columns=['序号'])

        df['source'] = '历史导入'

        for col in ['spot_name', 'comment', 'sentiment_score', 'user_name', 'comment_date', 'source']:
            if col not in df.columns:
                df[col] = ''

        if force:
            with self.engine.connect() as conn:
                conn.execute(text("TRUNCATE TABLE comments"))
                conn.commit()
            print("[DB] 已清空表")

        db_cols = ['spot_name', 'comment', 'sentiment_score', 'user_name', 'comment_date', 'source']
        df[db_cols].to_sql('comments', self.engine, if_exists='append', index=False, chunksize=500)

        total = self.get_total_count()
        print(f"[DB] ✅ 导入完成！共 {total} 条")
        return total

    def add_comment(self, spot_name, comment, sentiment_score,
                    user_name='', comment_date='', source='手动添加'):
        if not self.is_connected():
            return False
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO comments (spot_name,comment,sentiment_score,user_name,comment_date,source)
                    VALUES (:s,:c,:sc,:u,:d,:src)
                """), {'s':spot_name,'c':comment,'sc':int(sentiment_score),
                       'u':user_name,'d':comment_date,'src':source})
                conn.commit()
            return True
        except Exception as e:
            print(f"[DB][ERROR] 添加失败: {e}")
            return False

    def batch_add_comments(self, df):
        if not self.is_connected() or df is None or df.empty:
            return 0
        try:
            db_cols = ['spot_name','comment','sentiment_score','user_name','comment_date','source']
            for col in db_cols:
                if col not in df.columns:
                    df[col] = ''
            df[db_cols].to_sql('comments', self.engine, if_exists='append', index=False, chunksize=200)
            print(f"[DB] ✅ 批量入库 {len(df)} 条")
            return len(df)
        except Exception as e:
            print(f"[DB][ERROR] 批量失败: {e}")
            return 0


if __name__ == "__main__":
    print("=" * 50)
    print("  数据库工具")
    print("=" * 50)

    db = TourismDatabase()
    if not db.is_connected():
        print("❌ 连接失败")
    else:
        current = db.get_total_count()
        print(f"\n当前: {current} 条")

        if current > 0:
            print("\n1. 清空重导")
            print("2. 跳过")
            c = input("选择(1/2): ").strip()
            if c == '1':
                db.init_from_csv(force=True)
        else:
            print("\n数据库为空，开始导入...")
            db.init_from_csv()