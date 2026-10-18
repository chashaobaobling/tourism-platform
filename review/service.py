"""Batch orchestration and guarded publishing for the review workspace."""
from __future__ import annotations

import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import text

from . import store
from .identity import content_key, has_stable_identity, identity_key

_workers = ThreadPoolExecutor(max_workers=2, thread_name_prefix='review')
_crawler_lock = threading.Lock()
_db_lock = threading.Lock()
_db_instance = None
_refresh_callback = None
_commit_lock_name = 'tourism_review_comment_publish_v1'


def set_refresh_callback(callback):
    global _refresh_callback
    _refresh_callback = callback


def _db():
    global _db_instance
    if _db_instance is not None:
        return _db_instance if _db_instance.is_connected() else None
    with _db_lock:
        if _db_instance is None:
            from database import TourismDatabase
            _db_instance = TourismDatabase()
    return _db_instance if _db_instance.is_connected() else None


def _identity_index(db):
    """Return normalized identity and content candidates, or None when DB is unavailable."""
    if not db:
        return None
    with db.engine.connect() as conn:
        result = conn.execute(text('''SELECT id,spot_name,comment,user_name,comment_date
            FROM comments ORDER BY id'''))
        index = {'full': {}, 'content': {}}
        for row in result.mappings():
            comment_id = int(row['id'])
            index['full'].setdefault(identity_key(row), []).append(comment_id)
            index['content'].setdefault(content_key(row), []).append(comment_id)
    return index


def _identity_rows(rows, index):
    # Duplicate source rows must be explicitly resolved; never let one silently overwrite another.
    key_counts = {}
    for row in rows:
        key_counts[row['identity_key']] = key_counts.get(row['identity_key'], 0) + 1
    output = []
    for number, row in enumerate(rows, start=1):
        key = row['identity_key']
        exact = (index or {}).get('full', {}).get(key, [])
        similar = (index or {}).get('content', {}).get(content_key(row), [])
        candidates = exact or similar
        if key_counts[key] > 1:
            status = 'duplicate_in_batch'
        elif index is None:
            status = 'db_unavailable'
        elif not has_stable_identity(row):
            status = 'incomplete'
        elif len(exact) > 1:
            status = 'ambiguous'
        elif exact:
            status = 'matched'
        elif similar:
            status = 'possible_match'
        else:
            status = 'new'
        output.append((number, status, candidates))
    return output


def _prepare_rows(rows, source):
    def clean_value(value):
        if value is None:
            return ''
        text_value = str(value).strip()
        return '' if text_value.casefold() in {'nan', 'none', 'null'} else text_value

    prepared = []
    for row in rows:
        item = {
            'spot_name': clean_value(row.get('spot_name')),
            'comment': clean_value(row.get('comment')),
            'sentiment_score': int(row['sentiment_score']),
            'user_name': clean_value(row.get('user_name')),
            'comment_date': clean_value(row.get('comment_date')),
            'source': (clean_value(row.get('source')) or source)[:50],
        }
        item['identity_key'] = identity_key(item)
        prepared.append(item)
    return prepared


def create_csv_batch(rows, filename):
    return create_rows_batch(rows, 'csv', filename=filename)


def create_rows_batch(rows, source, filename=None, spot_name=''):
    batch_id = uuid.uuid4().hex
    prepared = _prepare_rows(rows, 'CSV导入' if source == 'csv' else '携程爬虫')
    store.create_batch(batch_id, source, filename, spot_name, prepared)
    _start_evaluation(batch_id, prepared)
    return batch_id


def create_crawler_batch(spot_name, url, pages):
    batch_id = uuid.uuid4().hex
    store.create_batch(batch_id, 'ctrip', None, spot_name, [])
    store.update_batch(batch_id, status='crawling')
    _workers.submit(_crawl_and_evaluate, batch_id, spot_name, url, pages)
    return batch_id


