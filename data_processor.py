"""
data_processor.py V5 - 所有分析全部走AI，保证质量
"""

import pandas as pd
import numpy as np
import jieba
import jieba.analyse
import re
import os
import time
import hashlib
import warnings
import requests
import threading
import time as time_module
import json
import random
from collections import Counter, defaultdict
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load project-root .env before reading the API keys below.
load_dotenv()

warnings.filterwarnings('ignore')

DATA_PATH       = r"D:\数据素养\standardized_final_v5.csv"
STOP_WORDS_PATH = r"C:\Users\wangjing\自然语言处理NLP\data\stop_words.utf8"


# ==================== AI API 配置（双引擎）====================
# Groq（国外，性能好，需翻墙）
AI_GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
AI_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
AI_GROQ_MODEL = "openai/gpt-oss-120b"

# 智谱AI（国内，免费，不用翻墙）
AI_ZHIPU_KEY = os.environ.get("ZHIPU_API_KEY", "").strip()
AI_ZHIPU_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
AI_ZHIPU_MODEL = "glm-4.7-flash"

# 默认使用哪个：'groq' 或 'zhipu'
AI_DEFAULT_ENGINE = "groq"

SENTIMENT_RANGES = {
    'positive': (4, 5),
    'neutral':  (3, 3),
    'negative': (1, 2)
}

OPERATION_TEMPLATES = {
    'cultural':      {'name': '文化深度体验型',   'strategies': ['打造沉浸式文化体验项目（汉服体验、非遗工坊）','开发文化IP联名产品，形成品牌矩阵','举办主题文化节庆活动，制造传播事件','建设数字化展陈系统，提升科技体验感']},
    'natural':       {'name': '自然生态休闲型',   'strategies': ['开发生态研学路线，打造教育+旅游融合产品','建设特色民宿集群，提升住宿体验','打造网红打卡点位，激发社交传播','推出四季主题活动，解决淡旺季问题']},
    'entertainment': {'name': '休闲娱乐综合型',   'strategies': ['引入夜经济业态，延长游客停留时间','开发亲子互动项目，拓展家庭客群','打造美食文化街区，丰富消费场景','建设智慧旅游系统，提升游览效率']},
    'historical':    {'name': '历史遗迹探访型',   'strategies': ['开发AR/VR历史重现体验，让文物"活"起来','推出专业讲解服务，提升文化传播深度','设计主题研学课程，吸引学生团体客群','打造历史文化街区，构建完整体验动线']}
}

SPOT_TYPE_KEYWORDS = {
    'cultural':      ['文化','艺术','博物馆','展览','非遗','传统','民俗','表演','戏曲'],
    'natural':       ['风景','山','水','湖','海','森林','自然','生态','花','公园'],
    'entertainment': ['美食','小吃','游乐','购物','夜市','娱乐','烧烤','网红'],
    'historical':    ['历史','古','遗址','古迹','城墙','寺庙','陵墓','朝代','兵马俑']
}
PLATFORM_RAW_DATA = {
        '兵马俑': {'mafengwo': 8065, 'ctrip': 139000, 'dianping': 208517},
        '陕西省历史博物馆': {'mafengwo': 6236, 'ctrip': 32000, 'dianping': 130536},
        '大唐芙蓉园': {'mafengwo': 2860, 'ctrip': 27000, 'dianping': 141009},
        '青龙寺': {'mafengwo': 489, 'ctrip': 546, 'dianping': 109010},
        '大雁塔': {'mafengwo': 4193, 'ctrip': 11000, 'dianping': 13966},
        '终南山南五台': {'mafengwo': 50, 'ctrip': 1357, 'dianping': 19237},
        '西安城墙': {'mafengwo': 7106, 'ctrip': 60000, 'dianping': 187733},
        '西安博物院': {'mafengwo': 1237, 'ctrip': 2872, 'dianping': 94995},
        '钟楼': {'mafengwo': 3139, 'ctrip': 23000, 'dianping': 23766},
        '大唐不夜城': {'mafengwo': 654, 'ctrip': 2003, 'dianping': 43870},
        '华清宫': {'mafengwo': 3971, 'ctrip': 31000, 'dianping': 37963},
        '白鹿原': {'mafengwo': 174, 'ctrip': 575, 'dianping': 32415},
    }

