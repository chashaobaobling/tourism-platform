"""
spider_pipeline.py - 爬虫+预处理+评论审核批次 整合管道
使用方式：python spider_pipeline.py
"""

import time
import re
import os
import sys
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==================== 景点配置表 ====================
# 你可以在这里预先配置好所有景点的URL
# 格式：'景点名称': 'URL'
SPOT_CONFIG = {
    '西安城墙':        'https://you.ctrip.com/sight/xian7/1449.html'
    # 可以继续添加...
}


# ==================== 驱动 ====================

def create_edge_driver(headless=False):
    """创建 Edge 驱动"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    if headless:
        options.add_argument("--headless")

    # 按顺序查找驱动，找到第一个存在的就用
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "msedgedriver.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe",
        r"C:\Windows\msedgedriver.exe",
        r"D:\爬虫\scrapyProject\msedgedriver.exe",
    ]

    driver_path = None
    for path in possible_paths:
        if os.path.exists(path):
            driver_path = path
            break

    if not driver_path:
        print("❌ 找不到msedgedriver.exe！")
        print("请按以下步骤操作：")
        print("1. 打开Edge，地址栏输入 edge://version/ 查看版本号")
        print("2. 去 https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/ 下载对应版本")
        print("3. 把 msedgedriver.exe 放到项目文件夹里")
        print(f"   项目文件夹：{os.path.dirname(os.path.abspath(__file__))}")
        raise Exception("找不到驱动文件")

    print(f"使用驱动: {driver_path}")

    service = Service(driver_path)
    driver = webdriver.Edge(service=service, options=options)
    return driver


# ==================== 爬虫核心 ====================

def click_time_sort(driver):
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='commentModule']/div[4]/span[2]"))
        )
        btn.click()
        time.sleep(3)
        print("✓ 已点击时间排序")
        return True
    except Exception as e:
        print(f"⚠ 时间排序失败: {e}")
        return False


def scrape_single_comment(driver, element):
    """提取单条评论"""
    try:
        try:
            username = element.find_element(By.CSS_SELECTOR, "div.userInfo div.userName").text.strip()
        except:
            username = ""

        try:
            rating_text = element.find_element(By.CSS_SELECTOR, "div.contentInfo div.scroreInfo span").text.strip()
        except:
            rating_text = ""

        try:
            content = element.find_element(By.CSS_SELECTOR, "div.contentInfo div.commentDetail").text.strip()
        except:
            content = ""

        try:
            date_el = element.find_element(By.CSS_SELECTOR,
                "div.contentInfo div.commentFooter div.commentTime")
            date_text = date_el.text.strip()
        except:
            date_text = ""

        try:
            ip = element.find_element(By.CSS_SELECTOR,
                "div.contentInfo div.commentFooter div.commentTime span").text.strip()
            if ip and ip in date_text:
                date_text = date_text.replace(ip, "").strip()
        except:
            pass

        return {
            'username':   username,
            'rating_raw': rating_text,
            'content':    content,
            'date':       date_text
        }
    except Exception as e:
        return None


def _make_review_key(review):
    """为一条评论生成唯一标识"""
    return f"{review['username']}|{review['content']}|{review['date']}"


def is_duplicate_fast(review, seen_set):
    """快速判断评论是否已存在（O(1) 复杂度）"""
    return _make_review_key(review) in seen_set


def get_page_comments(driver, existing):
    """获取当前页评论

    参数：
        existing: 已爬取的评论列表（list of dict），用于去重
    """
    new_reviews = []
    time.sleep(2)

    # 用集合存储已有评论的 key，避免每次翻页都做 O(n^2) 遍历
    seen_set = set()
    for r in existing:
        seen_set.add(_make_review_key(r))

    try:
        items = driver.find_elements(By.CSS_SELECTOR,
                                     "#commentModule > div.commentList > div")
        print(f"   当前页 {len(items)} 条")
        dup = 0
        for item in items:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", item)
            time.sleep(0.2)
            r = scrape_single_comment(driver, item)
            if r and r['content']:
                if not is_duplicate_fast(r, seen_set):
                    new_reviews.append(r)
                    seen_set.add(_make_review_key(r))  # 同页内也要去重
                else:
                    dup += 1
        if dup:
            print(f"   过滤重复 {dup} 条")
    except Exception as e:
        print(f"   提取出错: {e}")
    return new_reviews


def click_next_page(driver):
    """翻页"""
    methods = [
        ("XPATH", "//*[@id='commentModule']/div[6]/ul/li[9]/span/a"),
        ("XPATH", "//a[contains(text(),'下一页')]"),
        ("CSS",   "a[class*='next'], li[class*='next'] a"),
    ]
    for method, selector in methods:
        try:
            if method == "XPATH":
                btn = driver.find_element(By.XPATH, selector)
            else:
                btn = driver.find_element(By.CSS_SELECTOR, selector)
            if btn.is_enabled():
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(3)
                print("   ✓ 翻页成功")
                return True
        except:
            continue
    return False


def scrape_spot(spot_name, url, pages, headless=False):
    """爬取指定景点"""
    print(f"\n{'='*50}")
    print(f"开始爬取：{spot_name}")
    print(f"URL: {url}")
    print(f"目标页数: {pages}")
    print('='*50)

    driver = None
    all_reviews = []

    try:
        driver = create_edge_driver(headless=headless)
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "commentModule"))
        )
        cm = driver.find_element(By.ID, "commentModule")
        driver.execute_script("arguments[0].scrollIntoView(true);", cm)
        time.sleep(2)

        click_time_sort(driver)

        for page in range(1, pages + 1):
            print(f"\n>>> 第 {page}/{pages} 页")
            reviews = get_page_comments(driver, all_reviews)
            all_reviews.extend(reviews)
            print(f"   本页新增 {len(reviews)} 条，累计 {len(all_reviews)} 条")

            if page < pages:
                if not click_next_page(driver):
                    print("无法翻页，提前结束")
                    break
                time.sleep(2)

    except Exception as e:
        print(f"爬取出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

    print(f"\n爬取完成，共 {len(all_reviews)} 条")
    return all_reviews


# ==================== 预处理 ====================

def clean_score(score_raw):
    """
    评分清洗：统一转为1-5的整数
    处理：'5星' '4.5分' '9分' '90' 纯数字 等各种格式
    """
    try:
        if pd.isna(score_raw) or str(score_raw).strip() == '':
            return None
        s = str(score_raw).strip()
        match = re.search(r"(\d+\.?\d*)", s)
        if not match:
            return None
        val = float(match.group(1))

        # 百分制 → 5分制
        if val > 10:
            val = val / 20
        # 10分制 → 5分制
        elif val > 5:
            val = val / 2

        # 四舍五入到整数，并限制在1-5
        val = round(val)
        val = max(1, min(5, int(val)))
        return val
    except:
        return None


def clean_date(date_str):
    """
    日期清洗：统一格式为 YYYY/MM/DD
    处理：'2024年1月1日' '2024-01-01' '2024.01.01' '1天前' 等
    """
    if not date_str or pd.isna(date_str):
        return ''
    s = str(date_str).strip()

    # 已经是标准格式
    if re.match(r'\d{4}/\d{2}/\d{2}', s):
        return s

    # 尝试pandas解析
    try:
        dt = pd.to_datetime(s, errors='coerce')
        if pd.notna(dt):
            return dt.strftime('%Y/%m/%d')
    except:
        pass

    # 提取年月日数字
    nums = re.findall(r'\d+', s)
    if len(nums) >= 3:
        y, m, d = nums[0], nums[1].zfill(2), nums[2].zfill(2)
        return f"{y}/{m}/{d}"
    elif len(nums) == 2:
        return f"2024/{nums[0].zfill(2)}/{nums[1].zfill(2)}"

    return ''


def preprocess_reviews(spot_name, raw_reviews):
    """
    对爬取的原始评论进行预处理
    返回标准化的DataFrame，列名与数据库一致
    """
    if not raw_reviews:
        return pd.DataFrame()

    rows = []
    for r in raw_reviews:
        content = str(r.get('content', '')).strip()
        if len(content) < 3:
            continue

        score = clean_score(r.get('rating_raw', ''))
        if score is None:
            continue
        date = clean_date(r.get('date', ''))
        username = str(r.get('username', '')).strip()

        rows.append({
            'spot_name':       spot_name,
            'comment':         content,
            'sentiment_score': score,
            'user_name':       username,
            'comment_date':    date,
            'source':          '携程爬虫'
        })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    print(f"\n预处理结果：")
    print(f"  有效评论：{len(df)} 条")
    print(f"  评分分布：{df['sentiment_score'].value_counts().sort_index().to_dict()}")
    print(f"  平均评分：{df['sentiment_score'].mean():.2f}")

    return df


# ==================== 备份到CSV ====================

def save_to_csv_backup(df, spot_name):
    """
    同时备份一份CSV到 D:\数据素养\爬虫备份\ 目录
    文件名格式：景点名称_爬取时间.csv
    """
    if df.empty:
        return

    backup_dir = r"D:\数据素养\爬虫备份"
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(backup_dir, f"{spot_name}_{timestamp}.csv")

    # 转换为用户友好的列名
    df_export = df.rename(columns={
        'spot_name':       '景点名称',
        'comment':         '评论内容',
        'sentiment_score': '评分',
        'user_name':       '用户名',
        'comment_date':    '评论时间',
        'source':          '来源'
    })
    df_export.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✅ CSV备份已保存：{filename}")


# ==================== 主函数 ====================

def main():
    print("=" * 60)
    print("   携程景点评论爬虫 - 整合版")
    print("=" * 60)

    # 显示可用景点
    print("\n📍 已配置的景点：")
    spot_list = list(SPOT_CONFIG.keys())
    for i, name in enumerate(spot_list, 1):
        print(f"   {i}. {name}")
    print(f"   {len(spot_list)+1}. 手动输入景点名和URL")

    # 选择景点
    print("\n请选择景点（输入编号）：")
    while True:
        try:
            choice = int(input("编号: ").strip())
            if 1 <= choice <= len(spot_list):
                spot_name = spot_list[choice - 1]
                url = SPOT_CONFIG[spot_name]
                break
            elif choice == len(spot_list) + 1:
                spot_name = input("请输入景点名称（如：华山）: ").strip()
                url = input("请输入携程URL: ").strip()
                break
            else:
                print("请输入有效编号")
        except ValueError:
            print("请输入数字")

    # 输入页数
    print(f"\n已选择：{spot_name}")
    print("请输入爬取页数（每页约10条，建议10-50页）：")
    while True:
        try:
            pages = int(input("页数: ").strip())
            if pages > 0:
                break
            print("请输入大于0的数字")
        except ValueError:
            print("请输入数字")

    print(f"\n🚀 开始任务：{spot_name} × {pages}页")

    # 1. 爬取
    raw_reviews = scrape_spot(spot_name, url, pages)
    if not raw_reviews:
        print("未爬取到任何数据，程序结束")
        return

    # 2. 预处理
    print("\n" + "="*40)
    print("开始预处理...")
    df = preprocess_reviews(spot_name, raw_reviews)
    if df.empty:
        print("预处理后无有效数据")
        return

    # 3. 进入人工审核暂存区，不绕过模型和人工复核直接写正式表。
    print("\n" + "="*40)
    print("创建评论审核批次...")
    from review.service import create_rows_batch
    batch_id = create_rows_batch(df.to_dict('records'), 'ctrip', spot_name=spot_name)

    # 4. CSV备份
    print("\n备份CSV...")
    save_to_csv_backup(df, spot_name)

    # 5. 完成报告
    print("\n" + "="*60)
    print(f"✅ 全部完成！")
    print(f"   景点名称：{spot_name}")
    print(f"   爬取评论：{len(raw_reviews)} 条（含重复）")
    print(f"   有效评论：{len(df)} 条（去重后）")
    print(f"   审核批次：{batch_id}")
    print(f"   数据未直接写入数据库，请打开网页的「数据审核」完成复核和发布")
    print("="*60)


if __name__ == "__main__":
    main()