def _crawl_and_evaluate(batch_id, spot_name, url, pages):
    if not _crawler_lock.acquire(blocking=False):
        store.update_batch(batch_id, status='failed', error='已有携程爬取任务运行中，请稍后再试。')
        return
    try:
        from spider_pipeline import preprocess_reviews, scrape_spot
        raw = scrape_spot(spot_name, url, pages, headless=True)
        df = preprocess_reviews(spot_name, raw)
        if df is None or df.empty:
            store.update_batch(batch_id, status='failed', error='没有抓取到可审核的有效评论。')
            return
        rows = df.to_dict('records')
        prepared = _prepare_rows(rows, '携程爬虫')
        store.append_batch_rows(batch_id, prepared)
        db = _db()
        index = _identity_index(db)
        store.update_identities(batch_id, _identity_rows(prepared, index))
        _evaluate_rows(batch_id, prepared)
    except Exception as exc:
        store.update_batch(batch_id, status='failed', error=f'爬取或模型评估失败：{exc}')
    finally:
        _crawler_lock.release()


def _start_evaluation(batch_id, rows):
    _workers.submit(_evaluate_rows, batch_id, rows)


def _evaluate_rows(batch_id, rows):
    try:
        store.update_batch(batch_id, status='matching')
        db = _db()
        index = _identity_index(db)
        store.update_identities(batch_id, _identity_rows(rows, index))
        rows = store.get_batch_rows(batch_id)
        store.update_batch(batch_id, status='evaluating', processed_rows=0)
        from .pipeline import predict_and_compare
        chunk_size = 64
        for start in range(0, len(rows), chunk_size):
            results = predict_and_compare(rows[start:start + chunk_size])
            store.set_predictions(batch_id, start + 1, results)
            store.update_batch(batch_id, status='evaluating', processed_rows=min(start + chunk_size, len(rows)))
        store.update_batch(batch_id, status='ready', processed_rows=len(rows))
    except Exception as exc:
        store.update_batch(batch_id, status='failed', error=f'模型评估失败：{exc}')


def submit_decision(item_id, action, score=None, candidate_id=None, resolution=None, note=None):
    item = store.get_item(item_id)
    if not item:
        raise ValueError('找不到这条审核记录。')
    batch = store.get_batch(item['batch_id'])
    if batch and batch['status'] == 'committing':
        raise ValueError('数据库正在写入此批次，暂时不能更改审核决定。')
    if item['review_status'] in {'written', 'rejected'}:
        raise ValueError('该记录已写入或已跳过，不能重复处理。')

    status = item['identity_status']
    resolved_id = None
    if status in {'ambiguous', 'possible_match', 'incomplete', 'db_unavailable'}:
        if candidate_id is not None:
            try:
                candidate_id = int(candidate_id)
            except (TypeError, ValueError):
                raise ValueError('请选择有效的数据库记录 ID。')
            if candidate_id not in item['candidate_ids']:
                raise ValueError('所选数据库 ID 不在这条记录的候选范围内，请刷新后重选。')
            resolved_id = candidate_id
        elif resolution == 'new' and (status == 'possible_match' and has_stable_identity(item)
                                      or status in {'incomplete', 'db_unavailable'}):
            pass
        elif action == 'skip':
            store.mark_skipped(item_id)
            return
        else:
            raise ValueError('这条评论的唯一标识无法自动确认。请选择匹配的数据库 ID、明确按新评论保留，或跳过。')
    elif status == 'duplicate_in_batch':
        if action == 'skip':
            store.mark_skipped(item_id, '批次内重复记录，人工选择跳过')
            return
        if resolution != 'new':
            raise ValueError('该评论在导入批次中重复。请选择保留为新记录或跳过。')
    elif status not in {'new', 'matched'}:
        raise ValueError('该记录的身份状态尚未确认，暂不能审核。')

    if action == 'skip':
        store.mark_skipped(item_id)
        return
    if action == 'keep':
        reviewed_rating = int(item['sentiment_score'])
        reviewed_class = item['source_class']
        decision = 'keep_source_rating'
    elif action == 'model':
        reviewed_rating = int(item['sentiment_score'])
        reviewed_class = item['model_predicted_class']
        decision = 'accept_model_class_keep_numeric_rating'
    elif action == 'manual':
        try:
            reviewed_rating = int(score)
        except (TypeError, ValueError):
            raise ValueError('手动修正时请选择 1–5 的整数评分。')
        if reviewed_rating not in {1, 2, 3, 4, 5}:
            raise ValueError('手动评分只能是 1–5。')
        from .config import LABELS, RATING_TO_LABEL
        reviewed_class = LABELS[RATING_TO_LABEL[reviewed_rating]]
        decision = 'manual_rating'
    else:
        raise ValueError('未知审核操作。')
    if resolution == 'new' and status in {'possible_match', 'incomplete', 'db_unavailable', 'duplicate_in_batch'}:
        decision = 'insert_as_new:' + decision
    store.update_decision(item_id, 'approved', decision, reviewed_rating,
                          reviewed_class, note, resolved_id)