class TourismDataProcessor:

    def __init__(self):
        self.df              = None
        self.stop_words      = set()
        self._cache          = {}
        self._spot_names_set = set()
        self._db             = None
        self._current_count  = 0
        self._latest_id      = 0
        self._update_lock    = threading.Lock()

        # 初始化数据库
        self._init_database()

        self.load_stop_words()
        self.load_data()
        self._precompute()

        # 启动后台自动检测线程
        self._start_auto_check()

    # ================================================================
    # 数据加载
    # ================================================================
    def _init_database(self):
        """初始化数据库连接和数据导入"""
        try:
            from database import TourismDatabase
            self._db = TourismDatabase()
            if self._db.is_connected():
                # 如果数据库为空，从CSV导入
                count = self._db.get_total_count()
                if count == 0:
                    print("[INFO] 数据库为空，从CSV初始导入...")
                    self._db.init_from_csv()
                else:
                    print(f"[INFO] 数据库已有 {count} 条数据")
                self._current_count = self._db.get_total_count()
                self._latest_id = self._db.get_latest_id()
            else:
                print("[WARNING] 数据库连接失败，使用CSV模式")
                self._db = None
        except ImportError:
            print("[WARNING] database.py未找到，使用CSV模式")
            self._db = None
        except Exception as e:
            print(f"[WARNING] 数据库初始化失败: {e}，使用CSV模式")
            self._db = None

    def _start_auto_check(self):
        """启动后台线程，定时检测新数据"""
        def check_loop():
            while True:
                time_module.sleep(600)  # 每10分钟检查一次
                try:
                    self._check_and_update()
                except Exception as e:
                    print(f"[WARNING] 自动检测异常: {e}")

        t = threading.Thread(target=check_loop, daemon=True)
        t.start()
        print("[INFO] 数据自动更新线程已启动（每10分钟检测）")

    def _check_and_update(self):
        """检测数据库是否有新数据，有则增量更新"""
        if not self._db or not self._db.is_connected():
            return

        has_new, new_count = self._db.has_new_data(self._current_count)
        if not has_new:
            return

        print(f"[INFO] 检测到新数据，开始增量更新...")

        with self._update_lock:
            # 只加载新增的数据
            new_df = self._db.load_new_data(since_id=self._latest_id)
            if new_df is None or new_df.empty:
                return

            # 合并到现有DataFrame
            new_df = self._clean_new_data(new_df)
            if not new_df.empty:
                self.df = pd.concat([self.df, new_df], ignore_index=True)
                self._latest_id = self._db.get_latest_id()
                self._current_count = new_count

                # 重新预计算（清除缓存）
                self._cache.clear()
                self._precompute()
                print(f"[INFO] 增量更新完成，新增 {len(new_df)} 条，总计 {len(self.df)} 条")

    def force_full_reload(self):
        """强制全量重载数据 + 清空所有缓存"""
        with self._update_lock:
            print("[INFO] 强制全量重载...")

            # 清空所有缓存
            self._cache.clear()

            # 重新加载数据
            self.df = None
            self.load_data()

            # 重新预计算
            self._precompute()

            # 更新计数
            if self._db and self._db.is_connected():
                self._current_count = self._db.get_total_count()
                self._latest_id = self._db.get_latest_id()

            total = len(self.df) if self.df is not None else 0
            print(f"[INFO] 全量重载完成，共 {total} 条")
            return total

    def _clean_new_data(self, df):
        """清洗新增数据"""
        df = df.copy()
        df['comment'] = df['comment'].astype(str).apply(self._clean_text)
        df = df[df['comment'].str.len() > 2]
        df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')
        df = df.dropna(subset=['sentiment_score'])
        df['sentiment_score'] = df['sentiment_score'].clip(1, 5).astype(int)
        if 'comment_date' in df.columns:
            df = df.rename(columns={'comment_date': 'date'})
            # 统一日期格式
            df['date'] = df['date'].astype(str).str.replace('/', '-', regex=False)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        if 'user_name' in df.columns:
            df = df.rename(columns={'user_name': 'user'})
        return df


    def load_stop_words(self):
        try:
            if os.path.exists(STOP_WORDS_PATH):
                with open(STOP_WORDS_PATH, 'r', encoding='utf-8') as f:
                    self.stop_words = set(line.strip() for line in f if line.strip())
                print(f"[INFO] 停用词表加载成功，共 {len(self.stop_words)} 个")
            else:
                print(f"[WARNING] 停用词文件不存在: {STOP_WORDS_PATH}")
        except Exception as e:
            print(f"[ERROR] 加载停用词失败: {e}")
        extra = {
            '的','了','在','是','我','有','和','就','不','人','都','一','一个',
            '上','也','很','到','说','要','去','你','会','着','没有','看','好',
            '自己','这','他','她','它','们','那','些','什么','怎么','可以',
            '这个','那个','但是','因为','所以','如果','还是','已经','可能',
            '比较','非常','真的','觉得','应该','这里','那里','大家','时候',
            '知道','出来','起来','然后','之后','之前','还有','而且','或者',
            '虽然','不过','只是','毕竟','一下','确实','整体','基本','主要',
            '特别','真是','简直','居然','竟然','反正','总之','哈哈','嗯嗯',
            '哦','啊','呢','吧','吗','嘛','呀','景区','景点','旅游','游客',
            '门票','导游','地方','一般','感觉','来说','个人','总体','不错','还行',
        }
        self.stop_words.update(extra)

    def load_data(self):
        """优先从数据库加载，失败则从CSV"""

        # 优先数据库
        if self._db and self._db.is_connected():
            try:
                df = self._db.load_all_data()
                if df is not None and not df.empty:
                    self.df = df

                    # 列名适配
                    if 'comment_date' in self.df.columns and 'date' not in self.df.columns:
                        self.df = self.df.rename(columns={'comment_date': 'date'})
                    if 'user_name' in self.df.columns and 'user' not in self.df.columns:
                        self.df = self.df.rename(columns={'user_name': 'user'})

                    # 宽松清洗：不删除任何行，只做格式转换
                    if 'comment' in self.df.columns:
                        self.df['comment'] = self.df['comment'].astype(str).str.strip()

                    if 'sentiment_score' in self.df.columns:
                        self.df['sentiment_score'] = pd.to_numeric(
                            self.df['sentiment_score'], errors='coerce')
                        self.df['sentiment_score'] = self.df['sentiment_score'].fillna(5).clip(1, 5).astype(int)

                    if 'spot_name' in self.df.columns:
                        self.df['spot_name'] = self.df['spot_name'].astype(str).str.strip()
                        self.df = self.df[self.df['spot_name'].str.len() > 0]
                        self.df = self.df[self.df['spot_name'] != 'nan']

                    if 'date' in self.df.columns:
                        # 统一日期格式：把斜杠转成横杠
                        self.df['date'] = self.df['date'].astype(str).str.replace('/', '-', regex=False)
                        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')

                    # 景点名加入停用词
                    if 'spot_name' in self.df.columns:
                        self._spot_names_set = set(self.df['spot_name'].unique())
                        for name in self._spot_names_set:
                            self.stop_words.add(name)
                            for i in range(len(name)):
                                for j in range(i + 2, len(name) + 1):
                                    self.stop_words.add(name[i:j])

                    print(f"[INFO] 从数据库加载成功，共 {len(self.df)} 条，{self.df['spot_name'].nunique()} 个景点")
                    print(f"[INFO] 景点列表：{sorted(self.df['spot_name'].unique().tolist())}")
                    return
            except Exception as e:
                print(f"[WARNING] 数据库加载失败: {e}，降级使用CSV")
                import traceback
                traceback.print_exc()

        # 降级：从CSV加载
        try:
            for enc in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin1']:
                try:
                    self.df = pd.read_csv(DATA_PATH, encoding=enc)
                    print(f"[INFO] CSV加载成功，编码: {enc}")
                    break
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue

            if self.df is None:
                raise ValueError("无法读取CSV")

            print(f"[INFO] 列名: {list(self.df.columns)}")
            self._standardize_columns()
            self._clean_data()

            if 'spot_name' in self.df.columns:
                self._spot_names_set = set(self.df['spot_name'].unique())
                for name in self._spot_names_set:
                    self.stop_words.add(name)
                    for i in range(len(name)):
                        for j in range(i + 2, len(name) + 1):
                            self.stop_words.add(name[i:j])

            print(f"[INFO] CSV加载完成，{len(self.df)} 条，{self.df['spot_name'].nunique()} 个景点")

        except Exception as e:
            print(f"[ERROR] 数据加载失败: {e}")
            import traceback
            traceback.print_exc()
            self._create_demo_data()

    def get_db_status(self):
        """获取数据库状态（供前端展示）"""
        if not self._db or not self._db.is_connected():
            return {'connected': False, 'mode': 'CSV', 'total': len(self.df) if self.df is not None else 0}
        return {
            'connected': True,
            'mode': 'MySQL',
            'total': self._current_count,
            'latest_id': self._latest_id,
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _standardize_columns(self):
        col_exact = {c.strip(): c for c in self.df.columns}
        col_lower = {c.lower().strip(): c for c in self.df.columns}
        mapping   = {}
        def try_map(keys):
            for k in keys:
                if k in col_exact:         return col_exact[k]
                if k.lower() in col_lower: return col_lower[k.lower()]
            return None
        pairs = [
            ('spot_name',       ['景点名称','景区名称','景点','目的地','spot_name','name','attraction']),
            ('comment',         ['评论内容','评论','内容','评价','comment','review','content','text']),
            ('sentiment_score', ['评分','情感分数','分数','星级','标注','sentiment_score','score','rating','label']),
            ('date',            ['评论时间','日期','时间','发布时间','date','time','datetime']),
            ('user',            ['用户名','用户','昵称','user','username','author']),
        ]
        for target, keys in pairs:
            src = try_map(keys)
            if src and src != target:
                mapping[src] = target
        if mapping:
            self.df = self.df.rename(columns=mapping)
            print(f"[INFO] 列名映射: {mapping}")

    def _clean_data(self):
        essential = [c for c in ['spot_name','comment','sentiment_score'] if c in self.df.columns]
        self.df = self.df.dropna(subset=essential)
        if 'comment' in self.df.columns:
            self.df['comment'] = self.df['comment'].astype(str).apply(self._clean_text)
            self.df = self.df[self.df['comment'].str.len() > 2]
        if 'sentiment_score' in self.df.columns:
            self.df['sentiment_score'] = pd.to_numeric(self.df['sentiment_score'], errors='coerce')
            self.df = self.df.dropna(subset=['sentiment_score'])
            self.df['sentiment_score'] = self.df['sentiment_score'].clip(1,5).astype(int)
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        if 'spot_name' in self.df.columns:
            self.df['spot_name'] = self.df['spot_name'].astype(str).str.strip()
            self.df = self.df[(self.df['spot_name'].str.len()>0)&(self.df['spot_name']!='nan')]

    def _clean_text(self, text):
        if not isinstance(text, str): return ''
        text = re.sub(r'<[^>]+>','',text)
        text = re.sub(r'http[s]?://\S+','',text)
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？、；：""''（）\s]','',text)
        return re.sub(r'\s+',' ',text).strip()

    def _create_demo_data(self):
        print("[WARNING] 使用演示数据")
        spots = ['大唐不夜城','兵马俑','华清宫','大雁塔','陕西历史博物馆']
        pool  = {
            5:['夜景非常漂亮，灯光绚丽多彩，强烈推荐！','历史文化底蕴深厚，陈列丰富令人震撼','表演精彩绝伦，演员功底深厚值得一看'],
            4:['整体体验不错，建筑风格独特，风景优美','宏伟壮观，历史感很强，值得专程游览','文化氛围浓厚，讲解员专业，推荐参观'],
            3:['节假日人太多，排队时间长，体验一般','商业化气息较重，景色还行但性价比一般','门票价格偏高，内容与预期有一定差距'],
            2:['工作人员服务态度冷漠，令人非常失望','管理混乱，排队秩序差，体验很差','厕所卫生条件差，整体环境需要改善'],
            1:['完全不值得去，服务极差，体验极其糟糕','被宰客，强制消费，坚决不推荐','设施严重老化，管理混乱，与宣传严重不符']
        }
        data=[]
        np.random.seed(42)
        for spot in spots:
            for _ in range(np.random.randint(80,200)):
                score=np.random.choice([1,2,3,4,5],p=[0.05,0.1,0.2,0.35,0.3])
                data.append({'spot_name':spot,'comment':np.random.choice(pool[score]),
                             'sentiment_score':score,'date':datetime.now()-timedelta(days=np.random.randint(0,365))})
        self.df=pd.DataFrame(data)

    # ================================================================
    # 预计算
    # ================================================================

    def _precompute(self):
        print("[INFO] 预计算中...")
        t=time.time()
        stats=self.df.groupby('spot_name').agg(
            comment_count  =('comment','count'),
            avg_score      =('sentiment_score','mean'),
            score_std      =('sentiment_score','std'),
            positive_count =('sentiment_score',lambda x:(x>=4).sum()),
            negative_count =('sentiment_score',lambda x:(x<=2).sum())
        ).reset_index()
        stats['positive_rate']=(stats['positive_count']/stats['comment_count']*100).round(1)
        stats['negative_rate']=(stats['negative_count']/stats['comment_count']*100).round(1)
        max_c=stats['comment_count'].max()
        stats['heat_index']=(stats['comment_count']/max_c*40+stats['avg_score']/5*35+stats['positive_rate']/100*25).round(1)
        stats['avg_score']=stats['avg_score'].round(2)
        stats['score_std']=stats['score_std'].round(2).fillna(0)
        self._cache['spot_stats']=stats.sort_values('heat_index',ascending=False)

        self._cache['score_dist_by_spot']={}
        for spot in self.df['spot_name'].unique():
            raw=self.df[self.df['spot_name']==spot]['sentiment_score'].value_counts().to_dict()
            self._cache['score_dist_by_spot'][spot]={int(i):int(raw.get(i,0)) for i in range(1,6)}

        self._cache['comments_by_spot_sentiment']={}
        for spot in self.df['spot_name'].unique():
            self._cache['comments_by_spot_sentiment'][spot]={}
            for level,(lo,hi) in SENTIMENT_RANGES.items():
                mask=((self.df['spot_name']==spot)&(self.df['sentiment_score']>=lo)&(self.df['sentiment_score']<=hi))
                self._cache['comments_by_spot_sentiment'][spot][level]=self.df[mask]['comment'].tolist()

        self._cache['global_sentiment_comments']={}
        for level,(lo,hi) in SENTIMENT_RANGES.items():
            mask=(self.df['sentiment_score']>=lo)&(self.df['sentiment_score']<=hi)
            self._cache['global_sentiment_comments'][level]=self.df[mask]['comment'].tolist()

        list(jieba.cut('预热'))
        print(f"[INFO] 预计算完成，耗时 {time.time()-t:.1f}s")

    def _get_cache_key(self,*args):
        return hashlib.md5(str(args).encode()).hexdigest()

    # ================================================================
    # 词云词频
    # ================================================================

    def _simple_word_freq(self, text, top_n=80):
        words=jieba.cut(text,cut_all=False)
        counts=Counter()
        for w in words:
            w=w.strip()
            if(len(w)>=2 and w not in self.stop_words and not w.isdigit()
               and not re.match(r'^[a-zA-Z]{1,3}$',w) and w not in self._spot_names_set):
                if not any(w in name for name in self._spot_names_set):
                    counts[w]+=1
        return counts.most_common(top_n)

    # ================================================================
    # AI 核心调用
    # ================================================================
    def _call_ai(self, prompt, max_tokens=2500, engine=None):
        """双引擎AI：Groq限流立即切智谱"""
        if engine is None:
            engine = getattr(self, '_current_engine', AI_DEFAULT_ENGINE)

        if engine == 'groq':
            api_key, api_url, model = AI_GROQ_KEY, AI_GROQ_URL, AI_GROQ_MODEL
        else:
            api_key, api_url, model = AI_ZHIPU_KEY, AI_ZHIPU_URL, AI_ZHIPU_MODEL

        if not api_key:
            alt = 'zhipu' if engine == 'groq' else 'groq'
            alt_key = AI_ZHIPU_KEY if alt == 'zhipu' else AI_GROQ_KEY
            if alt_key:
                print(f"[INFO] {engine}未配Key，切换{alt}")
                return self._call_ai(prompt, max_tokens, engine=alt)
            return None

        system_prompt = ('你是专业的中文文旅数据分析师，请严格用中文回答，'
                        '分析深入具体，不得输出单个词语，'
                        '每条结论都要有数据支撑或具体描述。')

        for attempt in range(3):
            try:
                resp = requests.post(
                    api_url,
                    headers={'Authorization': f'Bearer {api_key}',
                             'Content-Type': 'application/json'},
                    json={
                        'model': model,
                        'messages': [
                            {'role': 'system', 'content': system_prompt},
                            {'role': 'user', 'content': prompt}
                        ],
                        'max_tokens': max_tokens,
                        'temperature': 0.5
                    },
                    timeout=90
                )

                if resp.status_code == 200:
                    result = resp.json()['choices'][0]['message']['content'].strip()
                    print(f"[INFO] AI({engine}/{model})成功，{len(result)}字")
                    return result

                elif resp.status_code == 429:
                    print(f"[WARNING] AI({engine})限流")
                    # Groq限流→立即切智谱
                    if engine == 'groq' and AI_ZHIPU_KEY:
                        print("[INFO] Groq限流，切换智谱")
                        return self._call_ai(prompt, max_tokens, engine='zhipu')
                    # 智谱限流→短暂等待重试
                    time.sleep(2 + attempt * 2)
                    continue

                else:
                    print(f"[WARNING] AI({engine}/{model})返回{resp.status_code}")
                    if engine == 'groq' and AI_ZHIPU_KEY:
                        print("[INFO] Groq异常，切换智谱")
                        return self._call_ai(prompt, max_tokens, engine='zhipu')
                    return None

            except requests.exceptions.Timeout:
                print(f"[WARNING] AI({engine})超时，重试{attempt+1}")
                if engine == 'groq' and AI_ZHIPU_KEY and attempt >= 1:
                    print("[INFO] Groq超时，切换智谱")
                    return self._call_ai(prompt, max_tokens, engine='zhipu')
                continue

            except Exception as e:
                print(f"[WARNING] AI({engine})失败: {e}")
                if engine == 'groq' and AI_ZHIPU_KEY:
                    print("[INFO] Groq异常，切换智谱")
                    return self._call_ai(prompt, max_tokens, engine='zhipu')
                return None

        print(f"[WARNING] AI({engine})3次均失败")
        return None

    def _get_engine_label(self):
        """获取当前引擎的显示名称"""
        engine = getattr(self, '_current_engine', AI_DEFAULT_ENGINE)
        if engine == 'groq':
            return f"Groq ({AI_GROQ_MODEL})"
        else:
            return f"智谱AI ({AI_ZHIPU_MODEL})"

    def set_engine(self, engine):
        if engine in ('groq', 'zhipu'):
            self._current_engine = engine
            # 清除所有AI相关缓存（按引擎区分后其实不用全清，但保险起见）
            keys_to_remove = [k for k in list(self._cache.keys())
                            if any(x in str(k) for x in ['ai_', 'kw_', 'success'])]
            for k in keys_to_remove:
                del self._cache[k]
            print(f"[INFO] 引擎切换: {engine}")
            return True
        return False

    def get_current_engine(self):
        return getattr(self, '_current_engine', AI_DEFAULT_ENGINE)

    def _extract_json_text(self, text):
        """从AI返回中稳定提取JSON"""
        if not text:
            return None
        text = text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()
        match = re.search(r'\{[\s\S]*\}', text)
        return match.group(0) if match else None
    # ================================================================
    # AI 关键短语提取（用于景点深度分析中的情感短语展示）
    # ================================================================

    def get_ai_keywords(self, spot_name=None):
            """提取情感短语，缓存key含引擎名，空结果不缓存"""
            engine = getattr(self, '_current_engine', AI_DEFAULT_ENGINE)
            cache_key = self._get_cache_key('ai_kw_v7', spot_name, engine)

            if cache_key in self._cache:
                cached = self._cache[cache_key]
                if any(cached.get(k) for k in ['positive', 'neutral', 'negative']):
                    return cached

            def sample(level, n=60):
                if spot_name:
                    comments = self._cache.get('comments_by_spot_sentiment', {}).get(spot_name, {}).get(level, [])
                else:
                    comments = self._cache.get('global_sentiment_comments', {}).get(level, [])
                if len(comments) > n:
                    random.seed(42)
                    comments = random.sample(comments, n)
                return comments

            pos_c = sample('positive')
            neu_c = sample('neutral')
            neg_c = sample('negative')
            spot_label = f"景点「{spot_name}」" if spot_name else "所有景点"

            prompt = f"""以下是{spot_label}的真实游客评论，按情感分为三组。
    请从每组评论中提炼 8~12 条完整的、有实际意义的短句或短语。

    【严格要求】
    - 每条必须是完整表达一个具体观点的短句
    - ✅ 正确："夜景灯光绚丽令人震撼"、"服务态度冷漠工作人员不热情"
    - ❌ 错误："讲解"、"里面"、"不好"（单个词或意义不明的片段）

    【好评评论（{len(pos_c)}条）】
    {chr(10).join(pos_c[:40])}

    【中性评论（{len(neu_c)}条）】
    {chr(10).join(neu_c[:25])}

    【差评评论（{len(neg_c)}条）】
    {chr(10).join(neg_c[:40])}

    请严格按以下JSON格式输出，不输出任何其他内容：
    {{
      "positive": ["完整短句1", "完整短句2", "完整短句3", "完整短句4", "完整短句5", "完整短句6", "完整短句7", "完整短句8"],
      "neutral":  ["完整短句1", "完整短句2", "完整短句3", "完整短句4", "完整短句5"],
      "negative": ["完整短句1", "完整短句2", "完整短句3", "完整短句4", "完整短句5", "完整短句6", "完整短句7", "完整短句8"]
    }}"""

            ai_text = self._call_ai(prompt, max_tokens=1200)
            result = {'positive': [], 'neutral': [], 'negative': []}

            if ai_text:
                try:
                    json_text = self._extract_json_text(ai_text)
                    if json_text:
                        parsed = json.loads(json_text)
                        for level in ['positive', 'neutral', 'negative']:
                            phrases = parsed.get(level, [])
                            result[level] = [p.strip() for p in phrases
                                             if isinstance(p, str) and len(p.strip()) >= 4]
                    else:
                        print(f"[WARNING] AI返回非JSON: {ai_text[:200]}")
                except Exception as e:
                    print(f"[WARNING] 关键词解析失败: {e}")

            # 只缓存非空结果
            if any(result.get(k) for k in ['positive', 'neutral', 'negative']):
                self._cache[cache_key] = result

            return result

    # ================================================================
    # AI 景点深度分析（景点详情页专用）
    # ================================================================
    def get_ai_insight(self, spot_name):
        """让 AI 提炼景点的【亮点 + 待改进点】结构化短语，用于 Hero 区智能洞察卡"""
        cache_key = self._get_cache_key('ai_insight', spot_name)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 取景点数据
        spot_df = self.df[self.df['spot_name'] == spot_name]
        if spot_df.empty:
            return {"highlights": [], "improvements": []}

        # 抽样评论（按情感分层）
        pos_samples = spot_df[spot_df['sentiment_score'] >= 4]['comment'].dropna().tolist()[:25]
        neg_samples = spot_df[spot_df['sentiment_score'] <= 2]['comment'].dropna().tolist()[:25]

        if not pos_samples and not neg_samples:
            return {"highlights": [], "improvements": []}

        avg_score = round(spot_df['sentiment_score'].mean(), 2)
        total = len(spot_df)

        prompt = f"""你是文旅数据分析师。请基于以下【{spot_name}】的游客评论数据，提炼出该景点的【亮点】和【待改进点】。

    景点基本信息：
    - 总评论数：{total}
    - 平均评分：{avg_score}/5

    【好评样本】（{len(pos_samples)}条）:
    {chr(10).join(['· ' + str(c)[:80] for c in pos_samples[:15]])}

    【差评样本】（{len(neg_samples)}条）:
    {chr(10).join(['· ' + str(c)[:80] for c in neg_samples[:15]])}

    请严格按以下 JSON 格式输出（不要任何额外说明，不要 markdown 代码块）：
    {{
      "highlights": ["亮点1（6-12字短语）", "亮点2", "亮点3", "亮点4"],
      "improvements": ["待改进1（6-12字短语）", "待改进2", "待改进3", "待改进4"]
    }}

    要求：
    1. 每边必须 4 条
    2. 每条短语 6-12 个字，简洁有力
    3. 亮点要具体（如"夜景灯光震撼"而非"很好看"）
    4. 待改进要建设性（如"票价偏高争议"而非"垃圾景点"）
    5. 只输出 JSON，不要其他任何文字
    """

        ai_text = self._call_ai(prompt, max_tokens=600)
        if not ai_text:
            return {"highlights": [], "improvements": []}

        # 解析 JSON
        import json as _json
        try:
            json_str = self._extract_json_text(ai_text) or ai_text
            result = _json.loads(json_str)
            highlights = result.get('highlights', [])[:5]
            improvements = result.get('improvements', [])[:5]
            out = {"highlights": highlights, "improvements": improvements}
            # 只在两边都有数据时缓存
            if highlights and improvements:
                self._cache[cache_key] = out
            return out
        except Exception as e:
            return {"highlights": [], "improvements": [], "error": str(e)}
    def get_ai_spot_analysis(self, spot_name):
        """景点深度分析，返回结果带引擎标识"""
        engine = getattr(self, '_current_engine', AI_DEFAULT_ENGINE)
        cache_key = self._get_cache_key('ai_spot_v7', spot_name, engine)
        if cache_key in self._cache:
            return self._cache[cache_key]

        detail = self.get_spot_detail(spot_name)
        if not detail:
            return {'error': '景点未找到'}

        kw = self.get_ai_keywords(spot_name)
        pos_str = '；'.join(kw.get('positive', [])[:8])
        neg_str = '；'.join(kw.get('negative', [])[:8])
        neu_str = '；'.join(kw.get('neutral', [])[:5])

        # 补充原始评论
        pos_comments = self._cache.get('comments_by_spot_sentiment', {}).get(spot_name, {}).get('positive', [])
        neg_comments = self._cache.get('comments_by_spot_sentiment', {}).get(spot_name, {}).get('negative', [])
        neu_comments = self._cache.get('comments_by_spot_sentiment', {}).get(spot_name, {}).get('neutral', [])
        random.seed(42)
        pos_samples = random.sample(pos_comments, min(10, len(pos_comments))) if pos_comments else []
        neg_samples = random.sample(neg_comments, min(10, len(neg_comments))) if neg_comments else []
        neu_samples = random.sample(neu_comments, min(5, len(neu_comments))) if neu_comments else []

        comp = detail.get('competitiveness', {})
        comp_info = ''
        if comp:
            comp_info = f"- 评论量排名：{comp.get('comment_rank', 'N/A')}，超过{comp.get('percentile_comment', 0)}%\n- 评分排名：{comp.get('score_rank', 'N/A')}，超过{comp.get('percentile_score', 0)}%\n- 好评率排名：{comp.get('positive_rank', 'N/A')}，超过{comp.get('percentile_positive', 0)}%"

        prompt = f"""你是专业文旅分析师，请对「{spot_name}」进行深度分析。

    【数据】
    - 评论数：{detail['total_comments']}，评分：{detail['avg_score']}/5
    - 好评率：{detail['positive_rate']}%，差评率：{detail['negative_rate']}%
    {comp_info}

    【AI提炼短语】好评：{pos_str or '提炼中'}
    差评：{neg_str or '提炼中'}
    中性：{neu_str or '提炼中'}

    【真实好评评论】
    {chr(10).join(pos_samples) if pos_samples else '暂无'}

    【真实差评评论】
    {chr(10).join(neg_samples) if neg_samples else '暂无'}

    【真实中性评论】
    {chr(10).join(neu_samples) if neu_samples else '暂无'}

    重要：必须引用上面的真实评论进行分析，不要说"没有具体数据"。

    请用中文markdown输出：
    ## 一、景点核心竞争力分析
    ## 二、游客痛点深度剖析
    ## 三、游客画像与行为洞察
    ## 四、对标竞品差距分析
    ## 五、精准改进建议"""

        ai_text = self._call_ai(prompt, max_tokens=2500)
        engine_label = self._get_engine_label()

        if ai_text:
            result = {'status': 'success', 'content': ai_text,
                      'source': 'ai', 'engine': engine_label}
        else:
            result = {'status': 'fallback',
                      'content': self._fallback_spot_analysis(spot_name, detail, kw),
                      'source': 'local', 'engine': '本地模板'}

        self._cache[cache_key] = result
        return result

    # ================================================================
    # AI 旅游规划分析（旅游规划页专用）
    # ================================================================

    def get_ai_travel_plan(self, spot_name):
            engine = getattr(self, '_current_engine', AI_DEFAULT_ENGINE)
            cache_key = self._get_cache_key('ai_plan_v7', spot_name, engine)
            if cache_key in self._cache:
                return self._cache[cache_key]

            detail = self.get_spot_detail(spot_name)
            if not detail:
                return {'error': '景点未找到'}

            kw = self.get_ai_keywords(spot_name)
            pos_str = '；'.join(kw.get('positive', [])[:8])
            neg_str = '；'.join(kw.get('negative', [])[:8])

            pos_comments = self._cache.get('comments_by_spot_sentiment', {}).get(spot_name, {}).get('positive', [])
            neg_comments = self._cache.get('comments_by_spot_sentiment', {}).get(spot_name, {}).get('negative', [])
            random.seed(42)
            pos_samples = random.sample(pos_comments, min(8, len(pos_comments))) if pos_comments else []
            neg_samples = random.sample(neg_comments, min(8, len(neg_comments))) if neg_comments else []

            spot_type = self._determine_spot_type(
                ' '.join(self.df[self.df['spot_name'] == spot_name]['comment'].tolist()))
            template = OPERATION_TEMPLATES.get(spot_type, OPERATION_TEMPLATES['entertainment'])

            prompt = f"""你是资深文旅规划专家，请为「{spot_name}」制定规划。

    【数据】类型：{template['name']}，评论：{detail['total_comments']}条，评分：{detail['avg_score']}/5
    好评率：{detail['positive_rate']}%，差评率：{detail['negative_rate']}%
    好评短语：{pos_str or '提炼中'}
    差评短语：{neg_str or '提炼中'}

    【真实好评】{chr(10).join(pos_samples) if pos_samples else '暂无'}
    【真实差评】{chr(10).join(neg_samples) if neg_samples else '暂无'}

    请用中文markdown输出：
    ## 一、景点定位与核心卖点
    ## 二、精品游览路线设计（含时间）
    ## 三、游客体验提升方案（针对差评）
    ## 四、特色活动与产品开发
    ## 五、营销传播策略
    ## 六、风险预警"""

            ai_text = self._call_ai(prompt, max_tokens=2500)
            engine_label = self._get_engine_label()

            if ai_text:
                result = {'status': 'success', 'content': ai_text,
                          'source': 'ai', 'engine': engine_label}
            else:
                result = {'status': 'fallback',
                          'content': self._fallback_travel_plan(spot_name, detail, template),
                          'source': 'local', 'engine': '本地模板'}

            self._cache[cache_key] = result
            return result

    # ================================================================
    # AI 运营模式分析（运营模式页专用）
    # ================================================================
    def get_ai_operation_model(self, spot_name):
        engine = getattr(self, '_current_engine', AI_DEFAULT_ENGINE)
        cache_key = self._get_cache_key('ai_op_v8', spot_name, engine)
        if cache_key in self._cache:
            return self._cache[cache_key]

        detail = self.get_spot_detail(spot_name)
        if not detail:
            return {'error': '景点未找到'}

        # === 评分分布 ===
        score_dist = detail.get('score_distribution', {}) or {}
        score_dist_str = (
            f"5分：{score_dist.get(5, 0)}条，4分：{score_dist.get(4, 0)}条，"
            f"3分：{score_dist.get(3, 0)}条，2分：{score_dist.get(2, 0)}条，"
            f"1分：{score_dist.get(1, 0)}条"
        )

        # === 高频评价词 TOP12 ===
        wordcloud = detail.get('wordcloud', []) or []
        top_keywords = [w['name'] for w in wordcloud[:12]] if wordcloud else []
        keywords_str = '、'.join(top_keywords) if top_keywords else '暂无'

        # === AI 亮点/待改进（兜底）===
        try:
            ai_insight = self.get_ai_insight(spot_name) or {}
        except Exception:
            ai_insight = {}
        highlights = ai_insight.get('highlights', []) if ai_insight else []
        improvements = ai_insight.get('improvements', []) if ai_insight else []
        highlights_str = '；'.join(highlights[:5]) if highlights else '暂无'
        improvements_str = '；'.join(improvements[:5]) if improvements else '暂无'

        # === 热度趋势 ===
        trend = detail.get('trend', []) or []
        trend_text = ""
        if len(trend) >= 2:
            last = trend[-1]
            prev = trend[-2]
            change = last.get('count', 0) - prev.get('count', 0)
            if change > 0:
                trend_text = f"近两月评论量增长 {change} 条，热度上升"
            elif change < 0:
                trend_text = f"近两月评论量下降 {abs(change)} 条，需关注"
            else:
                trend_text = "近两月评论量持平"

        # === AI 短语 ===
        kw = self.get_ai_keywords(spot_name) or {}
        pos_str = '；'.join(kw.get('positive', [])[:8])
        neg_str = '；'.join(kw.get('negative', [])[:8])

        # === 真实评论样本（带兜底）===
        comments_by_sent = self._cache.get('comments_by_spot_sentiment', {}) or {}
        spot_comments = comments_by_sent.get(spot_name, {}) or {}
        pos_comments = spot_comments.get('positive', []) or []
        neg_comments = spot_comments.get('negative', []) or []
        random.seed(42)
        pos_samples = random.sample(pos_comments, min(8, len(pos_comments))) if pos_comments else []
        neg_samples = random.sample(neg_comments, min(8, len(neg_comments))) if neg_comments else []

        # === TOP3 参照景点 ===
        top3 = self.get_spot_rankings(top_n=3)
        top3_info = '\n'.join([
            f"- {s['spot_name']}：评分{s['avg_score']}，好评率{s['positive_rate']}%，热度{s['heat_index']}"
            for s in top3
        ])

        prompt = f"""你是文旅运营专家，请为「{spot_name}」制定运营模式。

    【基础数据】评论：{detail['total_comments']}条，评分：{detail['avg_score']}/5
    好评率：{detail['positive_rate']}%，差评率：{detail['negative_rate']}%
    评分分布：{score_dist_str}
    热度趋势：{trend_text}

    【高频评价词】{keywords_str}

    【AI亮点】{highlights_str}
    【AI待改进】{improvements_str}

    【好评短语】{pos_str or '提炼中'}
    【差评短语】{neg_str or '提炼中'}

    【真实好评】{chr(10).join(pos_samples) if pos_samples else '暂无'}
    【真实差评】{chr(10).join(neg_samples) if neg_samples else '暂无'}

    【TOP3景点参照】
    {top3_info}

    请用中文markdown输出以下六个部分，要求结合数据给出具体分析：
    ## 一、"出圈"潜力评估（基于数据给出高/中/低评级）
    ## 二、核心成功要素（提炼3-5点，每点引用数据）
    ## 三、核心痛点与改进方向（针对差评数据，提出3-5点）
    ## 四、对标头部景点差距（对比TOP3，指出关键差距）
    ## 五、可复制运营框架（内容、体验、营销、数据四维度）
    ## 六、短期行动计划（3个月，列出5项具体行动，含做法和预期效果）"""

        ai_text = self._call_ai(prompt, max_tokens=2800)
        engine_label = self._get_engine_label()

        if ai_text:
            result = {'status': 'success', 'content': ai_text,
                      'source': 'ai', 'engine': engine_label}
        else:
            result = {'status': 'fallback',
                      'content': self._fallback_operation_model(spot_name, detail),
                      'source': 'local', 'engine': '本地模板'}

        self._cache[cache_key] = result
        return result

    # ================================================================
    # 兜底分析（AI失败时）- 注意：只在AI真的无法调用时使用
    # ================================================================

    def _fallback_spot_analysis(self, spot_name, detail, kw):
        pos=kw.get('positive',[])
        neg=kw.get('negative',[])
        return f"""## {spot_name} 景点深度分析

> ⚠️ AI服务暂时不可用，以下为基于数据的本地分析，建议配置AI Key获取深度分析。

### 数据概况
- 总评论 **{detail['total_comments']}** 条，平均评分 **{detail['avg_score']}** 分
- 好评率 **{detail['positive_rate']}%**，差评率 **{detail['negative_rate']}%**

### 游客正面反馈
{''.join(f'- {p}{chr(10)}' for p in pos) if pos else '- 暂无足够好评数据'}

### 游客主要问题
{''.join(f'- {p}{chr(10)}' for p in neg) if neg else '- 暂无足够差评数据'}

### 基础建议
- 针对差评中的问题建立专项整改机制
- 围绕好评亮点打造核心体验产品
- 建立数据监测体系，持续追踪口碑变化"""

    def _fallback_travel_plan(self, spot_name, detail, template):
        return f"""## {spot_name} 旅游规划方案

> ⚠️ AI服务暂时不可用，以下为基础模板方案。

### 景点类型
{template['name']}

### 推荐运营策略
{''.join(f'- {s}{chr(10)}' for s in template['strategies'])}

### 数据参考
- 当前评分：{detail['avg_score']}/5，好评率：{detail['positive_rate']}%
- 建议重点改善差评率（当前{detail['negative_rate']}%）"""

    def _fallback_operation_model(self, spot_name, detail):
        return f"""## {spot_name} 运营模式分析

> ⚠️ AI服务暂时不可用，以下为基础数据展示。

### 数据概况
- 评论数：{detail['total_comments']}，评分：{detail['avg_score']}/5
- 好评率：{detail['positive_rate']}%，差评率：{detail['negative_rate']}%

### 建议
- 请配置AI API Key以获取完整的运营模式分析报告"""

    # ================================================================
    # 运营模式页的成功共性因子（从TOP景点提炼）
    # ================================================================

    def get_success_factors(self):
            engine = getattr(self, '_current_engine', AI_DEFAULT_ENGINE)
            cache_key = f'success_factors_v7_{engine}'
            if cache_key in self._cache:
                return self._cache[cache_key]

            rankings = self.get_spot_rankings(top_n=5)
            if not rankings:
                return []

            all_pos = []
            spot_info = []
            for r in rankings:
                spot = r['spot_name']
                comments = self._cache.get('comments_by_spot_sentiment', {}).get(spot, {}).get('positive', [])
                if comments:
                    random.seed(42)
                    all_pos.extend(random.sample(comments, min(15, len(comments))))
                spot_info.append(f"「{spot}」评分{r['avg_score']}，好评率{r['positive_rate']}%")

            if not all_pos:
                return self._fallback_success_factors(rankings)

            prompt = f"""以下是TOP5景点的好评评论，提炼8~12个共性成功因子。

    【TOP5】{chr(10).join(spot_info)}
    【好评评论】{chr(10).join(all_pos[:60])}

    每个因子必须是完整短句，如"历史文化氛围浓厚令游客沉浸其中"。

    请严格JSON输出：
    {{"factors": ["因子1", "因子2", "因子3", "因子4", "因子5", "因子6", "因子7", "因子8"]}}"""

            ai_text = self._call_ai(prompt, max_tokens=800)
            result = []
            if ai_text:
                try:
                    json_text = self._extract_json_text(ai_text)
                    if json_text:
                        parsed = json.loads(json_text)
                        result = [f for f in parsed.get('factors', []) if len(f.strip()) >= 4]
                except Exception as e:
                    print(f"[WARNING] 成功因子解析失败: {e}")
                    result = self._fallback_success_factors(rankings)
            else:
                result = self._fallback_success_factors(rankings)

            if result:
                self._cache[cache_key] = result
            return result

    def _fallback_success_factors(self, rankings):
        """AI不可用时从jieba提取短语作为兜底"""
        all_text=''
        for r in rankings:
            spot=r['spot_name']
            pos_comments=self._cache['comments_by_spot_sentiment'].get(spot,{}).get('positive',[])
            all_text+=' '.join(pos_comments[:30])
        phrases=jieba.analyse.textrank(all_text,topK=15,withWeight=False)
        return [p for p in phrases if len(p)>=3 and p not in self.stop_words
                and not any(p in name for name in self._spot_names_set)][:10]

    # ================================================================
    # 词云
    # ================================================================

    def get_wordcloud_data(self, spot_name=None, sentiment_level=None):
        cache_key=self._get_cache_key('wc',spot_name,sentiment_level)
        if cache_key in self._cache:
            return self._cache[cache_key]
        mask=pd.Series([True]*len(self.df),index=self.df.index)
        if spot_name:
            mask&=(self.df['spot_name']==spot_name)
        if sentiment_level:
            lo,hi=SENTIMENT_RANGES.get(sentiment_level,(1,5))
            mask&=(self.df['sentiment_score']>=lo)&(self.df['sentiment_score']<=hi)
        text=' '.join(self.df[mask]['comment'].tolist())
        if not text: return []
        freq=self._simple_word_freq(text,top_n=80)
        result=[{'name':w,'value':c} for w,c in freq]
        self._cache[cache_key]=result
        return result

    # ================================================================
    # 景点详情
    # ================================================================

    def get_spot_detail(self, spot_name):
        spot_df=self.df[self.df['spot_name']==spot_name]
        if spot_df.empty: return None
        dist=self._cache.get('score_dist_by_spot',{}).get(spot_name,{})
        if not dist:
            raw=spot_df['sentiment_score'].value_counts().to_dict()
            dist={int(i):int(raw.get(i,0)) for i in range(1,6)}
        detail={
            'name':               spot_name,
            'total_comments':     int(len(spot_df)),
            'avg_score':          round(float(spot_df['sentiment_score'].mean()),2),
            'score_distribution': dist,
            'positive_rate':      round(float((spot_df['sentiment_score']>=4).mean()*100),1),
            'negative_rate':      round(float((spot_df['sentiment_score']<=2).mean()*100),1),
        }
        detail['wordcloud']       =self.get_wordcloud_data(spot_name)
        detail['competitiveness'] =self._analyze_competitiveness(spot_name)
        if 'date' in spot_df.columns and spot_df['date'].notna().any():
            detail['trend']=self._calculate_trend(spot_df)
        detail['travel_plan']=self._generate_basic_plan(spot_name,detail)
        return detail

    def _calculate_trend(self, spot_df):
        df2=spot_df.dropna(subset=['date']).copy()
        if df2.empty: return None
        df2['month']=df2['date'].dt.to_period('M')
        m=df2.groupby('month').agg(count=('comment','count'),avg_score=('sentiment_score','mean')).reset_index()
        m['month']=m['month'].astype(str)
        m['avg_score']=m['avg_score'].round(2)
        return m.to_dict('records')

    def _analyze_competitiveness(self, spot_name):
        all_s=self._cache['spot_stats']
        row=all_s[all_s['spot_name']==spot_name]
        if row.empty: return None
        row=row.iloc[0]; total=len(all_s)
        rc=int((all_s['comment_count']>row['comment_count']).sum()+1)
        rs=int((all_s['avg_score']>row['avg_score']).sum()+1)
        rp=int((all_s['positive_rate']>row['positive_rate']).sum()+1)
        return {
            'comment_rank':f"{rc}/{total}",'score_rank':f"{rs}/{total}",'positive_rank':f"{rp}/{total}",
            'percentile_comment':round((1-rc/total)*100,1),
            'percentile_score':round((1-rs/total)*100,1),
            'percentile_positive':round((1-rp/total)*100,1)
        }

    def _determine_spot_type(self, comments_text):
        scores=defaultdict(int)
        for stype,tkws in SPOT_TYPE_KEYWORDS.items():
            for kw in tkws: scores[stype]+=comments_text.count(kw)
        return max(scores,key=scores.get) if scores else 'entertainment'

    def _generate_basic_plan(self, spot_name, detail):
        spot_df=self.df[self.df['spot_name']==spot_name]
        all_text=' '.join(spot_df['comment'].tolist())
        spot_type=self._determine_spot_type(all_text)
        template=OPERATION_TEMPLATES.get(spot_type,OPERATION_TEMPLATES['entertainment'])
        return {'spot_type':template['name'],'operation_strategies':template['strategies'],
                'positive_rate':detail['positive_rate'],'negative_rate':detail['negative_rate'],'avg_score':detail['avg_score']}

    # ================================================================
    # 其余 API
    # ================================================================

    def get_overview(self):
        dist={int(k):int(v) for k,v in self.df['sentiment_score'].value_counts().items()}
        for i in range(1,6): dist.setdefault(i,0)
        return {
            'total_comments':    int(len(self.df)),
            'total_spots':       int(self.df['spot_name'].nunique()),
            'avg_score':         round(float(self.df['sentiment_score'].mean()),2),
            'score_distribution':dict(sorted(dist.items())),
            'spots_list':        sorted(self.df['spot_name'].unique().tolist()),
            'sentiment_summary': {
                'positive':int((self.df['sentiment_score']>=4).sum()),
                'neutral': int((self.df['sentiment_score']==3).sum()),
                'negative':int((self.df['sentiment_score']<=2).sum())
            }
        }

    def get_spot_rankings(self, top_n=20):
        stats=self._cache['spot_stats'].head(top_n)
        return [{'spot_name':row['spot_name'],'comment_count':int(row['comment_count']),
                 'avg_score':float(row['avg_score']),'score_std':float(row['score_std']),
                 'positive_rate':float(row['positive_rate']),'negative_rate':float(row['negative_rate']),
                 'positive_count':int(row['positive_count']),'negative_count':int(row['negative_count']),
                 'heat_index':float(row['heat_index'])} for _,row in stats.iterrows()]

    def get_sentiment_distribution(self):
        return self._cache.get('score_dist_by_spot',{})

    def get_comparison_data(self, spot_names):
        result=[]
        for name in spot_names:
            sdf=self.df[self.df['spot_name']==name]
            if sdf.empty: continue
            dist=self._cache.get('score_dist_by_spot',{}).get(name,{})
            if not dist:
                raw=sdf['sentiment_score'].value_counts().to_dict()
                dist={int(i):int(raw.get(i,0)) for i in range(1,6)}
            result.append({'name':name,'comment_count':int(len(sdf)),
                           'avg_score':round(float(sdf['sentiment_score'].mean()),2),
                           'positive_rate':round(float((sdf['sentiment_score']>=4).mean()*100),1),
                           'negative_rate':round(float((sdf['sentiment_score']<=2).mean()*100),1),
                           'score_distribution':dist})
        return result

    def get_overview_with_change(self):
        """带变化量的总览数据（按周对比，更平滑）"""
        overview = self.get_overview()

        if 'date' not in self.df.columns or self.df['date'].isna().all():
            overview['changes'] = None
            return overview

        df = self.df.dropna(subset=['date']).copy()
        if df.empty:
            overview['changes'] = None
            return overview

        max_date = df['date'].max()

        # 近7天 vs 之前7天
        recent_start = max_date - pd.Timedelta(days=6)  # 含max当天，共7天
        prev_end = recent_start - pd.Timedelta(days=1)
        prev_start = prev_end - pd.Timedelta(days=6)

        recent_df = df[df['date'] >= recent_start]
        prev_df = df[(df['date'] >= prev_start) & (df['date'] <= prev_end)]

        # 近7天新增
        recent_count = len(recent_df)
        prev_count = len(prev_df)

        # 评分（用平均评分对比）
        if not recent_df.empty:
            recent_avg = round(recent_df['sentiment_score'].mean(), 2)
        else:
            recent_avg = 0

        if not prev_df.empty:
            prev_avg = round(prev_df['sentiment_score'].mean(), 2)
        else:
            prev_avg = recent_avg

        score_change = round(recent_avg - prev_avg, 2)

        # 好评率
        if not recent_df.empty:
            recent_pos_rate = round((recent_df['sentiment_score'] >= 4).mean() * 100, 1)
        else:
            recent_pos_rate = 0

        if not prev_df.empty:
            prev_pos_rate = round((prev_df['sentiment_score'] >= 4).mean() * 100, 1)
        else:
            prev_pos_rate = recent_pos_rate

        pos_rate_change = round(recent_pos_rate - prev_pos_rate, 1)

        overview['changes'] = {
            'recent_count': recent_count,  # 近7天新增总数
            'recent_avg_score': recent_avg,  # 近7天平均评分
            'recent_pos_rate': recent_pos_rate,  # 近7天好评率
            'score_change': score_change,  # 评分变化
            'pos_rate_change': pos_rate_change,  # 好评率变化
            'date_range': f"{recent_start.strftime('%m-%d')} ~ {max_date.strftime('%m-%d')}"
        }

        return overview
    def get_heat_map_data(self):
        return [{'spot_name':row['spot_name'],'comment_count':int(row['comment_count']),
                 'avg_score':float(row['avg_score']),'positive_rate':float(row['positive_rate']),
                 'heat':float(row['heat_index'])} for _,row in self._cache['spot_stats'].iterrows()]

    def get_trend_analysis(self):
        if 'date' not in self.df.columns or self.df['date'].isna().all(): return None
        df2=self.df.dropna(subset=['date']).copy()
        df2['month']=df2['date'].dt.to_period('M')
        m=df2.groupby('month').agg(comment_count=('comment','count'),avg_score=('sentiment_score','mean'),
                                    positive_rate=('sentiment_score',lambda x:(x>=4).mean()*100)).reset_index()
        m['month']=m['month'].astype(str)
        m['avg_score']=m['avg_score'].round(2)
        m['positive_rate']=m['positive_rate'].round(1)
        return m.to_dict('records')

    def get_spot_monthly_trend(self, spot_name, start_date=None, end_date=None):
        """获取单个景点的月度趋势（自动补齐空月份）"""
        spot_df = self.df[self.df['spot_name'] == spot_name].copy()
        if spot_df.empty or 'date' not in spot_df.columns:
            return None

        df2 = spot_df.dropna(subset=['date']).copy()
        if df2.empty:
            return None

        # 时间范围筛选
        if start_date:
            df2 = df2[df2['date'] >= pd.to_datetime(start_date)]
        if end_date:
            df2 = df2[df2['date'] <= pd.to_datetime(end_date)]
        if df2.empty:
            return None

        df2['month'] = df2['date'].dt.to_period('M')

        # 按月聚合
        monthly = df2.groupby('month').agg(
            count=('comment', 'count'),
            avg_score=('sentiment_score', 'mean'),
            positive_rate=('sentiment_score', lambda x: round((x >= 4).mean() * 100, 1))
        ).reset_index()

        # ✨ 补齐空月份
        if not monthly.empty:
            # 生成完整的月份范围
            if start_date:
                start_period = pd.Period(pd.to_datetime(start_date), freq='M')
            else:
                start_period = monthly['month'].min()

            if end_date:
                end_period = pd.Period(pd.to_datetime(end_date), freq='M')
            else:
                end_period = monthly['month'].max()

            # 完整月份序列
            all_months = pd.period_range(start=start_period, end=end_period, freq='M')
            all_months_df = pd.DataFrame({'month': all_months})

            # 合并，缺失的月份用默认值填充
            monthly = all_months_df.merge(monthly, on='month', how='left')
            monthly['count'] = monthly['count'].fillna(0).astype(int)
            monthly['avg_score'] = monthly['avg_score'].fillna(0).round(2)
            monthly['positive_rate'] = monthly['positive_rate'].fillna(0)

        monthly['month'] = monthly['month'].astype(str)

        # 标注峰值和转折点
        if len(monthly) > 0:
            # 只在有数据的月份中找峰值
            non_zero = monthly[monthly['count'] > 0]
            if not non_zero.empty:
                max_idx = non_zero['count'].idxmax()
                monthly['is_peak'] = False
                monthly.loc[max_idx, 'is_peak'] = True
            else:
                monthly['is_peak'] = False

            monthly['is_turning'] = False
            counts = monthly['count'].tolist()
            for i in range(1, len(counts) - 1):
                # 跳过 0 值附近的转折
                if counts[i] == 0:
                    continue
                if (counts[i] > counts[i - 1] and counts[i] > counts[i + 1]) or \
                        (counts[i] < counts[i - 1] and counts[i] < counts[i + 1] and counts[i - 1] > 0 and counts[
                            i + 1] > 0):
                    monthly.loc[monthly.index[i], 'is_turning'] = True

        return monthly.to_dict('records')

    def get_heat_by_period(self, days=None, start_date=None, end_date=None):
        """按时间范围计算热度"""
        df_filtered = self.df.copy()

        if 'date' in df_filtered.columns:
            if start_date and end_date:
                df_filtered = df_filtered[
                    (df_filtered['date'] >= pd.to_datetime(start_date)) &
                    (df_filtered['date'] <= pd.to_datetime(end_date))
                ]
            elif days:
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
                df_filtered = df_filtered[df_filtered['date'] >= cutoff]

        if df_filtered.empty:
            df_filtered = self.df

        stats = df_filtered.groupby('spot_name').agg(
            comment_count=('comment', 'count'),
            avg_score=('sentiment_score', 'mean'),
            positive_count=('sentiment_score', lambda x: (x >= 4).sum()),
        ).reset_index()

        stats['positive_rate'] = (stats['positive_count'] / stats['comment_count'] * 100).round(1)
        max_c = stats['comment_count'].max() if stats['comment_count'].max() > 0 else 1
        stats['heat_index'] = (
            stats['comment_count'] / max_c * 40 +
            stats['avg_score'] / 5 * 35 +
            stats['positive_rate'] / 100 * 25
        ).round(1)
        stats['avg_score'] = stats['avg_score'].round(2)
        stats = stats.sort_values('heat_index', ascending=False)

        return [
            {
                'spot_name': row['spot_name'],
                'comment_count': int(row['comment_count']),
                'avg_score': float(row['avg_score']),
                'positive_rate': float(row['positive_rate']),
                'heat': float(row['heat_index'])
            }
            for _, row in stats.iterrows()
        ]

    def get_keyword_sentiment_heatmap(self, spot_name=None, top_n=60):
        """
        功能一：情感-关键词关联热力图（v2: 增加好评率字段）
        返回字段：keyword、frequency、avg_score、positive_rate、sentiment_level
        """
        cache_key = self._get_cache_key('keyword_sentiment_heatmap_v2', spot_name, top_n)
        if cache_key in self._cache:
            return self._cache[cache_key]

        df = self.df.copy()
        if spot_name and spot_name not in ("全部景点", "全部", "all"):
            df = df[df["spot_name"] == spot_name]
        if df.empty:
            return []

        invalid_words = {
            "令人", "非常", "特别", "真的", "比较", "感觉", "觉得", "还是", "可以",
            "不错", "很好", "好看", "漂亮", "值得", "推荐", "一定", "必须", "强烈",
            "一个", "这个", "那个", "这里", "那里", "里面", "外面", "时候", "方面",
            "游客", "景点", "景区", "旅游", "地方", "体验", "参观", "游览", "进去",
            "整体", "还有", "就是", "因为", "所以", "但是", "不过", "如果", "虽然",
            "很多", "一些", "一下", "完全", "十分", "超级", "太多", "太大", "太好",
            "不错的", "真是", "简直", "居然", "竟然", "反正", "总之", "哈哈", "嗯嗯",
            "来说", "个人", "总体", "还行", "一下子", "真的很", "特别是", "比较好",
            "值得一看", "强烈推荐", "精彩", "精彩绝伦", "震撼", "很强", "很美", "很棒"
        }

        valuable_keywords = {
            "夜景", "灯光", "演出", "表演", "汉服", "建筑", "历史", "文化", "讲解",
            "服务", "排队", "人多", "拥挤", "门票", "价格", "停车", "交通", "卫生",
            "厕所", "管理", "商业化", "消费", "餐饮", "美食", "环境", "设施", "路线",
            "秩序", "拍照", "打卡", "文创", "预约", "讲解员", "工作人员", "博物馆",
            "不倒翁", "兵马俑", "城墙", "大唐", "芙蓉园", "大雁塔", "华清宫",
            "排队时间", "服务态度", "门票价格", "性价比", "停车场", "卫生条件"
        }

        valuable_contains = [
            "排队", "门票", "服务", "交通", "停车", "卫生", "管理", "价格", "演出", "灯光",
            "夜景", "讲解", "厕所", "拥挤", "人多", "商业", "消费", "预约", "路线", "秩序",
            "设施", "餐饮", "文创", "拍照", "打卡", "汉服", "历史", "文化", "建筑"
        ]

        word_scores = defaultdict(list)
        for _, row in df.iterrows():
            comment = str(row.get("comment", ""))
            try:
                score = float(row.get("sentiment_score", 3))
            except Exception:
                score = 3.0

            for w in jieba.lcut(comment):
                w = w.strip()
                if len(w) < 2:
                    continue
                if w.isdigit() or re.match(r'^[a-zA-Z]{1,3}$', w):
                    continue
                if w in invalid_words:
                    continue

                is_valuable = (
                        w in valuable_keywords
                        or any(k in w for k in valuable_contains)
                        or len(w) >= 3
                )

                if (not is_valuable) and hasattr(self, "stop_words") and w in self.stop_words:
                    continue

                if hasattr(self, "_spot_names_set"):
                    if w in self._spot_names_set:
                        continue
                    if (not is_valuable) and any(w in name for name in self._spot_names_set):
                        continue

                if is_valuable:
                    word_scores[w].append(score)

        result = []
        for word, scores in word_scores.items():
            freq = len(scores)
            if freq < 3:
                continue
            avg_score = sum(scores) / len(scores)
            # ✨ 新增：好评率（评分≥4 的占比）
            pos_count = sum(1 for s in scores if s >= 4)
            positive_rate = round(pos_count / freq * 100, 1)

            # 用好评率判定情感等级（比 avg_score 更准）
            if positive_rate >= 70:
                level = "高满意"
            elif positive_rate >= 40:
                level = "中性"
            else:
                level = "低满意"

            result.append({
                "keyword": word,
                "frequency": int(freq),
                "avg_score": round(float(avg_score), 2),
                "positive_rate": positive_rate,
                "sentiment_level": level
            })

        # 排序：按词频 + 偏离中性程度
        result = sorted(
            result,
            key=lambda x: (x["frequency"], abs(x["positive_rate"] - 50)),
            reverse=True
        )[:top_n]
        self._cache[cache_key] = result
        return result

    def get_negative_factor_model(self, spot_name=None, top_n=10):
        """
        功能二：失望原因诊断（槽点关键词 → 情感分 线性回归模型）

        模型：sentiment_score = intercept + β1X1 + β2X2 + ... + ε
        X：每条评论是否出现某类槽点关键词，出现=1，未出现=0。
        β：对应槽点对评分的影响系数，负数越大表示破坏力越强。
        """
        cache_key = self._get_cache_key('negative_factor_model_v1', spot_name, top_n, len(self.df))
        if cache_key in self._cache:
            return self._cache[cache_key]

        df = self.df.copy()
        if spot_name and spot_name not in ("全部景点", "全部", "all"):
            df = df[df["spot_name"] == spot_name]
        if df.empty or len(df) < 8:
            return {"summary": {"sample_size": int(len(df)), "avg_score": 0, "intercept": 0}, "items": []}

        factor_defs = [
            {"factor": "排队等待", "category": "体验类", "keywords": ["排队", "等", "等待", "队伍", "排很久", "排长队"],
             "advice": "优化排队动线，增加分流通道或预约限流。"},
            {"factor": "人多拥挤", "category": "体验类", "keywords": ["人多", "拥挤", "挤", "人山人海", "游客太多"],
             "advice": "设置错峰游览、限流预警和分时预约。"},
            {"factor": "价格/门票", "category": "价格类",
             "keywords": ["贵", "门票贵", "门票", "不值", "性价比低", "收费", "价格"],
             "advice": "优化票价说明，推出组合票或差异化优惠。"},
            {"factor": "服务态度", "category": "服务类",
             "keywords": ["服务差", "态度差", "态度", "工作人员", "冷漠", "不热情", "服务"],
             "advice": "加强员工培训，建立服务评价反馈机制。"},
            {"factor": "交通停车", "category": "交通类",
             "keywords": ["远", "交通", "停车", "停车场", "不好找", "打车", "堵车"],
             "advice": "完善交通指引、停车信息和接驳服务。"},
            {"factor": "环境卫生", "category": "环境类",
             "keywords": ["脏", "乱", "卫生", "厕所", "垃圾", "环境差", "异味"],
             "advice": "提高保洁频次，重点改善厕所和公共区域卫生。"},
            {"factor": "商业化", "category": "消费类",
             "keywords": ["商业化", "强制消费", "宰客", "消费", "小摊", "推销"],
             "advice": "规范商户经营，减少过度商业化对体验的干扰。"},
            {"factor": "设施管理", "category": "管理类",
             "keywords": ["设施", "老化", "管理", "混乱", "秩序", "指示牌", "路线"],
             "advice": "完善导览标识，维护基础设施，强化现场秩序管理。"},
            {"factor": "天气体感", "category": "环境类", "keywords": ["热", "晒", "冷", "下雨", "天气", "遮阳"],
             "advice": "增加遮阳避雨设施，优化高温/雨天游览提示。"}
        ]

        X_rows, y_vals = [], []
        comments = df["comment"].astype(str).tolist()
        scores = pd.to_numeric(df["sentiment_score"], errors="coerce").fillna(3).clip(1, 5).astype(float).tolist()

        for comment, score in zip(comments, scores):
            X_rows.append([1 if any(k in comment for k in f["keywords"]) else 0 for f in factor_defs])
            y_vals.append(float(score))

        X = np.array(X_rows, dtype=float)
        y = np.array(y_vals, dtype=float)

        # 删除完全没有出现过的槽点列，避免无效系数干扰
        valid_idx = [i for i in range(X.shape[1]) if X[:, i].sum() > 0]
        if not valid_idx:
            return {"summary": {"sample_size": int(len(df)), "avg_score": round(float(np.mean(y)), 2),
                                "intercept": round(float(np.mean(y)), 2)}, "items": []}

        X_valid = X[:, valid_idx]
        try:
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
            model.fit(X_valid, y)
            coefs = model.coef_
            intercept = float(model.intercept_)
        except Exception:
            # sklearn 不可用时使用最小二乘兜底
            X_design = np.column_stack([np.ones(len(X_valid)), X_valid])
            beta = np.linalg.lstsq(X_design, y, rcond=None)[0]
            intercept = float(beta[0])
            coefs = beta[1:]

        items = []
        for local_i, original_i in enumerate(valid_idx):
            f = factor_defs[original_i]
            coef = float(coefs[local_i])
            count = int(X[:, original_i].sum())
            occurrence_rate = count / len(df)
            negative_effect = max(0.0, -coef)
            impact = negative_effect * occurrence_rate
            # 估算：若该问题明显改善，可带来的平均分提升空间
            estimated_gain = impact

            items.append({
                "factor": f["factor"],
                "category": f["category"],
                "keywords": "、".join(f["keywords"][:4]),
                "coef": round(coef, 3),
                "count": count,
                "occurrence_rate": round(occurrence_rate, 3),
                "occurrence_pct": round(occurrence_rate * 100, 1),
                "impact": round(impact, 3),
                "estimated_gain": round(estimated_gain, 3),
                "advice": f["advice"],
                "direction": "负向" if coef < 0 else "非负向"
            })

        items = sorted(items, key=lambda x: (x["impact"], x["count"]), reverse=True)
        if top_n:
            items = items[:top_n]

        for idx, item in enumerate(items, 1):
            item["priority"] = f"P{idx - 1}" if idx <= 3 else f"P{idx}"

        result = {
            "summary": {
                "spot_name": spot_name or "全部景点",
                "sample_size": int(len(df)),
                "avg_score": round(float(np.mean(y)), 2),
                "intercept": round(float(intercept), 3),
                "model": "LinearRegression"
            },
            "items": items
        }
        self._cache[cache_key] = result
        return result

    def get_day_plan_data(self, spot_names):
        """为一日游规划准备各景点的数据"""
        result = []
        for name in spot_names:
            spot_df = self.df[self.df['spot_name'] == name]
            if spot_df.empty:
                continue

            avg_score = round(float(spot_df['sentiment_score'].mean()), 2)
            positive_rate = round(float((spot_df['sentiment_score'] >= 4).mean() * 100), 1)
            total = len(spot_df)

            # 获取AI关键词
            kw = self.get_ai_keywords(name)
            pos_phrases = kw.get('positive', [])[:4]
            neg_phrases = kw.get('negative', [])[:4]

            # 获取失望原因
            neg_model = self.get_negative_factor_model(spot_name=name, top_n=3)
            neg_factors = []
            if neg_model and neg_model.get('items'):
                neg_factors = [
                    {'factor': item['factor'], 'advice': item['advice'], 'impact': item['impact']}
                    for item in neg_model['items'][:3]
                    if item.get('impact', 0) > 0
                ]

            result.append({
                'name': name,
                'avg_score': avg_score,
                'positive_rate': positive_rate,
                'total_comments': total,
                'positive_phrases': pos_phrases,
                'negative_phrases': neg_phrases,
                'negative_factors': neg_factors
            })
        return result

    def get_ai_day_plan(self, spot_names, duration='一日游', start_time='08:30', transport='地铁+步行',
                        season='不限'):
        """AI生成旅游规划"""
        engine = getattr(self, '_current_engine', AI_DEFAULT_ENGINE)
        cache_key = self._get_cache_key('day_plan_v2', ','.join(sorted(spot_names)), duration, start_time,
                                        transport, season, engine)
        if cache_key in self._cache:
            return self._cache[cache_key]

        spots_data = self.get_day_plan_data(spot_names)
        if not spots_data:
            return {'error': '未找到景点数据'}

        spots_info = []
        for s in spots_data:
            info = f"""【{s['name']}】评分{s['avg_score']}/5，好评率{s['positive_rate']}%，{s['total_comments']}条评论"""
            if s['positive_phrases']:
                info += f"\n  游客好评：{'；'.join(s['positive_phrases'][:3])}"
            if s['negative_phrases']:
                info += f"\n  游客差评：{'；'.join(s['negative_phrases'][:3])}"
            if s['negative_factors']:
                factors_str = '；'.join([f"{f['factor']}（影响分{f['impact']}）" for f in s['negative_factors']])
                info += f"\n  失望原因诊断：{factors_str}"
            spots_info.append(info)

        # 获取月度趋势数据，分析淡旺季 + 评分变化
        best_months_info = []
        for s in spots_data:
            trend = self.get_spot_monthly_trend(s['name'])
            if not trend:
                continue

            # 只看有数据的月份
            non_zero = [t for t in trend if t.get('count', 0) > 0]
            if not non_zero:
                continue

            # 按月份分组聚合（不分年份）
            from collections import defaultdict
            month_stats = defaultdict(lambda: {'count': 0, 'score_sum': 0, 'score_n': 0, 'pos_sum': 0, 'pos_n': 0})
            for t in non_zero:
                ym = t['month']
                m = ym.split('-')[1]
                month_stats[m]['count'] += t.get('count', 0)
                if t.get('avg_score', 0) > 0:
                    month_stats[m]['score_sum'] += t['avg_score']
                    month_stats[m]['score_n'] += 1
                if t.get('positive_rate', 0) > 0:
                    month_stats[m]['pos_sum'] += t['positive_rate']
                    month_stats[m]['pos_n'] += 1

            # 计算每月聚合值
            month_summary = []
            for m, stats in month_stats.items():
                avg_score = round(stats['score_sum'] / stats['score_n'], 2) if stats['score_n'] > 0 else 0
                pos_rate = round(stats['pos_sum'] / stats['pos_n'], 1) if stats['pos_n'] > 0 else 0
                month_summary.append({
                    'month': m,
                    'count': stats['count'],
                    'avg_score': avg_score,
                    'pos_rate': pos_rate
                })

            # 按评论量排序
            by_count = sorted(month_summary, key=lambda x: -x['count'])
            # 按评分排序
            by_score = sorted([m for m in month_summary if m['avg_score'] > 0], key=lambda x: -x['avg_score'])

            if not by_count:
                continue

            # 旺季：评论量前 3
            peak = by_count[:3]
            # 淡季：评论量后 3
            off = by_count[-3:] if len(by_count) >= 4 else []
            # 体验最佳：评分前 2
            best_exp = by_score[:2] if by_score else []

            # 拼接详细信息
            peak_detail = '、'.join(
                [f"{p['month']}月(评论{p['count']}条,评分{p['avg_score']},好评{p['pos_rate']}%)" for p in peak])
            off_detail = '、'.join(
                [f"{o['month']}月(评论{o['count']}条,评分{o['avg_score']},好评{o['pos_rate']}%)" for o in
                 off]) if off else '无明显淡季'
            best_detail = '、'.join([f"{b['month']}月(评分{b['avg_score']})" for b in best_exp]) if best_exp else '无显著差异'

            best_months_info.append(
                f"【{s['name']}】\n"
                f"  · 🌺 旺季（评论量高）：{peak_detail}\n"
                f"  · 🍃 淡季（评论量低）：{off_detail}\n"
                f"  · ⭐ 体验最佳月份（评分高）：{best_detail}"
            )

        best_months_str = '\n\n'.join(best_months_info) if best_months_info else '暂无月度数据'
        # 季节偏好提示
        season_prompt = ''
        if season == '旺季':
            season_prompt = """
【⚠️ 重要：用户选择了"旺季出行"】
- 必须在行程开头明确告知用户：哪几个月是这些景点的旺季（基于上方分析数据）
- 旺季优点：氛围热闹、配套服务完善、夜景灯光秀更精彩
- 旺季提醒：必须提前预约、人流量大、住宿和门票价格上涨
- 应对策略要重点提及如何避免长时间排队、错峰游览技巧"""
        elif season == '淡季':
            season_prompt = """
【⚠️ 重要：用户选择了"淡季出行"】
- 必须在行程开头明确告知用户：哪几个月是这些景点的淡季（基于上方分析数据）
- 淡季优点：游客稀少、拍照出片、性价比高、深度体验
- 淡季提醒：部分景点表演可能减少、部分配套商家营业时间缩短
- 推荐用户深度游览，慢节奏体验"""
        else:
            season_prompt = """
【季节偏好：用户未指定】
- 简要提及各景点的旺季和淡季月份即可"""

        prompt = f"""你是西安本地资深导游，拥有10年以上带团经验。请为游客规划行程。

【游客需求】
- 游览类型：{duration}
- 出发时间：{start_time}
- 交通方式偏好：{transport}
- 季节偏好：{season}
- 要去的景点（共{len(spot_names)}个）：{'、'.join(spot_names)}

【重要提示】
- 游客选择的是「{duration}」，请严格按照{duration}的时间跨度来规划
- 如果是"两日游"，必须规划两天的行程，包含第一天晚上的住宿建议
- 如果是"半日游"，行程控制在4-5小时内
- 如果你认为选择的景点数量和游览时长不匹配，请在开头明确说明并给出建议

【各景点数据（基于携程{sum(s['total_comments'] for s in spots_data)}条真实评论）】
{chr(10).join(spots_info)}

【各景点淡旺季分析（基于月度热度数据）】
{best_months_str}

{season_prompt}

请用中文、markdown格式输出：

## 一、行程总览
（总结本次行程的核心亮点，必须包含旺季/淡季提醒）

## 二、推荐游览顺序
（考虑地理位置、最佳游览时段、避开人流高峰，给出顺序并解释原因）

## 三、详细时间安排
（从{start_time}开始，精确到每半小时，包含交通耗时和用餐休息。如果是两日游要分Day1和Day2）

## 四、各景点攻略
（每个景点：推荐时长、必看亮点、避坑提醒、实用Tips）

## 五、交通指南
（景点之间的{transport}具体路线、耗时、费用）

## 六、餐饮推荐
（沿途的特色美食和餐厅推荐）

## 七、预估费用
（门票+交通+餐饮分项列出）

## 八、最佳出行时间
（基于淡旺季数据，结合用户的{season}偏好，给出具体的月份建议和理由）

## 九、注意事项
（基于差评数据的针对性提醒，包含季节性提醒）"""

        ai_text = self._call_ai(prompt, max_tokens=3000)
        engine_label = self._get_engine_label()

        if ai_text:
            result = {'status': 'success', 'content': ai_text, 'source': 'ai', 'engine': engine_label}
        else:
            result = {'status': 'fallback', 'content': '## AI规划生成失败\n\n请稍后重试，或切换AI引擎。',
                      'source': 'local', 'engine': '本地'}

        self._cache[cache_key] = result
        return result



    # ===================== 动态时序情感词云 =====================
    def get_dynamic_sentiment_time_wordcloud(self, spot_name=None):
        try:
            # ✅ 在函数内部筛选，完全不动 self.df
            if spot_name:
                df = self.df[self.df['spot_name'] == spot_name].copy()
            else:
                df = self.df

            # 后续所有 self.df 替换为局部变量 df
            date_col = 'date' if 'date' in df.columns else (
                'comment_date' if 'comment_date' in df.columns else '评论时间')
            score_col = 'sentiment_score' if 'sentiment_score' in df.columns else '评分'
            text_col = 'comment' if 'comment' in df.columns else '评论内容'

            df_work = df.dropna(subset=[date_col, text_col]).copy()
            if df_work.empty:
                return {"情感词云数据": {"global_positive": []},
                        "时序维度": {"工作日/节假日": {}}}

            df_work['date_parsed'] = pd.to_datetime(df_work[date_col], errors='coerce')
            df_work = df_work.dropna(subset=['date_parsed'])
            df_work['week_type'] = df_work['date_parsed'].dt.weekday.apply(
                lambda x: "节假日" if x >= 5 else "工作日"
            )

            result = {
                "情感词云数据": {"global_positive": []},
                "时序维度": {"工作日/节假日": {}}
            }

            # 全局正向词云
            good_df = df_work[df_work[score_col] >= 4]
            if not good_df.empty:
                text = " ".join(good_df[text_col].astype(str))
                freq = self._simple_word_freq(text, 50)
                result["情感词云数据"]["global_positive"] = [
                    {"name": w, "value": c} for w, c in freq
                ]

            # 工作日/节假日
            all_scene_words = {}
            for period in ["工作日", "节假日"]:
                period_df = df_work[df_work['week_type'] == period]
                result["时序维度"]["工作日/节假日"][period] = {
                    "positive": [], "negative": []
                }
                for sentiment, rng in [("positive", (4, 5)), ("negative", (0, 2))]:
                    sent_df = period_df[
                        (period_df[score_col] >= rng[0]) &
                        (period_df[score_col] <= rng[1])
                        ]
                    if not sent_df.empty:
                        text = " ".join(sent_df[text_col].astype(str))
                        freq = self._simple_word_freq(text, 60)
                        word_list = [{"name": w, "value": c} for w, c in freq]
                        all_scene_words[period + "_" + sentiment] = set(
                            [w for w, _ in freq]
                        )
                        result["时序维度"]["工作日/节假日"][period][sentiment] = word_list

            # 通用词过滤
            if len(all_scene_words) == 4:
                common_words = set.intersection(*all_scene_words.values())
                common_words.update({
                    "风景", "门票", "服务", "环境", "体验", "感觉", "不错",
                    "有点", "真的", "非常", "还是", "就是", "可以", "没有"
                })
                for period in ["工作日", "节假日"]:
                    for sentiment in ["positive", "negative"]:
                        filtered = [
                            w for w in result["时序维度"]["工作日/节假日"][period][sentiment]
                            if w['name'] not in common_words
                        ]
                        result["时序维度"]["工作日/节假日"][period][sentiment] = filtered[:30]

            return result

        except Exception as e:
            return {
                "情感词云数据": {"global_positive": []},
                "时序维度": {"工作日/节假日": {}},
                "error": str(e)
            }
    # ================================================================
    # 工作日 vs 节假日 关键词差异分析
    # ================================================================
    def get_weekday_holiday_diff(self, spot_name=None):
        """分析工作日和节假日的关键词差异"""
        cache_key = self._get_cache_key('weekday_holiday_diff_v1', spot_name)
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            date_col = 'date' if 'date' in self.df.columns else 'comment_date'
            score_col = 'sentiment_score'
            text_col = 'comment'
            spot_col = 'spot_name'

            # 局部筛选
            if spot_name:
                df = self.df[self.df[spot_col] == spot_name].copy()
            else:
                df = self.df.copy()

            df = df.dropna(subset=[date_col, text_col])
            if df.empty:
                return {'positive': self._empty_diff(), 'negative': self._empty_diff()}

            # 解析日期
            df['_date'] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=['_date'])
            df['_is_holiday'] = df['_date'].dt.weekday >= 5

            result = {}

            for sentiment, score_range in [('positive', (4, 5)), ('negative', (0, 2))]:
                sent_df = df[(df[score_col] >= score_range[0]) & (df[score_col] <= score_range[1])]

                workday_df = sent_df[~sent_df['_is_holiday']]
                holiday_df = sent_df[sent_df['_is_holiday']]

                if workday_df.empty or holiday_df.empty:
                    result[sentiment] = self._empty_diff()
                    continue

                # 词频统计
                workday_freq = self._count_words(' '.join(workday_df[text_col].astype(str)), top_n=200)
                holiday_freq = self._count_words(' '.join(holiday_df[text_col].astype(str)), top_n=200)

                workday_dict = dict(workday_freq)
                holiday_dict = dict(holiday_freq)
                all_words = set(workday_dict.keys()) | set(holiday_dict.keys())

                # 计算差异度
                workday_total = sum(workday_dict.values()) or 1
                holiday_total = sum(holiday_dict.values()) or 1

                workday_only = []  # 工作日专属
                holiday_only = []  # 节假日专属
                common = []        # 共同高频

                for word in all_words:
                    w_freq = workday_dict.get(word, 0)
                    h_freq = holiday_dict.get(word, 0)
                    total = w_freq + h_freq

                    if total < 5:
                        continue  # 太低频，忽略

                    # 归一化频次（每万词出现次数）
                    w_norm = w_freq / workday_total * 10000
                    h_norm = h_freq / holiday_total * 10000

                    # 差异度
                    diff_score = abs(w_norm - h_norm) / (w_norm + h_norm)

                    if diff_score > 0.6:
                        # 专属词
                        if w_norm > h_norm:
                            workday_only.append({'word': word, 'count': w_freq, 'diff': round(diff_score, 2)})
                        else:
                            holiday_only.append({'word': word, 'count': h_freq, 'diff': round(diff_score, 2)})
                    elif diff_score < 0.3 and w_freq >= 8 and h_freq >= 8:
                        # 共同高频词
                        common.append({'word': word, 'count': w_freq + h_freq})

                # 排序取 TOP 8
                workday_only.sort(key=lambda x: -x['count'])
                holiday_only.sort(key=lambda x: -x['count'])
                common.sort(key=lambda x: -x['count'])

                result[sentiment] = {
                    'workday_only': workday_only[:8],
                    'holiday_only': holiday_only[:8],
                    'common': common[:12]
                }

            self._cache[cache_key] = result
            return result

        except Exception as e:
            print(f"[ERROR] get_weekday_holiday_diff: {e}")
            import traceback
            traceback.print_exc()
            return {'positive': self._empty_diff(), 'negative': self._empty_diff(), 'error': str(e)}

    def _empty_diff(self):
        return {'workday_only': [], 'holiday_only': [], 'common': []}

    def _count_words(self, text, top_n=200):
        """词频统计（复用 _simple_word_freq 但添加更严格过滤）"""
        invalid_words = {
            '风景', '门票', '服务', '环境', '体验', '感觉', '不错', '一般',
            '有点', '真的', '非常', '还是', '就是', '可以', '没有', '但是',
            '所以', '因为', '然后', '觉得', '比较', '特别', '整体', '基本',
            '主要', '地方', '景点', '旅游', '游客', '时间', '里面', '外面',
            '今天', '昨天', '一天', '一次', '一些', '一下', '一直', '一定',
            '我们', '他们', '什么', '怎么', '这里', '那里', '这个', '那个'
        }
        words = jieba.cut(text, cut_all=False)
        counts = Counter()
        for w in words:
            w = w.strip()
            if (len(w) >= 2 and w not in self.stop_words
                    and w not in invalid_words
                    and not w.isdigit()
                    and not re.match(r'^[a-zA-Z]{1,3}$', w)
                    and w not in self._spot_names_set):
                if not any(w in name for name in self._spot_names_set):
                    counts[w] += 1
        return counts.most_common(top_n)
    # ===================== 四维游客画像 =====================
    def get_4d_visitor_portrait(self, spot_name=None):
        """游客画像 + 行为特征画像（关键词驱动，支持单景点筛选）"""
        try:
            score_col = 'sentiment_score' if 'sentiment_score' in self.df.columns else '评分'
            text_col = 'comment' if 'comment' in self.df.columns else '评论内容'
            spot_col = 'spot_name' if 'spot_name' in self.df.columns else '景点名称'

            # 局部筛选，不修改 self.df
            if spot_name:
                df = self.df[self.df[spot_col] == spot_name].copy()
            else:
                df = self.df

            portrait = {
                "游客画像": {},
                "行为特征画像": {},
                "典型客群聚类": {},
                "营销推送建议": [],
                "可视化数据": {}
            }

            if df.empty:
                return portrait

            total_comments = len(df)
            all_text = " ".join(df[text_col].astype(str))

            def calc_percent(keywords):
                scores = {k: sum(all_text.count(kw) for kw in v) for k, v in keywords.items()}
                if total_comments == 0:
                    return {}
                return {k: round(v / total_comments * 100, 1) for k, v in scores.items() if v > 0}

            # ========== 1. 游客画像 ==========
            scene_keywords = {
                "亲子出行": ["带小孩", "带孩子", "带娃", "孩子", "小孩", "小朋友", "宝宝", "亲子", "遛娃", "儿童",
                             "跟孩子", "和孩子", "陪着孩子", "带孩子玩", "亲子游", "一家三口", "有孩子", "带娃出行",
                             "亲子出行", "带宝贝", "和宝宝"],
                "家庭出行": ["全家", "家人", "老人", "一家", "家庭", "老少", "一家老小", "带着家人", "和父母", "和爸妈",
                             "带父母", "陪父母", "全家出游", "家庭出游", "带长辈", "和老人", "三代"],
                "情侣出行": ["情侣", "男朋友", "女朋友", "老公", "老婆", "爱人", "对象", "夫妻", "两人", "两个人",
                             "二人世界", "约会", "和对象", "和男朋友", "和女朋友", "和老公", "和老婆", "情侣游", "蜜月",
                             "小两口", "两口子"],
                "朋友结伴": ["朋友", "同学", "闺蜜", "兄弟", "伙伴", "友人", "和朋友", "和闺蜜", "和兄弟", "结伴",
                             "一起", "组团", "约上", "三五好友", "小伙伴", "死党", "朋友一起", "和朋友一起",
                             "结伴而行"],
                "独自旅行": ["一个人", "独自", "自己", "单人", "孤身", "独行", "单独", "一个人来", "自己来", "独游",
                             "一人", "自个", "一个人旅行", "独自一人", "单人行"]
            }
            consumption_keywords = {
                "网红打卡型": ["拍照", "打卡", "出片", "网红", "滤镜", "好看", "美", "大片", "ins风", "朋友圈", "发圈"],
                "品质体验型": ["体验", "服务", "品质", "舒适", "享受", "氛围", "精致", "高端", "豪华", "贴心"],
                "深度文化型": ["文化", "历史", "讲解", "知识", "古迹", "传统", "博物馆", "文物", "典故", "传说",
                               "底蕴"],
                "性价比优先型": ["便宜", "实惠", "划算", "性价比", "优惠", "团购", "特价", "省钱", "值", "超值", "不贵"]
            }
            tendency_keywords = {
                "深度游览": ["深度", "仔细", "慢慢", "详细", "沉浸", "细品", "慢慢逛", "认真", "细细", "用心", "全程",
                             "完整"],
                "快速浏览": ["快速", "赶时间", "路过", "走马观花", "匆匆", "打卡式", "简单逛", "粗略", "没逛完",
                             "时间紧"],
                "二次游览意愿": ["再来", "下次", "二刷", "还会来", "值得再来", "下次还来", "会推荐", "还想来", "推荐来",
                                 "安利", "强烈推荐", "必来"]
            }

            portrait["游客画像"] = {
                "出行场景": calc_percent(scene_keywords),
                "消费习惯": calc_percent(consumption_keywords),
                "游览倾向": calc_percent(tendency_keywords)
            }

            # ========== 2. 行为特征画像 ==========
            focus_keywords = {
                "景观体验": ["风景", "建筑", "夜景", "景色", "壮观", "美丽", "美景", "风光", "漂亮", "震撼", "迷人",
                             "如画", "山水"],
                "服务质量": ["排队", "工作人员", "服务", "态度", "秩序", "管理", "引导", "热情", "周到", "专业", "效率",
                             "体验感"],
                "文化内容": ["历史", "讲解", "文化", "故事", "古迹", "传统", "博物馆", "文物", "传说", "底蕴", "人文",
                             "民俗"],
                "价格因素": ["门票", "价格", "划算", "性价比", "贵", "便宜", "收费", "票价", "值", "超值", "不贵",
                             "合理"]
            }
            platform_keywords = {
                "小红书": ["小红书", "红书", "种草", "笔记", "博主", "小🍠"],
                "抖音": ["抖音", "短视频", "刷到", "热门", "视频", "抖", "抖音刷到"],
                "微博": ["微博", "热搜", "超话", "大V", "微"],
                "携程/美团": ["携程", "美团", "大众点评", "订票", "攻略", "程"],
                "朋友推荐": ["朋友", "推荐", "安利", "介绍", "同事", "家人", "亲戚"]
            }
            portrait["行为特征画像"] = {
                "关注重点": calc_percent(focus_keywords),
                "浏览偏好": calc_percent(platform_keywords)
            }

            # ========== 3. 五类典型客群 ==========
            consumption_scores = {k: sum(all_text.count(kw) for kw in v) for k, v in consumption_keywords.items()}
            family_score = sum(all_text.count(kw) for kw in
                               ["带娃", "孩子", "宝宝", "亲子", "家庭", "小孩", "带孩子", "遛娃", "儿童", "全家",
                                "跟孩子", "和孩子"])

            clusters = {}
            if consumption_scores.get("网红打卡型", 0) > 0:
                clusters["📸 网红打卡型游客"] = {
                    "占比": round(consumption_scores["网红打卡型"] / total_comments * 100, 1),
                    "人群画像": "18-30岁年轻群体，热衷拍照打卡、追求出片效果",
                    "决策因素": ["拍照氛围感", "网红景点", "社交传播价值"],
                    "信息渠道": ["小红书", "抖音", "微博"]
                }
            if consumption_scores.get("品质体验型", 0) > 0:
                clusters["✨ 品质体验型游客"] = {
                    "占比": round(consumption_scores["品质体验型"] / total_comments * 100, 1),
                    "人群画像": "25-40岁中产/白领，注重服务质量和综合体验",
                    "决策因素": ["服务品质", "环境舒适度", "独特体验"],
                    "信息渠道": ["携程", "微信公众号", "朋友推荐"]
                }
            if family_score > 0:
                clusters["👨‍👩‍👧 亲子家庭型游客"] = {
                    "占比": round(family_score / total_comments * 100, 1),
                    "人群画像": "30-45岁父母，以家庭为单位出游",
                    "决策因素": ["安全性", "儿童友好", "趣味性"],
                    "信息渠道": ["朋友推荐", "携程", "微信公众号"]
                }
            if consumption_scores.get("深度文化型", 0) > 0:
                clusters["🏛️ 深度文化型游客"] = {
                    "占比": round(consumption_scores["深度文化型"] / total_comments * 100, 1),
                    "人群画像": "对历史文化有浓厚兴趣的各年龄段游客",
                    "决策因素": ["文化内涵", "历史价值", "知识获取"],
                    "信息渠道": ["攻略网站", "纪录片", "书籍"]
                }
            if consumption_scores.get("性价比优先型", 0) > 0:
                clusters["💰 性价比优先型游客"] = {
                    "占比": round(consumption_scores["性价比优先型"] / total_comments * 100, 1),
                    "人群画像": "学生/预算有限的年轻群体",
                    "决策因素": ["价格实惠", "优惠活动", "性价比"],
                    "信息渠道": ["团购平台", "学生社群", "抖音"]
                }

            if not clusters:
                clusters = {
                    "📸 网红打卡型游客": {"占比": 100, "人群画像": "综合型游客群体", "决策因素": [], "信息渠道": []}}

            clusters = dict(sorted(clusters.items(), key=lambda x: x[1]["占比"], reverse=True))
            portrait["典型客群聚类"] = clusters

            # ========== 4. 营销推送建议 ==========
            marketing_tips = []
            main_cluster = list(clusters.keys())[0] if clusters else ""

            if "网红打卡" in main_cluster:
                marketing_tips.append({
                    "目标客群": "网红打卡型游客",
                    "核心洞察": "受社交媒体影响大，容易被种草，追求出片效果",
                    "推送渠道": "小红书、抖音、微博",
                    "内容方向": "拍照攻略、打卡路线、网红机位、滤镜推荐",
                    "营销形式": "KOL种草、短视频挑战赛、打卡集章活动"
                })
            if "品质体验" in main_cluster or "亲子家庭" in main_cluster:
                marketing_tips.append({
                    "目标客群": "品质/家庭型游客",
                    "核心洞察": "注重服务品质和家庭体验，决策周期较长",
                    "推送渠道": "携程、美团、微信公众号",
                    "内容方向": "品质服务展示、亲子攻略、用户真实评价",
                    "营销形式": "套餐推荐、会员专属优惠、口碑传播"
                })
            if "性价比" in main_cluster:
                marketing_tips.append({
                    "目标客群": "性价比优先型游客",
                    "核心洞察": "价格敏感，容易被优惠吸引",
                    "推送渠道": "团购平台、学生社群、抖音",
                    "内容方向": "优惠信息、学生特价、套票推荐",
                    "营销形式": "限时优惠、拼团活动、学生认证折扣"
                })
            if "深度文化" in main_cluster:
                marketing_tips.append({
                    "目标客群": "深度文化型游客",
                    "核心洞察": "追求文化内涵，希望获得深度体验",
                    "推送渠道": "攻略网站、文化类公众号",
                    "内容方向": "历史文化讲解、故事挖掘、深度游攻略",
                    "营销形式": "文化讲座、沉浸式体验、主题路线"
                })
            marketing_tips.append({
                "目标客群": "全域游客",
                "核心洞察": "多样化需求，需平衡各客群偏好",
                "推送渠道": "综合平台",
                "内容方向": "季节性活动、特色体验、游客故事",
                "营销形式": "社交媒体运营、用户UGC激励、口碑营销"
            })
            portrait["营销推送建议"] = marketing_tips[:4]

            # ========== 5. 可视化数据 ==========
            portrait["可视化数据"] = {
                "客群名称": list(clusters.keys()),
                "客群占比": [str(v["占比"]) + "%" for v in clusters.values()]
            }

            return portrait

        except Exception as e:
            return {"error": str(e)}
    def get_date_range(self):
        """获取数据的时间范围，精确到日"""
        if 'date' not in self.df.columns:
            return None
        dates = self.df['date'].dropna()
        if dates.empty:
            return None
        return {
            'min': dates.min().strftime('%Y-%m-%d'),
            'max': dates.max().strftime('%Y-%m-%d')
        }

    def get_operation_model(self):
        """只返回 TOP5 景点数据"""
        if 'operation_model' in self._cache:
            return self._cache['operation_model']
        rankings = self.get_spot_rankings(top_n=10)
        if not rankings:
            return None
        model = {'top_spots': rankings[:5]}
        self._cache['operation_model'] = model
        return model

    def get_hot_potential(self, top_n=5):
        """
        热度爆发潜力分析：
        - 评论量增长率（最近30天 vs 之前30天）
        - 评分变化
        - 正向情感关键词增长
        综合输出爆发指数和未来7天预测
        """
        cache_key = self._get_cache_key('hot_potential_v3', top_n)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if 'date' not in self.df.columns or self.df['date'].isna().all():
            return []

        df = self.df.dropna(subset=['date']).copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])

        results = []
        for spot in df['spot_name'].unique():
            spot_df = df[df['spot_name'] == spot]
            if spot_df.empty:
                continue

            # 每个景点用自己最新的日期作为基准
            spot_max_date = spot_df['date'].max()
            recent_start = spot_max_date - pd.Timedelta(days=30)
            prev_start = spot_max_date - pd.Timedelta(days=60)

            recent = spot_df[spot_df['date'] > recent_start]
            prev = spot_df[(spot_df['date'] > prev_start) & (spot_df['date'] <= recent_start)]

            recent_count = len(recent)
            prev_count = len(prev)

            # 数据太少跳过
            if recent_count < 3:
                continue

            # 评论量增长率
            if prev_count > 0:
                count_growth = (recent_count - prev_count) / prev_count * 100
            else:
                count_growth = 100 if recent_count > 0 else 0

            # 评分变化
            recent_avg = recent['sentiment_score'].mean()
            prev_avg = prev['sentiment_score'].mean() if prev_count > 0 else recent_avg
            score_change = recent_avg - prev_avg

            # 关键词增长（简化版，作为辅助）
            keyword_score = self._calc_keyword_growth(spot, recent, prev)

            # 综合爆发指数
            count_score = min(100, max(0, 50 + count_growth * 0.4))
            score_score = min(100, max(0, 50 + score_change * 50))
            potential = round(count_score * 0.5 + score_score * 0.25 + keyword_score * 0.25, 0)
            potential = max(50, min(100, potential))  # 限制在50-100

            # 线性回归预测未来7天
            history_data, forecast_data = self._predict_future(spot_df)

            results.append({
                'spot_name': spot,
                'potential_score': int(potential),
                'growth_rate': round(count_growth, 0),
                'recent_count': recent_count,
                'prev_count': prev_count,
                'recent_avg_score': round(recent_avg, 2),
                'score_change': round(score_change, 2),
                'history_data': history_data,
                'forecast_data': forecast_data,
                'base_date': spot_max_date.strftime('%Y-%m-%d')  # ← 加这个
            })

        # 按爆发指数排序
        results.sort(key=lambda x: x['potential_score'], reverse=True)
        results = results[:top_n]

        # 加排名
        for i, r in enumerate(results):
            r['rank'] = i + 1

        self._cache[cache_key] = results
        return results

    def _calc_keyword_growth(self, spot, recent_df, prev_df):
        """计算正向关键词增长得分（简化版）"""
        try:
            if recent_df.empty:
                return 50

            recent_pos = recent_df[recent_df['sentiment_score'] >= 4]['comment'].astype(str).tolist()
            prev_pos = prev_df[prev_df['sentiment_score'] >= 4]['comment'].astype(str).tolist() if not prev_df.empty else []

            if not recent_pos:
                return 50

            recent_text = ' '.join(recent_pos)
            recent_words = Counter()
            for w in jieba.cut(recent_text):
                if len(w) >= 2 and w not in self.stop_words and w not in self._spot_names_set:
                    if not any(w in name for name in self._spot_names_set):
                        recent_words[w] += 1

            if not prev_pos:
                return 70  # 之前没数据，给个中等偏上分

            prev_text = ' '.join(prev_pos)
            prev_words = Counter()
            for w in jieba.cut(prev_text):
                if len(w) >= 2 and w not in self.stop_words:
                    prev_words[w] += 1

            # 计算新增/上涨关键词数量
            rising_count = 0
            for word, cnt in recent_words.most_common(30):
                prev_cnt = prev_words.get(word, 0)
                if prev_cnt == 0 and cnt >= 3:
                    rising_count += 2  # 新增词
                elif prev_cnt > 0 and (cnt / prev_cnt) >= 1.5:
                    rising_count += 1  # 显著上涨

            # 映射到0-100分
            score = min(100, 50 + rising_count * 4)
            return score
        except Exception as e:
            print(f"[WARN] keyword growth error: {e}")
            return 50

    def _predict_future(self, spot_df, max_date=None):
        """用线性回归预测未来7天评论量（以该景点最新日期为基准）"""
        try:
            if spot_df.empty:
                return [], []

            # 用景点自己的最新日期
            base_date = spot_df['date'].max()
            window = 30

            df_recent = spot_df[spot_df['date'] > base_date - pd.Timedelta(days=window)].copy()
            df_recent['day'] = (df_recent['date'] - (base_date - pd.Timedelta(days=window))).dt.days
            daily = df_recent.groupby('day').size().reindex(range(window), fill_value=0).tolist()

            # 用numpy做线性回归
            x = np.arange(len(daily))
            y = np.array(daily)
            if len(x) >= 2 and y.std() > 0:
                # 拟合
                slope, intercept = np.polyfit(x, y, 1)
                # 预测未来7天
                forecast = []
                for i in range(7):
                    pred = slope * (len(daily) + i) + intercept
                    forecast.append(max(0, round(pred, 1)))
            else:
                avg = float(np.mean(y)) if len(y) > 0 else 0
                forecast = [round(avg, 1)] * 7

            return daily, forecast
        except Exception as e:
            print(f"[WARN] predict error: {e}")
            return [], []

    def get_hot_potential_detail(self, spot_name):
        """单景点爆发详情"""
        cache_key = self._get_cache_key('hot_potential_detail_v3', spot_name)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if 'date' not in self.df.columns:
            return None

        df = self.df.dropna(subset=['date']).copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        spot_df = df[df['spot_name'] == spot_name]
        if spot_df.empty:
            return None

        max_date = spot_df['date'].max()
        recent_start = max_date - pd.Timedelta(days=30)
        prev_start = max_date - pd.Timedelta(days=60)

        recent = spot_df[spot_df['date'] > recent_start]
        prev = spot_df[(spot_df['date'] > prev_start) & (spot_df['date'] <= recent_start)]

        # 计算关键词变化（找上涨最显著的词）
        rising_keywords = self._find_rising_keywords(recent, prev)

        # 历史+预测
        history_data, forecast_data = self._predict_future(spot_df)

        # 评论量、评分
        recent_count = len(recent)
        prev_count = len(prev)
        recent_avg = round(recent['sentiment_score'].mean(), 2) if recent_count else 0
        prev_avg = round(prev['sentiment_score'].mean(), 2) if prev_count else recent_avg

        if prev_count > 0:
            count_growth = round((recent_count - prev_count) / prev_count * 100, 1)
        else:
            count_growth = 100 if recent_count > 0 else 0

        predicted_count = round(sum(forecast_data), 0)

        result = {
            'spot_name': spot_name,
            'history_data': history_data,
            'forecast_data': forecast_data,
            'recent_count': recent_count,
            'prev_count': prev_count,
            'count_growth': count_growth,
            'recent_avg_score': recent_avg,
            'prev_avg_score': prev_avg,
            'score_change': round(recent_avg - prev_avg, 2),
            'predicted_7d_count': int(predicted_count),
            'rising_keywords': rising_keywords
        }

        self._cache[cache_key] = result
        return result

    def _find_rising_keywords(self, recent_df, prev_df, top_n=8):
        """找出上涨最显著的正向关键词"""
        try:
            recent_pos = recent_df[recent_df['sentiment_score'] >= 4]['comment'].astype(str).tolist()
            prev_pos = prev_df[prev_df['sentiment_score'] >= 4]['comment'].astype(str).tolist() if not prev_df.empty else []

            if not recent_pos:
                return []

            def count_words(texts):
                counter = Counter()
                for t in texts:
                    for w in jieba.cut(t):
                        w = w.strip()
                        if (len(w) >= 2 and w not in self.stop_words
                            and not w.isdigit()
                            and w not in self._spot_names_set
                            and not any(w in name for name in self._spot_names_set)):
                            counter[w] += 1
                return counter

            recent_c = count_words(recent_pos)
            prev_c = count_words(prev_pos) if prev_pos else Counter()

            rising = []
            for word, cnt in recent_c.most_common(50):
                if cnt < 3:
                    continue
                prev_cnt = prev_c.get(word, 0)
                if prev_cnt == 0:
                    change_pct = 999  # 新增词
                    rising.append({
                        'word': word,
                        'current_count': cnt,
                        'prev_count': 0,
                        'change_pct': '新增',
                        'is_new': True
                    })
                elif cnt / prev_cnt >= 1.3:
                    change = round((cnt - prev_cnt) / prev_cnt * 100, 0)
                    rising.append({
                        'word': word,
                        'current_count': cnt,
                        'prev_count': prev_cnt,
                        'change_pct': '+' + str(int(change)) + '%',
                        'is_new': False
                    })

            # 排序：新增词在前，然后按当前频次
            rising.sort(key=lambda x: (not x['is_new'], -x['current_count']))
            return rising[:top_n]
        except Exception as e:
            print(f"[WARN] rising keywords error: {e}")
            return []

    def get_factor_trend_simple(self, days=30):
        """
        首页用：痛点出现率的时序变化
        对比：近N天 vs 全时段（去掉近N天）
        """
        cache_key = self._get_cache_key('factor_trend_simple_v1', days)
        if cache_key in self._cache:
            return self._cache[cache_key]

        df = self.df.copy()
        if 'date' not in df.columns or df['date'].isna().all():
            return None

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        if df.empty:
            return None

        # 痛点定义（和 negative_factor_model 保持一致）
        factor_defs = [
            {"factor": "排队等待", "keywords": ["排队", "等", "等待", "队伍", "排很久", "排长队"]},
            {"factor": "人多拥挤", "keywords": ["人多", "拥挤", "挤", "人山人海", "游客太多"]},
            {"factor": "价格/门票", "keywords": ["贵", "门票贵", "门票", "不值", "性价比低", "收费", "价格"]},
            {"factor": "服务态度", "keywords": ["服务差", "态度差", "态度", "工作人员", "冷漠", "不热情", "服务"]},
            {"factor": "交通停车", "keywords": ["远", "交通", "停车", "停车场", "不好找", "打车", "堵车"]},
            {"factor": "环境卫生", "keywords": ["脏", "乱", "卫生", "厕所", "垃圾", "环境差", "异味"]},
            {"factor": "商业化", "keywords": ["商业化", "强制消费", "宰客", "消费", "小摊", "推销"]},
            {"factor": "设施管理", "keywords": ["设施", "老化", "管理", "混乱", "秩序", "指示牌", "路线"]},
            {"factor": "天气体感", "keywords": ["热", "晒", "冷", "下雨", "天气", "遮阳"]}
        ]

        # 用全局最新日期为基准
        max_date = df['date'].max()
        recent_start = max_date - pd.Timedelta(days=days)

        recent_df = df[df['date'] > recent_start]
        all_df = df  # 用全时段做基准

        recent_total = len(recent_df)
        all_total = len(all_df)

        if recent_total < 10 or all_total < 10:
            return None

        # 只对差评做痛点统计（评分<=3）
        recent_neg = recent_df[recent_df['sentiment_score'] <= 3]
        all_neg = all_df[all_df['sentiment_score'] <= 3]
        recent_neg_total = max(len(recent_neg), 1)
        all_neg_total = max(len(all_neg), 1)

        results = []
        for f in factor_defs:
            kws = f['keywords']

            # 近30天该痛点出现次数
            recent_match = recent_neg['comment'].astype(str).apply(
                lambda c: any(k in c for k in kws)
            ).sum()
            # 全时段该痛点出现次数
            all_match = all_neg['comment'].astype(str).apply(
                lambda c: any(k in c for k in kws)
            ).sum()

            recent_rate = round(recent_match / recent_neg_total * 100, 1)
            all_rate = round(all_match / all_neg_total * 100, 1)
            change = round(recent_rate - all_rate, 1)

            results.append({
                'factor': f['factor'],
                'recent_rate': recent_rate,    # 近30天出现率
                'all_rate': all_rate,           # 全时段出现率
                'change': change,                # 变化值
                'trend': 'up' if change > 0.5 else ('down' if change < -0.5 else 'flat'),
                'recent_count': int(recent_match),
                'all_count': int(all_match)
            })

        # 按全时段出现率排序
        results.sort(key=lambda x: x['all_rate'], reverse=True)

        self._cache[cache_key] = {
            'items': results,
            'recent_sample': recent_neg_total,
            'all_sample': all_neg_total,
            'days': days
        }
        return self._cache[cache_key]

    def get_dual_rankings(self, weights=None, ranking_type='hot'):
        """
        双榜单计算
        :param weights: {'mafengwo': 33, 'ctrip': 34, 'dianping': 33} 默认均衡
        :param ranking_type: 'hot'=热度榜, 'quality'=好评榜
        :return: 排名列表
        """
        import math

        if weights is None:
            weights = {'mafengwo': 33, 'ctrip': 34, 'dianping': 33}

        # 从缓存取数据，转为干净的 Python 列表
        raw_stats = self._cache.get('spot_stats', None)
        if raw_stats is None or (hasattr(raw_stats, 'empty') and raw_stats.empty):
            return []
        spot_stats = raw_stats.to_dict('records')

        # 权重归一化
        w_sum = sum(weights.values())
        if w_sum == 0:
            return []
        w_mfw = weights.get('mafengwo', 0) / w_sum
        w_ctp = weights.get('ctrip', 0) / w_sum
        w_dp = weights.get('dianping', 0) / w_sum

        # ===== 热度榜 =====
        if ranking_type == 'hot':
            plat_data = []
            for s in spot_stats:
                name = s['spot_name']
                raw = PLATFORM_RAW_DATA.get(name, {'mafengwo': 0, 'ctrip': 0, 'dianping': 0})
                plat_data.append({
                    'spot_name': name,
                    'avg_score': float(s.get('avg_score', 0)),
                    'positive_rate': float(s.get('positive_rate', 0)),
                    'comment_count': int(s.get('comment_count', 0)),
                    'mafengwo': int(raw['mafengwo']),
                    'ctrip': int(raw['ctrip']),
                    'dianping': int(raw['dianping']),
                })

            max_mfw = max((d['mafengwo'] for d in plat_data), default=1) or 1
            max_ctp = max((d['ctrip'] for d in plat_data), default=1) or 1
            max_dp = max((d['dianping'] for d in plat_data), default=1) or 1

            for d in plat_data:
                score = (
                                (d['mafengwo'] / max_mfw) * w_mfw +
                                (d['ctrip'] / max_ctp) * w_ctp +
                                (d['dianping'] / max_dp) * w_dp
                        ) * 100
                d['heat_score'] = round(score, 1)

            plat_data.sort(key=lambda x: x['heat_score'], reverse=True)
            return plat_data

        # ===== 好评榜 =====
        elif ranking_type == 'quality':
            max_comments = max((int(s.get('comment_count', 0)) for s in spot_stats), default=1) or 1

            quality_data = []
            for s in spot_stats:
                avg_score = min(float(s.get('avg_score', 0)), 5)  # 防止超过5分
                positive_rate = float(s.get('positive_rate', 0))
                comment_count = int(s.get('comment_count', 0))

                score = (
                                (avg_score / 5) * 0.5 +
                                (positive_rate / 100) * 0.3 +
                                (math.log10(comment_count + 1) / math.log10(max_comments + 1)) * 0.2
                        ) * 100

                quality_data.append({
                    'spot_name': s['spot_name'],
                    'avg_score': avg_score,
                    'positive_rate': positive_rate,
                    'negative_rate': float(s.get('negative_rate', 0)),
                    'comment_count': comment_count,
                    'quality_score': round(score, 1),
                })

            quality_data.sort(key=lambda x: x['quality_score'], reverse=True)
            return quality_data

        return []

    # ================================================================
    # 运营预警面板
    # ================================================================
    def get_operation_alerts(self):
        """运营预警：检测客流异常、舆情风险、口碑变化"""
        cache_key = self._get_cache_key('operation_alerts_v1')
        if cache_key in self._cache:
            return self._cache[cache_key]

        if 'date' not in self.df.columns or self.df['date'].isna().all():
            return {'urgent': [], 'warning': [], 'stable': []}

        df = self.df.dropna(subset=['date']).copy()
        if df.empty:
            return {'urgent': [], 'warning': [], 'stable': []}

        # 敏感词检测
        sensitive_words = ['投诉', '维权', '黑导游', '坑骗', '强制消费', '骗人', '欺诈', '宰客']

        urgent = []
        warning = []
        stable = []

        for spot in df['spot_name'].unique():
            spot_df = df[df['spot_name'] == spot]
            if spot_df.empty:
                continue

            spot_max = spot_df['date'].max()
            recent_start = spot_max - pd.Timedelta(days=7)
            prev_end = recent_start - pd.Timedelta(days=1)
            prev_start = prev_end - pd.Timedelta(days=7)

            recent = spot_df[spot_df['date'] >= recent_start]
            prev = spot_df[(spot_df['date'] >= prev_start) & (spot_df['date'] <= prev_end)]

            if len(recent) < 5:
                continue  # 数据太少不分析

            # 1. 评论量变化
            recent_cnt = len(recent)
            prev_cnt = max(len(prev), 1)
            cnt_change_pct = round((recent_cnt - prev_cnt) / prev_cnt * 100, 1)

            # 2. 差评率变化
            recent_neg_rate = round((recent['sentiment_score'] <= 2).mean() * 100, 1)
            prev_neg_rate = round((prev['sentiment_score'] <= 2).mean() * 100, 1) if len(prev) > 0 else recent_neg_rate
            neg_change = round(recent_neg_rate - prev_neg_rate, 1)

            # 3. 敏感词检测
            recent_comments_text = ' '.join(recent['comment'].astype(str).tolist())
            sensitive_hits = []
            for kw in sensitive_words:
                count = recent_comments_text.count(kw)
                if count >= 2:
                    sensitive_hits.append({'word': kw, 'count': count})

            # 判断预警等级
            alerts = []
            level = 'stable'  # urgent / warning / stable

            # 紧急：敏感词出现 + 差评率激增
            if sensitive_hits:
                level = 'urgent'
                # 提取每个敏感词对应的真实评论（最多2条/词）
                related_comments = []
                for h in sensitive_hits[:3]:
                    word = h['word']
                    matched = recent[recent['comment'].astype(str).str.contains(word, na=False)]['comment'].tolist()[:2]
                    for c in matched:
                        related_comments.append({'keyword': word, 'text': str(c)[:120]})

                alerts.append({
                    'type': '舆情风险',
                    'desc': f"近7天出现敏感词：{', '.join([h['word'] for h in sensitive_hits[:3]])}",
                    'icon': '⚠️',
                    'related_comments': related_comments
                })

            if neg_change >= 5:
                level = 'urgent' if level == 'urgent' else 'urgent'
                # 取近7天的差评样本
                recent_neg_samples = recent[recent['sentiment_score'] <= 2]['comment'].astype(str).tolist()[:5]
                related_comments = [{'keyword': '差评', 'text': c[:120]} for c in recent_neg_samples]
                alerts.append({
                    'type': '差评激增',
                    'desc': f"差评率周环比 +{neg_change}%（{prev_neg_rate}% → {recent_neg_rate}%）",
                    'icon': '📉',
                    'related_comments': related_comments
                })

            # 关注：评论量大幅波动
            if abs(cnt_change_pct) >= 100 and level != 'urgent':
                level = 'warning'
                trend_word = '激增' if cnt_change_pct > 0 else '骤降'
                alerts.append({
                    'type': f'客流{trend_word}',
                    'desc': f"评论量周环比 {'+' if cnt_change_pct > 0 else ''}{cnt_change_pct}%（{prev_cnt} → {recent_cnt}）",
                    'icon': '📈' if cnt_change_pct > 0 else '📉'
                })
            elif abs(cnt_change_pct) >= 50 and level == 'stable':
                level = 'warning'
                trend_word = '上升' if cnt_change_pct > 0 else '下降'
                alerts.append({
                    'type': f'热度{trend_word}',
                    'desc': f"评论量周环比 {'+' if cnt_change_pct > 0 else ''}{cnt_change_pct}%",
                    'icon': '📊'
                })

            if neg_change >= 2 and level == 'stable':
                level = 'warning'
                recent_neg_samples = recent[recent['sentiment_score'] <= 2]['comment'].astype(str).tolist()[:5]
                related_comments = [{'keyword': '差评', 'text': c[:120]} for c in recent_neg_samples]
                alerts.append({
                    'type': '差评上升',
                    'desc': f"差评率周环比 +{neg_change}%",
                    'icon': '⚠️',
                    'related_comments': related_comments
                })

            item = {
                'spot_name': spot,
                'level': level,
                'alerts': alerts if alerts else [{'type': '运行平稳', 'desc': '近期无异常波动', 'icon': '✓'}],
                'recent_count': recent_cnt,
                'prev_count': prev_cnt,
                'recent_neg_rate': recent_neg_rate,
                'cnt_change_pct': cnt_change_pct,
                'neg_change': neg_change
            }

            if level == 'urgent':
                urgent.append(item)
            elif level == 'warning':
                warning.append(item)
            else:
                stable.append(item)

        result = {
            'urgent': sorted(urgent, key=lambda x: -abs(x['cnt_change_pct'])),
            'warning': sorted(warning, key=lambda x: -abs(x['cnt_change_pct'])),
            'stable': stable,
            'summary': {
                'urgent_count': len(urgent),
                'warning_count': len(warning),
                'stable_count': len(stable),
                'total': len(urgent) + len(warning) + len(stable)
            }
        }

        self._cache[cache_key] = result
        return result

    # ================================================================
    # 节假日客流预测
    # ================================================================
    def get_holiday_forecast(self):
        """节假日预测：自动识别下一个法定节假日"""
        cache_key = self._get_cache_key('holiday_forecast_v2')
        if cache_key in self._cache:
            return self._cache[cache_key]

        if 'date' not in self.df.columns or self.df['date'].isna().all():
            return None

        df = self.df.dropna(subset=['date']).copy()
        if df.empty:
            return None

        # 数据最新日期（用于历史数据查询范围）
        max_date = df['date'].max()

        # 使用真实今天（用于节假日倒计时展示）
        from datetime import date as _real_date
        today = _real_date.today()

        # ==================== 找下一个节假日 ====================
        upcoming = self._find_next_holiday(today)
        if not upcoming:
            return None

        # ==================== 预测各景点客流 ====================
        spot_forecasts = []
        for spot in df['spot_name'].unique():
            spot_df = df[df['spot_name'] == spot]
            if spot_df.empty:
                continue

            # 查找往年同名节假日的真实日期，取历史数据
            history_counts = self._get_holiday_history_avg(
                spot_df, upcoming['name'], today.year
            )

            if history_counts:
                avg_daily = round(sum(history_counts) / len(history_counts), 0)
            else:
                # 没有历史同期数据，用最近 30 天平均
                recent = spot_df[spot_df['date'] >= max_date - pd.Timedelta(days=30)]
                avg_daily = round(len(recent) / 30, 0) if not recent.empty else 0

            # 预测节假日期间总量（节假日通常 1.5-2 倍）
            holiday_factor = 1.8
            predicted_total = int(avg_daily * upcoming['duration'] * holiday_factor)

            # 客流等级
            if predicted_total >= 500:
                level, level_text = 'extreme', '极高'
            elif predicted_total >= 100:
                level, level_text = 'high', '高'
            elif predicted_total >= 50:
                level, level_text = 'medium', '中等'
            else:
                level, level_text = 'low', '一般'

            # 建议
            suggestions = []
            if level in ('extreme', 'high'):
                suggestions.append('开放分时预约，控制单日上限')
                suggestions.append('增派现场工作人员维持秩序')
                suggestions.append('准备应急疏散预案')
            elif level == 'medium':
                suggestions.append('做好基础接待保障')
                suggestions.append('监测实时客流')
            else:
                suggestions.append('利用客流较少时段开展营销')

            spot_forecasts.append({
                'spot_name': spot,
                'predicted_total': predicted_total,
                'daily_avg': int(avg_daily * holiday_factor),
                'level': level,
                'level_text': level_text,
                'suggestions': suggestions,
                'has_history': len(history_counts) > 0
            })

        spot_forecasts.sort(key=lambda x: -x['predicted_total'])

        result = {
            'holiday': {
                'name': upcoming['name'],
                'date': upcoming['start_date'].strftime('%Y-%m-%d'),
                'duration': upcoming['duration'],
                'days_left': (upcoming['start_date'] - today).days
            },
            'forecasts': spot_forecasts,
            'base_date': today.strftime('%Y-%m-%d')
        }

        self._cache[cache_key] = result
        return result

    def _find_next_holiday(self, today):
        """使用 chinese_calendar 库找下一个尚未开始的法定节假日"""
        try:
            import chinese_calendar
            from datetime import date, timedelta
        except ImportError:
            print("[WARNING] chinese_calendar 库未安装")
            return None

        name_map = {
            "New Year's Day": '元旦',
            'Spring Festival': '春节',
            'Tomb-sweeping Day': '清明节',
            'Labour Day': '劳动节',
            'Dragon Boat Festival': '端午节',
            'Mid-autumn Festival': '中秋节',
            'National Day': '国庆节',
        }

        # 查询节假日
        all_holidays = None
        for end_year in [today.year + 1, today.year]:
            try:
                end_date_query = date(end_year, 12, 31)
                all_holidays = chinese_calendar.get_holidays(today, end_date_query)
                break
            except Exception as e:
                print(f"[INFO] chinese_calendar 查询 {end_year} 失败: {e}")
                continue

        if not all_holidays:
            return None

        # 关键过滤：只保留有中文名映射的真实法定节假日（排除库里可能返回的其他日期）
        valid_holidays = []
        for d in all_holidays:
            try:
                _, en_name = chinese_calendar.get_holiday_detail(d)
                if en_name in name_map:
                    valid_holidays.append((d, en_name))
            except Exception:
                continue

        if not valid_holidays:
            return None

        # 按连续日期加同名分组
        groups = []
        current_group = [valid_holidays[0]]
        for i in range(1, len(valid_holidays)):
            prev_d, prev_name = valid_holidays[i - 1]
            curr_d, curr_name = valid_holidays[i]
            if (curr_d - prev_d).days == 1 and curr_name == prev_name:
                current_group.append(valid_holidays[i])
            else:
                groups.append(current_group)
                current_group = [valid_holidays[i]]
        groups.append(current_group)

        # 取第一个 start_date 严格大于 today 的节假日
        for group in groups:
            first_date = group[0][0]
            last_date = group[-1][0]
            en_name = group[0][1]

            if first_date > today:
                # 只在法定节假日紧挨着周末时才把周末算进假期
                # 向前延伸：如果第一天是周一，前一天（周日）算连休
                start_date = first_date
                check = first_date - timedelta(days=1)
                while check.weekday() >= 5:  # 5=周六 6=周日
                    start_date = check
                    check -= timedelta(days=1)

                # 向后延伸：如果最后一天是周五，后一天（周六）算连休
                end_date = last_date
                check = last_date + timedelta(days=1)
                while check.weekday() >= 5:
                    end_date = check
                    check += timedelta(days=1)

                duration = (end_date - start_date).days + 1
                cn_name = name_map.get(en_name, en_name)

                return {
                    'name': cn_name,
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration': duration,
                }

        # chinese_calendar only contains officially announced data through a
        # limited year range. If the current year's holidays are exhausted,
        # the next fixed-date statutory holiday is New Year's Day. Do not guess
        # any adjusted days off for the following year.
        next_new_year = date(today.year + 1, 1, 1)
        if next_new_year > today:
            return {
                'name': '元旦',
                'start_date': next_new_year,
                'end_date': next_new_year,
                'duration': 1,
            }

        return None

    def _get_holiday_history_avg(self, spot_df, holiday_name, current_year):
        """获取往年同名节假日期间该景点的日均评论数"""
        try:
            import chinese_calendar
            from datetime import date
        except ImportError:
            return []

        name_map = {
            '元旦': "New Year's Day",
            '春节': 'Spring Festival',
            '清明节': 'Tomb-sweeping Day',
            '劳动节': 'Labour Day',
            '端午节': 'Dragon Boat Festival',
            '中秋节': 'Mid-autumn Festival',
            '国庆节': 'National Day',
        }
        en_name = name_map.get(holiday_name)
        if not en_name:
            return []

        history_counts = []
        for year_offset in range(1, 4):
            history_year = current_year - year_offset
            try:
                year_holidays = chinese_calendar.get_holidays(
                    date(history_year, 1, 1), date(history_year, 12, 31)
                )
            except Exception:
                continue

            # 找到该年同名节假日的所有日期
            matched_dates = []
            for d in year_holidays:
                try:
                    _, name = chinese_calendar.get_holiday_detail(d)
                    if name == en_name:
                        matched_dates.append(d)
                except Exception:
                    continue

            if not matched_dates:
                continue

            # 转成 pandas 时间戳并查询该景点评论数
            start = pd.Timestamp(matched_dates[0])
            end = pd.Timestamp(matched_dates[-1])
            hist_df = spot_df[(spot_df['date'] >= start) & (spot_df['date'] <= end)]
            if not hist_df.empty:
                history_counts.append(len(hist_df) / len(matched_dates))

        return history_counts

    # ================================================================
    # 景点能力雷达
    # ================================================================
    def get_capability_radar(self, spot_names=None):
        """景点能力雷达：从评论中提取6个维度的能力分"""
        if not spot_names:
            spot_names = self.df['spot_name'].unique().tolist()

        # 6个能力维度，每个维度配关键词
        dimensions = {
            '服务质量': {
                'positive': ['服务好', '热情', '态度好', '专业', '周到', '贴心', '讲解员', '细心'],
                'negative': ['服务差', '态度差', '冷漠', '不耐烦', '推卸', '推销']
            },
            '卫生环境': {
                'positive': ['干净', '整洁', '卫生', '清洁', '环境好'],
                'negative': ['脏', '乱', '臭', '垃圾', '厕所差', '异味']
            },
            '设施完善': {
                'positive': ['设施完善', '便利', '配套', '指示清楚', '路线好走'],
                'negative': ['设施老旧', '指示不清', '路线乱', '没座位', '没遮阳']
            },
            '性价比': {
                'positive': ['值', '便宜', '划算', '性价比高', '不贵'],
                'negative': ['贵', '不值', '坑', '门票贵', '消费高']
            },
            '文化体验': {
                'positive': ['文化', '历史', '震撼', '讲解好', '底蕴', '有意义', '涨知识'],
                'negative': ['没文化', '商业化', '没意思', '无聊', '一般']
            },
            '人流管理': {
                'positive': ['不挤', '人少', '秩序好', '不排队', '宽松'],
                'negative': ['人多', '拥挤', '排队', '挤死', '人山人海']
            }
        }

        result = []
        for spot in spot_names:
            spot_df = self.df[self.df['spot_name'] == spot]
            if spot_df.empty:
                continue

            text = ' '.join(spot_df['comment'].astype(str).tolist())
            total = len(spot_df)

            scores = {}
            for dim_name, kws in dimensions.items():
                pos_hits = sum(text.count(k) for k in kws['positive'])
                neg_hits = sum(text.count(k) for k in kws['negative'])

                # 计算得分 0-100
                if pos_hits + neg_hits == 0:
                    score = 60  # 没提到，给中位数
                else:
                    raw = pos_hits / (pos_hits + neg_hits) * 100
                    # 平滑：考虑提及频次
                    mention_density = (pos_hits + neg_hits) / total * 100
                    if mention_density < 5:
                        # 提及太少，向中位数收敛
                        score = round(raw * 0.5 + 60 * 0.5, 1)
                    else:
                        score = round(raw, 1)

                # 限制 20-95，避免极值
                score = max(20, min(95, score))
                scores[dim_name] = score

            result.append({
                'spot_name': spot,
                'scores': scores,
                'avg_score': round(sum(scores.values()) / len(scores), 1)
            })

        return result

    # ================================================================
    # 景点对比 - 综合数据
    # ================================================================
    def get_comparison_advanced(self, spot_names):
        """整合多个景点的对比数据"""
        print(f"[DEBUG] get_comparison_advanced 收到: {spot_names}")
        print(f"[DEBUG] 类型: {type(spot_names)}")

        if not spot_names:
            print("[DEBUG] spot_names 为空")
            return []

        dimensions = {
            '服务质量': {
                'positive': ['服务好', '热情', '态度好', '专业', '周到', '贴心', '讲解员', '细心'],
                'negative': ['服务差', '态度差', '冷漠', '不耐烦', '推卸', '推销']
            },
            '卫生环境': {
                'positive': ['干净', '整洁', '卫生', '清洁', '环境好'],
                'negative': ['脏', '乱', '臭', '垃圾', '厕所差', '异味']
            },
            '设施完善': {
                'positive': ['设施完善', '便利', '配套', '指示清楚', '路线好走'],
                'negative': ['设施老旧', '指示不清', '路线乱', '没座位', '没遮阳']
            },
            '性价比': {
                'positive': ['值', '便宜', '划算', '性价比高', '不贵'],
                'negative': ['贵', '不值', '坑', '门票贵', '消费高']
            },
            '文化体验': {
                'positive': ['文化', '历史', '震撼', '讲解好', '底蕴', '有意义', '涨知识'],
                'negative': ['没文化', '商业化', '没意思', '无聊', '一般']
            },
            '人流管理': {
                'positive': ['不挤', '人少', '秩序好', '不排队', '宽松'],
                'negative': ['人多', '拥挤', '排队', '挤死', '人山人海']
            }
        }

        def calc_radar(spot_df):
            text = ' '.join(spot_df['comment'].astype(str).tolist())
            total = len(spot_df)
            scores = {}
            for dim_name, kws in dimensions.items():
                pos_hits = sum(text.count(k) for k in kws['positive'])
                neg_hits = sum(text.count(k) for k in kws['negative'])
                if pos_hits + neg_hits == 0:
                    score = 60
                else:
                    raw = pos_hits / (pos_hits + neg_hits) * 100
                    mention_density = (pos_hits + neg_hits) / total * 100
                    if mention_density < 5:
                        score = round(raw * 0.5 + 60 * 0.5, 1)
                    else:
                        score = round(raw, 1)
                score = max(20, min(95, score))
                scores[dim_name] = score
            return scores

        result = []
        for name in spot_names:
            print(f"[DEBUG] 处理景点: '{name}'")
            spot_df = self.df[self.df['spot_name'] == name]
            print(f"[DEBUG] 匹配条数: {len(spot_df)}")

            if spot_df.empty:
                print(f"[DEBUG] 景点 '{name}' 数据为空，跳过")
                continue

            try:
                dist = self._cache.get('score_dist_by_spot', {}).get(name, {})
                if not dist:
                    raw = spot_df['sentiment_score'].value_counts().to_dict()
                    dist = {int(i): int(raw.get(i, 0)) for i in range(1, 6)}

                kw = self.get_ai_keywords(name) or {}
                radar_scores = calc_radar(spot_df)

                # 取热度分（用首页双榜单的热度榜）
                heat_score = 0
                try:
                    hot_data = self.get_dual_rankings(ranking_type='hot')
                    if hot_data:
                        for h in hot_data:
                            if h['spot_name'] == name:
                                heat_score = h.get('heat_score', 0)
                                break
                except Exception:
                    pass

                result.append({
                    'name': name,
                    'comment_count': int(len(spot_df)),
                    'avg_score': round(float(spot_df['sentiment_score'].mean()), 2),
                    'positive_rate': round(float((spot_df['sentiment_score'] >= 4).mean() * 100), 1),
                    'negative_rate': round(float((spot_df['sentiment_score'] <= 2).mean() * 100), 1),
                    'heat_score': heat_score,
                    'score_distribution': dist,
                    'positive_keywords': (kw.get('positive') or [])[:5],
                    'negative_keywords': (kw.get('negative') or [])[:5],
                    'radar_scores': radar_scores
                })
                print(f"[DEBUG] 景点 '{name}' 处理成功")
            except Exception as e:
                print(f"[DEBUG] 景点 '{name}' 处理失败: {e}")
                import traceback
                traceback.print_exc()

        print(f"[DEBUG] 最终结果: {len(result)} 个景点")
        return result

    # ================================================================
    # AI 综合推荐结论
    # ================================================================
    def get_ai_comparison_summary(self, spot_names):
        """AI 生成景点对比的综合推荐结论"""
        engine = getattr(self, '_current_engine', AI_DEFAULT_ENGINE)
        cache_key = self._get_cache_key('ai_cmp_summary_v1', ','.join(sorted(spot_names)), engine)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not spot_names or len(spot_names) < 2:
            return {'error': '至少需要2个景点'}

        spots_data = []
        for name in spot_names:
            spot_df = self.df[self.df['spot_name'] == name]
            if spot_df.empty:
                continue
            kw = self.get_ai_keywords(name) or {}
            spots_data.append({
                'name': name,
                'avg_score': round(float(spot_df['sentiment_score'].mean()), 2),
                'positive_rate': round(float((spot_df['sentiment_score'] >= 4).mean() * 100), 1),
                'negative_rate': round(float((spot_df['sentiment_score'] <= 2).mean() * 100), 1),
                'comment_count': len(spot_df),
                'pos_keywords': '；'.join((kw.get('positive') or [])[:5]),
                'neg_keywords': '；'.join((kw.get('negative') or [])[:5])
            })

        if not spots_data:
            return {'error': '数据不足'}

        spots_info = '\n'.join([
            f"【{d['name']}】评分{d['avg_score']}，好评率{d['positive_rate']}%，差评率{d['negative_rate']}%，{d['comment_count']}条评论\n  好评：{d['pos_keywords']}\n  差评：{d['neg_keywords']}"
            for d in spots_data
        ])

        spot_list = '、'.join([d['name'] for d in spots_data])

        prompt = f"""你是专业文旅分析师，请对比以下景点：{spot_list}

        【各景点数据】
        {spots_info}
        
        请严格按以下JSON格式输出，不要任何markdown代码块标记：
        {{
          "summary": "一句话对比总结（30-50字，说清各景点最大差异）",
          "spot_profiles": [
            {{"name": "景点名", "tagline": "一句话定位（10-15字）", "best_for": "适合人群（10-15字）"}}
          ],
          "scenario_recommendations": [
            {{"scenario": "文化深度游", "recommend": "景点名", "reason": "理由（20字内）"}},
            {{"scenario": "情侣浪漫游", "recommend": "景点名", "reason": "理由（20字内）"}},
            {{"scenario": "亲子家庭游", "recommend": "景点名", "reason": "理由（20字内）"}},
            {{"scenario": "网红打卡", "recommend": "景点名", "reason": "理由（20字内）"}},
            {{"scenario": "性价比之选", "recommend": "景点名", "reason": "理由（20字内）"}}
          ]
        }}"""

        ai_text = self._call_ai(prompt, max_tokens=1200)
        engine_label = self._get_engine_label()

        if not ai_text:
            return {'status': 'fallback', 'engine': '本地模板',
                    'summary': '、'.join([d['name'] for d in spots_data]) + ' 各有特色',
                    'spot_profiles': [],
                    'scenario_recommendations': []}

        try:
            json_text = self._extract_json_text(ai_text)
            if json_text:
                parsed = json.loads(json_text)
                result = {
                    'status': 'success',
                    'engine': engine_label,
                    'summary': parsed.get('summary', ''),
                    'spot_profiles': parsed.get('spot_profiles', []),
                    'scenario_recommendations': parsed.get('scenario_recommendations', [])
                }
                self._cache[cache_key] = result
                return result
        except Exception as e:
            print(f"[WARN] AI对比总结解析失败: {e}")

        return {'status': 'fallback', 'engine': '本地模板',
                'summary': '请配置AI Key获取智能推荐',
                'spot_profiles': [],
                'scenario_recommendations': []}
