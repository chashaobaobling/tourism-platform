"""
preprocess_all.py - 批量预处理数据并创建评论审核批次（V2）
支持：
  1. 单文件导入：python preprocess_all.py 文件路径
  2. 文件夹批量导入：python preprocess_all.py 文件夹路径
  3. 默认导入：直接运行，读取 DATA_DIR 配置的文件夹
"""

import pandas as pd
import os
import sys
import glob
import re

# ==================== 配置 ====================
DATA_DIR = r"D:\数据素养\数据"       # 默认数据文件夹
OUTPUT_CSV = r"D:\数据素养\standardized_final_v5.csv"
# =============================================

# 列名映射：原始列 → 数据库标准列
COLUMN_MAP = {
    '景点名称': 'spot_name',
    '昵称':     'user_name',
    '评分':     'sentiment_score',
    '评论':     'comment',
    '日期':     'comment_date',
    # 兼容其他可能的列名
    '景点':     'spot_name',
    '用户名':   'user_name',
    '用户':     'user_name',
    '评论内容': 'comment',
    '内容':     'comment',
    '评论时间': 'comment_date',
    '时间':     'comment_date',
    '评论日期': 'comment_date',
    '打分':     'sentiment_score',
    '星级':     'sentiment_score',
    'score':    'sentiment_score',
    'rating':   'sentiment_score',
}


def clean_score(score):
    """评分清洗，统一为 1-5 整数"""
    try:
        if pd.isna(score) or str(score).strip() == '':
            return 5
        s = str(score)
        match = re.search(r"(\d+\.?\d*)", s)
        if match:
            val = float(match.group(1))
            if val > 10:
                val = val / 20
            elif val > 5:
                val = val / 2
            val = round(val)
            return max(1, min(5, int(val)))
        return 5
    except:
        return 5


def clean_date(date_str):
    """日期清洗，统一为 YYYY-MM-DD"""
    if not date_str or pd.isna(date_str):
        return ''
    s = str(date_str).strip()

    # 已经是标准格式
    if re.match(r'^\d{4}[-/]\d{2}[-/]\d{2}', s):
        return s.replace('/', '-')[:10]

    # 尝试 pandas 解析
    try:
        dt = pd.to_datetime(s, errors='coerce')
        if pd.notna(dt):
            return dt.strftime('%Y-%m-%d')
    except:
        pass

    # 提取数字
    nums = re.findall(r'\d+', s)
    if len(nums) >= 3:
        y, m, d = nums[0], nums[1].zfill(2), nums[2].zfill(2)
        return f"{y}-{m}-{d}"
    return ''


def read_one_file(file_path):
    """读取一个文件（CSV/Excel），返回标准化的 DataFrame"""
    ext = os.path.splitext(file_path)[1].lower()
    fname = os.path.basename(file_path)

    try:
        if ext in ('.xlsx', '.xls'):
            df = pd.read_excel(file_path)
        elif ext == '.csv':
            # 尝试多种编码
            df = None
            for enc in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    break
                except:
                    continue
            if df is None:
                print(f"✗ {fname}: 编码识别失败")
                return None
        else:
            print(f"⊘ {fname}: 不支持的格式")
            return None
    except Exception as e:
        print(f"✗ {fname}: 读取失败 - {e}")
        return None

    if df is None or df.empty:
        print(f"⊘ {fname}: 文件为空")
        return None

    # 列名清洗
    df.columns = [str(c).strip() for c in df.columns]

    # 列名映射
    rename_dict = {}
    for col in df.columns:
        if col in COLUMN_MAP:
            rename_dict[col] = COLUMN_MAP[col]
    df = df.rename(columns=rename_dict)

    # 检查必要列
    if 'comment' not in df.columns:
        print(f"✗ {fname}: 缺少评论列")
        return None

    # 景点名兜底：如果没有，用文件名
    if 'spot_name' not in df.columns:
        spot_name = os.path.splitext(fname)[0]
        # 去掉常见后缀
        spot_name = re.sub(r'[_\-]?\d+页?[_\-]?\d*$', '', spot_name)
        spot_name = re.sub(r'_\d{8}_\d{6}$', '', spot_name)
        df['spot_name'] = spot_name

    # 补充其他列
    if 'user_name' not in df.columns:
        df['user_name'] = '未知用户'
    if 'comment_date' not in df.columns:
        df['comment_date'] = ''
    if 'sentiment_score' not in df.columns:
        df['sentiment_score'] = 5

    df['source'] = ext.replace('.', '').upper() + '导入'

    print(f"✓ {fname}: {len(df)} 条")
    return df