def _load_comment_index(conn):
    index = {'full': {}, 'content': {}}
    result = conn.execute(text('''SELECT id,spot_name,comment,user_name,comment_date
        FROM comments ORDER BY id'''))
    for row in result.mappings():
        comment_id = int(row['id'])
        index['full'].setdefault(identity_key(row), []).append(comment_id)
        index['content'].setdefault(content_key(row), []).append(comment_id)
    return index


def _validate_comments_schema(conn):
    columns = {row[0] for row in conn.execute(text('SHOW COLUMNS FROM comments')).all()}
    required = {'id', 'spot_name', 'comment', 'sentiment_score', 'user_name', 'comment_date', 'source'}
    missing = sorted(required - columns)
    if missing:
        raise RuntimeError('comments 表缺少必要字段：' + ', '.join(missing))


def publish_batch(batch_id):
    """Serialize writers and re-resolve every identity inside one MySQL transaction."""
    batch = store.get_batch(batch_id)
    if not batch:
        raise ValueError('找不到审核批次。')
    if batch['status'] not in {'ready', 'partially_written', 'committing'}:
        raise ValueError('批次尚未完成模型评估，暂不能写入。')
    items = store.get_commit_items(batch_id)
    if not items:
        raise ValueError('没有已通过且可写入的记录。')
    db = _db()
    if not db:
        raise RuntimeError('数据库当前不可用；批次仍保留在暂存区，未写入任何数据。')

    written, blocked, lock_held = [], [], False
    with db.engine.connect() as conn:
        try:
            lock_result = conn.execute(text('SELECT GET_LOCK(:name, 15)'), {'name': _commit_lock_name}).scalar()
            conn.commit()
            if lock_result != 1:
                raise RuntimeError('无法取得数据库写入锁，暂未写入。请稍后重试。')
            lock_held = True
            with conn.begin():
                _validate_comments_schema(conn)
                identity_index = _load_comment_index(conn)
                staged_keys = set()
                staged_targets = set()
                for item in items:
                    key = item['identity_key']
                    status = item['identity_status']
                    exact_candidates = identity_index['full'].get(key, [])
                    similar_candidates = identity_index['content'].get(content_key(item), [])
                    candidates = exact_candidates or similar_candidates
                    selected_id = item.get('resolved_existing_id')
                    if key in staged_keys:
                        blocked.append((item, '本次写入批次含重复唯一标识，未创建重复记录。'))
                        continue
                    if status == 'manual_new' and exact_candidates and selected_id is None:
                        store.update_identity(batch_id, item['row_number'], 'ambiguous', exact_candidates)
                        blocked.append((dict(item, resolved_existing_id=None),
                                        '确认新建的身份键已匹配到数据库候选，请改选目标记录或跳过。'))
                        continue
                    if status == 'manual_new' and similar_candidates and not exact_candidates \
                            and not has_stable_identity(item) and selected_id is None:
                        store.update_identity(batch_id, item['row_number'], 'incomplete', similar_candidates)
                        blocked.append((dict(item, resolved_existing_id=None),
                                        '缺少昵称或日期，且评论正文存在相似记录，请先选定目标记录。'))
                        continue
                    if selected_id is not None:
                        if int(selected_id) not in candidates:
                            refreshed_status = 'ambiguous' if len(exact_candidates) > 1 else 'possible_match'
                            store.update_identity(batch_id, item['row_number'], refreshed_status, candidates)
                            blocked.append((dict(item, resolved_existing_id=None),
                                            '选择的目标记录已变化，请重新匹配。'))
                            continue
                        target_id = int(selected_id)
                    elif status == 'duplicate_in_batch' and not str(item.get('decision') or '').startswith('insert_as_new:'):
                        blocked.append((item, '批次内存在重复评论，需先明确保留哪一条。'))
                        continue
                    elif len(exact_candidates) > 1:
                        store.update_identity(batch_id, item['row_number'], 'ambiguous', exact_candidates)
                        blocked.append((item, '数据库中存在多个完全匹配身份候选，未自动覆盖。'))
                        continue
                    elif len(exact_candidates) == 1:
                        target_id = exact_candidates[0]
                    elif similar_candidates and status != 'manual_new':
                        store.update_identity(batch_id, item['row_number'], 'possible_match', similar_candidates)
                        blocked.append((dict(item, resolved_existing_id=None),
                                        '景点与评论正文存在相同记录，但昵称或日期不同；请确认更新哪条或另存新记录。'))
                        continue
                    else:
                        if status in {'incomplete', 'db_unavailable', 'duplicate_in_batch'} and not str(
                            item.get('decision') or ''
                        ).startswith('insert_as_new:'):
                            blocked.append((item, '缺少稳定标识，未写入。'))
                            continue
                        target_id = None

                    if target_id is not None:
                        if target_id in staged_targets:
                            blocked.append((item, '本批次已有另一条记录选择了同一数据库 ID，避免重复覆盖，请跳过其中一条。'))
                            continue
                        conn.execute(text('UPDATE comments SET sentiment_score=:score WHERE id=:id'),
                                     {'score': int(item['reviewed_rating'] or item['sentiment_score']), 'id': target_id})
                        written.append((int(item['item_id']), target_id))
                        staged_targets.add(target_id)
                        staged_keys.add(key)
                        continue

                    result = conn.execute(text('''INSERT INTO comments
                        (spot_name,comment,sentiment_score,user_name,comment_date,source)
                        VALUES (:spot,:comment,:score,:user,:date,:source)'''), {
                            'spot': item['spot_name'], 'comment': item['comment'],
                            'score': int(item['reviewed_rating'] or item['sentiment_score']),
                            'user': item['user_name'], 'date': item['comment_date'], 'source': item['source'],
                        })
                    new_id = int(result.lastrowid)
                    staged_keys.add(key)
                    staged_targets.add(new_id)
                    identity_index['full'].setdefault(key, []).append(new_id)
                    identity_index['content'].setdefault(content_key(item), []).append(new_id)
                    written.append((int(item['item_id']), new_id))
            store.set_written(batch_id, written)
            if blocked:
                for item, reason in blocked:
                    store.update_decision(int(item['item_id']), 'needs_review', item.get('decision'),
                                          item.get('reviewed_rating'), item.get('reviewed_class'), reason,
                                          item.get('resolved_existing_id'), allow_committing=True,
                                          preserve_identity_status=True)
            updated = store.get_batch(batch_id)
            remaining = sum(1 for row in store.get_batch_rows(batch_id)
                            if row['review_status'] not in {'written', 'rejected'})
            store.update_batch(batch_id, status='completed' if remaining == 0 else 'partially_written')
        finally:
            if lock_held:
                try:
                    if conn.in_transaction():
                        conn.commit()
                    conn.execute(text('SELECT RELEASE_LOCK(:name)'), {'name': _commit_lock_name})
                    conn.commit()
                except Exception:
                    pass
    return {'written': len(written), 'blocked': len(blocked), 'message':
            f'已写入 {len(written)} 条；{len(blocked)} 条因身份冲突或数据变化而保留在审核区。'}


def submit_publish(batch_id):
    batch = store.get_batch(batch_id)
    if not batch:
        raise ValueError('找不到审核批次。')
    if batch['status'] == 'committing':
        raise ValueError('此批次正在写入，请等待完成。')
    if batch['status'] not in {'ready', 'partially_written'}:
        raise ValueError('批次尚未完成模型评估，暂不能写入。')
    if not store.claim_batch_for_publish(batch_id):
        raise ValueError('此批次状态已变化，刷新后再试。')
    return _workers.submit(_publish_and_refresh, batch_id)


def _publish_and_refresh(batch_id):
    try:
        result = publish_batch(batch_id)
        if result['written']:
            try:
                if _refresh_callback:
                    _refresh_callback()
            except Exception:
                pass
        if result['blocked']:
            current = store.get_batch(batch_id)
            if current and current['status'] == 'partially_written':
                store.update_batch(batch_id, status='partially_written', error=result['message'])
    except Exception as exc:
        store.update_batch(batch_id, status='ready', error=str(exc))

