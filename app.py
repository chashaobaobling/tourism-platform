"""
app.py - Flask Web服务器 V5 (lazy init compatibility patch)

Changes made:
- Delay creation of TourismDataProcessor to a background thread to avoid import-time blocking.
- Read configuration from environment variables: ALLOWED_ORIGINS, APP_DEBUG.
- Limit CORS to configured origins (fallback to localhost origins).
- Add /api/processor_status to report initialization state: initializing / ready / failed.
- Add a before_request guard to return a friendly 202/503 response when processor is not ready, while allowing a small whitelist of endpoints (processor_status, xian_geojson, and root/ static resources).
- Preserve all existing routes and their logic unchanged; routes under /api/* will be blocked until processor is ready to avoid attribute errors.
- Keep `python app.py` compatibility and Windows-friendly behavior.

Notes:
- This patch avoids modifying data_processor.py to minimize behavioral risk. The background thread constructs the real TourismDataProcessor instance.
- Only one background thread performs initialization; thread-safety is ensured by acquiring a lock during assignment.
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import threading
import logging
import time

# Keep compatibility: import the heavy class but don't instantiate it at import-time
from data_processor import TourismDataProcessor

app = Flask(__name__, static_folder='static', template_folder='templates')

# Read configuration from environment
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS')
if ALLOWED_ORIGINS:
    # support comma separated
    origins = [o.strip() for o in ALLOWED_ORIGINS.split(',') if o.strip()]
else:
    origins = ['http://localhost:3000', 'http://127.0.0.1:3000']

APP_DEBUG = os.environ.get('APP_DEBUG', 'false').lower() in ('1', 'true', 'yes')

app.config['APP_DEBUG'] = APP_DEBUG

# Configure CORS with allowed origins for /api/*
CORS(app, resources={r"/api/*": {"origins": origins}})

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Module-level processor holder and state
processor = None
processor_lock = threading.Lock()
processor_init_error = None
processor_init_started = False

# Whitelisted paths that are allowed before processor initialization completes
_WHITELISTED_API_PATHS = set([
    '/api/processor_status',
    '/api/xian_geojson',
])


def _initialize_processor_in_background():
    global processor, processor_init_error
    try:
        logger.info('Processor initialization thread starting...')
        # construct the heavy object (may take time)
        p = TourismDataProcessor()
        with processor_lock:
            processor = p
        logger.info('Processor initialized successfully')
    except Exception as e:
        logger.exception('Processor initialization failed: %s', e)
        processor_init_error = str(e)


# Start background initialization lazily on first request if not already started
def ensure_processor_initialization():
    global processor_init_started
    if processor is None and not processor_init_started:
        processor_init_started = True
        t = threading.Thread(target=_initialize_processor_in_background, daemon=True)
        t.start()


@app.before_request
def _check_processor_ready():
    # Only guard API endpoints; static and root pages are allowed
    path = request.path
    if not path.startswith('/api/'):
        return None

    # Always allow whitelisted API endpoints
    if path in _WHITELISTED_API_PATHS:
        return None

    # If processor is ready, allow
    if processor is not None:
        return None

    # If initialization failed, return 503
    if processor_init_error is not None:
        return jsonify({'status': 'error', 'message': '初始化失败', 'detail': processor_init_error}), 503

    # Not ready yet: ensure initialization started and return 202
    ensure_processor_initialization()
    return jsonify({'status': 'initializing', 'message': '数据正在初始化，请稍后重试'}), 202


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/processor_status')
def api_processor_status():
    state = 'ready' if processor is not None else ('failed' if processor_init_error else 'initializing')
    return jsonify({'status': 'success', 'data': {'state': state, 'error': processor_init_error}})


# === existing routes kept as-is ===

@app.route('/api/overview')
def api_overview():
    try:
        return jsonify({'status':'success','data': processor.get_overview_with_change()})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/rankings')
def api_rankings():
    try:
        top_n = request.args.get('top_n', 20, type=int)
        return jsonify({'status':'success','data': processor.get_spot_rankings(top_n)})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/spot/<spot_name>')
def api_spot_detail(spot_name):
    try:
        data = processor.get_spot_detail(spot_name)
        if data is None:
            return jsonify({'status':'error','message':'景点未找到'}), 404
        return jsonify({'status':'success','data': data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/ai_keywords')
def api_ai_keywords():
    try:
        spot_name = request.args.get('spot_name', None)
        data = processor.get_ai_keywords(spot_name)
        return jsonify({'status':'success','data': data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/ai_spot_analysis')
def api_ai_spot_analysis():
    """景点深度分析专用AI接口"""
    try:
        spot_name = request.args.get('spot_name', '')
        if not spot_name:
            return jsonify({'status':'error','message':'请指定景点'}), 400
        data = processor.get_ai_spot_analysis(spot_name)
        return jsonify({'status':'success','data': data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/ai_travel_plan')
def api_ai_travel_plan():
    """旅游规划专用AI接口"""
    try:
        spot_name = request.args.get('spot_name', '')
        if not spot_name:
            return jsonify({'status':'error','message':'请指定景点'}), 400
        data = processor.get_ai_travel_plan(spot_name)
        return jsonify({'status':'success','data': data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/ai_operation_model')
def api_ai_operation_model():
    """运营模式专用AI接口"""
    try:
        spot_name = request.args.get('spot_name', '')
        if not spot_name:
            return jsonify({'status':'error','message':'请指定景点'}), 400
        data = processor.get_ai_operation_model(spot_name)
        return jsonify({'status':'success','data': data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/set_engine')
def api_set_engine():
    """切换AI引擎"""
    try:
        engine = request.args.get('engine', '')
        if processor.set_engine(engine):
            return jsonify({'status':'success','data':{'engine':engine}})
        return jsonify({'status':'error','message':'无效引擎，使用 groq 或 zhipu'}), 400
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/current_engine')
def api_current_engine():
    """获取当前AI引擎"""
    try:
        return jsonify({'status':'success','data':{'engine':processor.get_current_engine()}})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/success_factors')
def api_success_factors():
    """成功共性因子"""
    try:
        data = processor.get_success_factors()
        return jsonify({'status':'success','data': data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/db_status')
def api_db_status():
    """数据库状态"""
    try:
        return jsonify({'status':'success','data': processor.get_db_status()})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/add_comment', methods=['POST'])
def api_add_comment():
    """手动添加评论"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status':'error','message':'无数据'}), 400
        required = ['spot_name','comment','sentiment_score']
        for f in required:
            if f not in data:
                return jsonify({'status':'error','message':f'缺少{f}'}), 400
        if processor._db:
            ok = processor._db.add_comment(
                spot_name      = data['spot_name'],
                comment        = data['comment'],
                sentiment_score= int(data['sentiment_score']),
                user_name      = data.get('user_name',''),
                comment_date   = data.get('comment_date',''),
                source         = data.get('source','手动添加')
            )
            if ok:
                # 触发一次即时检测
                processor._check_and_update()
                return jsonify({'status':'success','message':'添加成功'})
        return jsonify({'status':'error','message':'数据库未连接'}), 500
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/force_refresh')
def api_force_refresh():
    """强制全量刷新数据（清空所有缓存）"""
    try:
        total = processor.force_full_reload()
        return jsonify({
            'status': 'success',
            'message': f'刷新完成，共 {total} 条',
            'total': total
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/wordcloud')
def api_wordcloud():
    try:
        spot_name = request.args.get('spot_name', None)
        sentiment = request.args.get('sentiment', None)
        return jsonify({'status':'success',
                        'data': processor.get_wordcloud_data(spot_name, sentiment)})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/comparison')
def api_comparison():
    try:
        spots = request.args.getlist('spots')
        if not spots:
            spots = request.args.get('spots','').split(',')
        spots = [s.strip() for s in spots if s.strip()]
        return jsonify({'status':'success','data': processor.get_comparison_data(spots)})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/heatmap')
def api_heatmap():
    try:
        return jsonify({'status':'success','data': processor.get_heat_map_data()})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/heat_by_period')
def api_heat_by_period():
    try:
        days = request.args.get('days', None, type=int)
        start_date = request.args.get('start', None)
        end_date = request.args.get('end', None)
        return jsonify({'status':'success','data': processor.get_heat_by_period(days, start_date, end_date)})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/spot_trend')
def api_spot_trend():
    try:
        spot_name = request.args.get('spot_name', '')
        start_date = request.args.get('start', None)
        end_date = request.args.get('end', None)
        if not spot_name:
            return jsonify({'status':'error','message':'请指定景点'}), 400
        data = processor.get_spot_monthly_trend(spot_name, start_date, end_date)
        return jsonify({'status':'success','data': data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/ai_insight')
def api_ai_insight():
    try:
        spot_name = request.args.get('spot_name', None)
        if not spot_name:
            return jsonify({'status': 'error', 'message': '缺少 spot_name 参数'}), 400
        data = processor.get_ai_insight(spot_name)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/date_range')
def api_date_range():
    try:
        return jsonify({'status':'success','data': processor.get_date_range()})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/trend')
def api_trend():
    try:
        return jsonify({'status':'success','data': processor.get_trend_analysis()})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/operation_model')
def api_operation_model():
    try:
        return jsonify({'status':'success','data': processor.get_operation_model()})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/keyword_sentiment_heatmap')
def api_keyword_sentiment_heatmap():
    try:
        spot_name = request.args.get('spot_name', None)
        top_n = request.args.get('top_n', 60, type=int)
        data = processor.get_keyword_sentiment_heatmap(spot_name=spot_name, top_n=top_n)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/negative_model')
def api_negative_model():
    try:
        spot_name = request.args.get('spot_name', None)
        top_n = request.args.get('top_n', 10, type=int)
        data = processor.get_negative_factor_model(spot_name=spot_name, top_n=top_n)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/day_plan')
def api_day_plan():
    try:
        spots_str = request.args.get('spots', '')
        spots = [s.strip() for s in spots_str.split(',') if s.strip()]
        if not spots:
            return jsonify({'status':'error','message':'请选择至少一个景点'}), 400
        duration = request.args.get('duration', '一日游')
        start_time = request.args.get('start_time', '08:30')
        transport = request.args.get('transport', '地铁+步行')
        season = request.args.get('season', '不限')  # ✨ 新增
        data = processor.get_ai_day_plan(spots, duration, start_time, transport, season)
        return jsonify({'status':'success','data': data})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/age_data')
def api_age_data():
    try:
        spot_name = request.args.get('spot_name', None)
        # 参数透传，不污染 processor.df（线程安全）
        data = processor.get_4d_visitor_portrait(spot_name=spot_name)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/time_wordcloud')
def api_time_wordcloud():
    try:
        spot_name = request.args.get('spot_name', None)
        # ✅ 直接传参数，不动全局 df
        data = processor.get_dynamic_sentiment_time_wordcloud(
            spot_name=spot_name
        )
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ai_reply', methods=['POST'])
def api_ai_reply():
    """AI差评回复生成"""
    try:
        req = request.get_json()
        review_text = req.get('review_text', '').strip()
        spot_name = req.get('spot_name', '')
        sentiment_score = req.get('sentiment_score', 2)

        if not review_text:
            return jsonify({'status': 'error', 'message': '请输入差评内容'}), 400

        # 拼接prompt
        prompt = f"""你是「{spot_name or '景区'}」的官方客服，请针对游客差评撰写专业的官方回复。

【游客评分】{sentiment_score}/5分
【差评内容】
{review_text}

【回复要求】
1. **必须针对评论中提到的具体问题逐一回应**（如服务态度、卫生、排队、价格等），不要套话
2. 结构要清晰：先共情致歉 → 说明已关注/正在改进 → 邀请再次到访
3. 语气真诚专业，避免"亲爱的游客"这类老套称呼
4. 字数控制在150-250字
5. 如果游客提到了人物（如导游、工作人员），要明确说明会调查处理
6. 如果游客提到了硬件问题（如设施、卫生），要承诺整改时间表

请直接输出回复正文，不要有任何前缀说明。"""

        ai_text = processor._call_ai(prompt, max_tokens=600)
        if ai_text:
            return jsonify({
                'status': 'success',
                'data': {
                    'reply': ai_text,
                    'engine': processor._get_engine_label(),
                    'needs_review': sentiment_score <= 1
                }
            })
        else:
            return jsonify({'status': 'error', 'message': 'AI服务暂时不可用，请稍后重试'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/xian_geojson')
def api_xian_geojson():
    """提供西安区县GeoJSON地图数据"""
    import os
    try:
        geo_path = r"C:\Users\wangjing\Desktop\front_end_practice\tourism_analysis\data\西安市.geojson"
        if not os.path.exists(geo_path):
            return jsonify({'status': 'error', 'message': 'GeoJSON文件不存在'}), 404
        with open(geo_path, 'r', encoding='utf-8') as f:
            import json
            data = json.load(f)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/district_heat')
def api_district_heat():
    """西安各区景点热度聚合数据"""
    try:
        # 景点-区县映射
        district_map = {
            '陕西省历史博物馆': '雁塔区',
            '大雁塔': '雁塔区',
            '青龙寺': '雁塔区',
            '大唐芙蓉园': '雁塔区',
            '大唐不夜城': '雁塔区',
            '西安博物院': '碑林区',
            '钟楼': '碑林区',
            '西安城墙': '碑林区',
            '兵马俑': '临潼区',
            '华清宫': '临潼区',
            '终南山南五台': '长安区',
            '白��原': '灞桥区'
        }

        rankings = processor.get_spot_rankings(top_n=100)
        if not rankings:
            return jsonify({'status': 'success', 'data': []})

        district_data = {}
        for r in rankings:
            district = district_map.get(r['spot_name'])
            if not district:
                print(f"[WARN] 景点未匹配到区县: {r['spot_name']}")
                continue  # 跳过未匹配的景点
            if district not in district_data:
                district_data[district] = {
                    'name': district,
                    'comment_count': 0,
                    'avg_score_sum': 0,
                    'spot_count': 0,
                    'heat_sum': 0,
                    'spots': []
                }
            district_data[district]['comment_count'] += r['comment_count']
            district_data[district]['avg_score_sum'] += r['avg_score']
            district_data[district]['spot_count'] += 1
            district_data[district]['heat_sum'] += r['heat_index']
            district_data[district]['spots'].append({
                'name': r['spot_name'],
                'score': r['avg_score'],
                'heat': r['heat_index']
            })

        result = []
        for d in district_data.values():
            result.append({
                'name': d['name'],
                'value': round(d['heat_sum'] / d['spot_count'], 1),
                'comment_count': d['comment_count'],
                'avg_score': round(d['avg_score_sum'] / d['spot_count'], 2),
                'spot_count': d['spot_count'],
                'spots': d['spots']
            })

        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/hot_potential')
def api_hot_potential():
    try:
        top_n = request.args.get('top_n', 5, type=int)
        data = processor.get_hot_potential(top_n=top_n)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/hot_potential_detail')
def api_hot_potential_detail():
    try:
        spot_name = request.args.get('spot_name', '')
        if not spot_name:
            return jsonify({'status': 'error', 'message': '请指定景点'}), 400
        data = processor.get_hot_potential_detail(spot_name)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/factor_trend_simple')
def api_factor_trend_simple():
    try:
        days = request.args.get('days', 30, type=int)
        data = processor.get_factor_trend_simple(days=days)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/weekday_holiday_diff')
def api_weekday_holiday_diff():
    """工作日 vs 节假日 关键词差异"""
    try:
        spot_name = request.args.get('spot_name', None)
        data = processor.get_weekday_holiday_diff(spot_name=spot_name)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dual_rankings')
def api_dual_rankings():
    try:
        ranking_type = request.args.get('type', 'hot')  # 'hot' / 'quality'
        # 权重参数（可选）
        weights = None
        mfw = request.args.get('mafengwo', type=int)
        ctp = request.args.get('ctrip', type=int)
        dp = request.args.get('dianping', type=int)
        if mfw is not None and ctp is not None and dp is not None:
            weights = {'mafengwo': mfw, 'ctrip': ctp, 'dianping': dp}

        data = processor.get_dual_rankings(weights=weights, ranking_type=ranking_type)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        import traceback
        traceback.print_exc()  # 加这行
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/operation_alerts')
def api_operation_alerts():
    """运营预警面板"""
    try:
        data = processor.get_operation_alerts()
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/holiday_forecast')
def api_holiday_forecast():
    """节假日客流预测"""
    try:
        data = processor.get_holiday_forecast()
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/capability_radar')
def api_capability_radar():
    """景点能力雷达"""
    try:
        spots_str = request.args.get('spots', '')
        spot_names = [s.strip() for s in spots_str.split(',') if s.strip()] if spots_str else None
        data = processor.get_capability_radar(spot_names)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/comparison_advanced')
def api_comparison_advanced():
    """景点对比综合数据"""
    try:
        # 关键修复：先尝试从单个参数里 split
        spots_str = request.args.get('spots', '')
        if spots_str:
            spots = [s.strip() for s in spots_str.split(',') if s.strip()]
        else:
            spots = request.args.getlist('spots')
            spots = [s.strip() for s in spots if s.strip()]

        data = processor.get_comparison_advanced(spots)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ai_comparison_summary')
def api_ai_comparison_summary():
    """AI 综合推荐"""
    try:
        spots = request.args.get('spots', '').split(',')
        spots = [s.strip() for s in spots if s.strip()]
        if len(spots) < 2:
            return jsonify({'status': 'error', 'message': '至少需要2个景点'}), 400
        data = processor.get_ai_comparison_summary(spots)
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    logger.info('\n🌐 访问地址: http://localhost:5000')
    # ensure background initialization starts when running directly
    ensure_processor_initialization()
    app.run(debug=app.config['APP_DEBUG'], host='0.0.0.0', port=5000)