def collect_files(path):
    """收集要处理的文件列表"""
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        files = []
        for ext in ('*.csv', '*.xlsx', '*.xls'):
            files.extend(glob.glob(os.path.join(path, ext)))
        return sorted(files)
    else:
        return []


def main():
    print("=" * 60)
    print("批量数据预处理 → 数据库")
    print("=" * 60)

    # 命令行参数 > 默认配置
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = DATA_DIR

    print(f"\n目标路径：{target_path}")

    if not os.path.exists(target_path):
        print(f"✗ 路径不存在：{target_path}")
        return

    # 收集文件
    files = collect_files(target_path)
    if not files:
        print("✗ 没有找到任何数据文件")
        return

    print(f"✓ 找到 {len(files)} 个文件\n")
    print("-" * 60)

    # 逐个读取
    all_dfs = []
    for f in files:
        df = read_one_file(f)
        if df is not None and not df.empty:
            all_dfs.append(df)

    if not all_dfs:
        print("\n✗ 没有有效数据")
        return

    print("-" * 60)

    # 合并
    final_df = pd.concat(all_dfs, ignore_index=True)

    # 清洗
    print("\n清洗数据...")
    final_df = final_df.dropna(subset=['spot_name', 'comment'])
    final_df['spot_name'] = final_df['spot_name'].astype(str).str.strip()
    final_df['comment'] = final_df['comment'].astype(str).str.strip()
    final_df = final_df[final_df['comment'].str.len() > 2]
    final_df = final_df[final_df['spot_name'].str.len() > 0]

    # 评分和日期清洗
    final_df['sentiment_score'] = final_df['sentiment_score'].apply(clean_score)
    final_df['comment_date'] = final_df['comment_date'].apply(clean_date)

    # 保留候选重复记录，交给审核批次的身份核对，不按景点+正文粗暴丢行。
    print(f"  保留 {len(final_df)} 条；重复身份候选将在审核工作台标记")

    print(f"\n合并后总计：{len(final_df)} 条")
    print(f"\n景点分布：")
    print(final_df['spot_name'].value_counts())

    # 送入审核暂存区，禁止本脚本绕过人工复核直写正式表。
    print("\n" + "-" * 60)
    print("创建评论审核批次...")
    print("-" * 60)

    try:
        from review.service import create_rows_batch
        batch_id = create_rows_batch(final_df.to_dict('records'), 'csv',
                                     filename=os.path.basename(target_path))
        print(f"✓ 已创建审核批次：{batch_id}（{len(final_df)} 条）")
        print("  打开网页「数据审核」完成复核后再发布到正式评论表")
    except Exception as e:
        print(f"✗ 创建审核批次失败：{e}")
        import traceback
        traceback.print_exc()

    # 更新主 CSV
    print("\n更新主 CSV...")
    try:
        export_df = final_df.rename(columns={
            'spot_name':       '景点名称',
            'user_name':       '昵称',
            'sentiment_score': '评分',
            'comment':         '评论',
            'comment_date':    '日期',
        })
        # 保留需要的列
        keep_cols = ['景点名称', '昵称', '评分', '评论', '日期']
        export_df = export_df[[c for c in keep_cols if c in export_df.columns]]
        export_df.insert(0, '序号', range(1, len(export_df) + 1))
        export_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        print(f"✅ 主 CSV 已更新：{OUTPUT_CSV}")
    except Exception as e:
        print(f"✗ CSV 更新失败：{e}")

    print("\n" + "=" * 60)
    print(f"✅ 全部完成！共处理 {len(final_df)} 条数据")
    print("=" * 60)


if __name__ == "__main__":
    main()
