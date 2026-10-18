"""Persistent local staging for review batches; formal comments remain untouched here."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from .config import PROJECT_ROOT

STAGING_PATH = PROJECT_ROOT / 'data' / 'review_staging.sqlite3'
_initialized = False
_init_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _connect():
    STAGING_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(STAGING_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout=20000')
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def initialize():
    global _initialized
    with _init_lock:
        if _initialized:
            return
        with _connect() as conn:
            conn.execute('PRAGMA journal_mode=WAL')
            conn.executescript('''
            CREATE TABLE IF NOT EXISTS review_batches (
                batch_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                filename TEXT,
                spot_name TEXT,
                status TEXT NOT NULL,
                total_rows INTEGER NOT NULL DEFAULT 0,
                processed_rows INTEGER NOT NULL DEFAULT 0,
                error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS review_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL REFERENCES review_batches(batch_id),
                row_number INTEGER NOT NULL,
                spot_name TEXT NOT NULL,
                comment TEXT NOT NULL,
                sentiment_score INTEGER NOT NULL,
                user_name TEXT NOT NULL DEFAULT '',
                comment_date TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL,
                identity_key TEXT NOT NULL,
                identity_status TEXT NOT NULL DEFAULT 'pending',
                candidate_ids TEXT NOT NULL DEFAULT '[]',
                resolved_existing_id INTEGER,
                model_predicted_class TEXT,
                model_confidence REAL,
                model_probabilities TEXT,
                source_class TEXT,
                rating_agrees INTEGER,
                review_status TEXT NOT NULL DEFAULT 'queued',
                decision TEXT,
                reviewed_rating INTEGER,
                reviewed_class TEXT,
                review_note TEXT,
                written_comment_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(batch_id, row_number),
                FOREIGN KEY(batch_id) REFERENCES review_batches(batch_id)
            );
            CREATE INDEX IF NOT EXISTS idx_review_items_batch_status
                ON review_items(batch_id, review_status, item_id);
            CREATE INDEX IF NOT EXISTS idx_review_items_identity
                ON review_items(batch_id, identity_key);
            ''')
        _initialized = True


def create_batch(batch_id, source, filename, spot_name, rows):
    initialize()
    now = _now()
    with _connect() as conn:
        conn.execute('''INSERT INTO review_batches
            (batch_id,source,filename,spot_name,status,total_rows,processed_rows,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?)''',
            (batch_id, source, filename, spot_name, 'queued', len(rows), 0, now, now))
        conn.executemany('''INSERT INTO review_items
            (batch_id,row_number,spot_name,comment,sentiment_score,user_name,comment_date,source,
             identity_key,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', [
                (batch_id, i, row['spot_name'], row['comment'], row['sentiment_score'],
                 row.get('user_name', ''), row.get('comment_date', ''), row.get('source', source),
                 row['identity_key'], now, now)
                for i, row in enumerate(rows, start=1)
            ])


def append_batch_rows(batch_id, rows):
    initialize()
    now = _now()
    with _connect() as conn:
        batch = conn.execute('SELECT COALESCE(MAX(row_number),0) FROM review_items WHERE batch_id=?',
                             (batch_id,)).fetchone()[0]
        conn.executemany('''INSERT INTO review_items
            (batch_id,row_number,spot_name,comment,sentiment_score,user_name,comment_date,source,
             identity_key,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', [
                (batch_id, batch + i, row['spot_name'], row['comment'], row['sentiment_score'],
                 row.get('user_name', ''), row.get('comment_date', ''), row.get('source', 'crawler'),
                 row['identity_key'], now, now)
                for i, row in enumerate(rows, start=1)
            ])
        conn.execute('''UPDATE review_batches SET total_rows=total_rows+?,updated_at=? WHERE batch_id=?''',
                     (len(rows), now, batch_id))


def get_batch(batch_id):
    initialize()
    with _connect() as conn:
        row = conn.execute('SELECT * FROM review_batches WHERE batch_id=?', (batch_id,)).fetchone()
        return dict(row) if row else None


def get_latest_batch():
    initialize()
    with _connect() as conn:
        row = conn.execute('SELECT * FROM review_batches ORDER BY created_at DESC LIMIT 1').fetchone()
        return dict(row) if row else None


def claim_batch_for_publish(batch_id):
    initialize()
    with _connect() as conn:
        cursor = conn.execute('''UPDATE review_batches SET status='committing',error=NULL,updated_at=?
            WHERE batch_id=? AND status IN ('ready','partially_written')''', (_now(), batch_id))
        return cursor.rowcount == 1


def update_batch(batch_id, status=None, processed_rows=None, error=None):
    initialize()
    fields, values = [], []
    if status is not None:
        fields.append('status=?')
        values.append(status)
    if processed_rows is not None:
        fields.append('processed_rows=?')
        values.append(int(processed_rows))
    if error is not None:
        fields.append('error=?')
        values.append(str(error)[:1000])
    elif status in {'queued', 'crawling', 'matching', 'evaluating', 'ready', 'completed'}:
        fields.append('error=NULL')
    fields.append('updated_at=?')
    values.extend((_now(), batch_id))
    with _connect() as conn:
        conn.execute(f"UPDATE review_batches SET {', '.join(fields)} WHERE batch_id=?", values)


def update_identity(batch_id, row_number, status, candidate_ids=()):
    initialize()
    with _connect() as conn:
        conn.execute('''UPDATE review_items SET identity_status=?, candidate_ids=?, updated_at=?
            WHERE batch_id=? AND row_number=?''',
            (status, json.dumps(list(candidate_ids)), _now(), batch_id, row_number))


def update_identities(batch_id, identity_rows):
    initialize()
    now = _now()
    with _connect() as conn:
        conn.executemany('''UPDATE review_items SET identity_status=?,candidate_ids=?,updated_at=?
            WHERE batch_id=? AND row_number=?''', [
                (status, json.dumps(list(candidate_ids)), now, batch_id, row_number)
                for row_number, status, candidate_ids in identity_rows
            ])


def set_predictions(batch_id, first_row, predictions):
    initialize()
    now = _now()
    values = []
    for offset, result in enumerate(predictions):
        status = result['review_status']
        values.append((
            result['model_predicted_class'], result['model_confidence'],
            json.dumps(result['model_probabilities'], ensure_ascii=False), result['source_class'],
            int(result['rating_agrees']), status, now, batch_id, first_row + offset
        ))
    with _connect() as conn:
        conn.executemany('''UPDATE review_items SET model_predicted_class=?,model_confidence=?,
            model_probabilities=?,source_class=?,rating_agrees=?,review_status=?,updated_at=?
            WHERE batch_id=? AND row_number=?''', values)


def update_decision(item_id, review_status, decision=None, reviewed_rating=None,
                    reviewed_class=None, review_note=None, resolved_existing_id=None,
                    allow_committing=False, preserve_identity_status=False):
    initialize()
    identity_status = None
    if resolved_existing_id is not None:
        identity_status = 'resolved'
    elif review_status == 'rejected':
        identity_status = 'skipped'
    elif str(decision or '').startswith('insert_as_new:') and not preserve_identity_status:
        identity_status = 'manual_new'
    with _connect() as conn:
        conn.execute('BEGIN IMMEDIATE')
        batch_status = conn.execute('''SELECT b.status FROM review_items i
            JOIN review_batches b ON b.batch_id=i.batch_id WHERE i.item_id=?''', (item_id,)).fetchone()
        if not batch_status:
            raise ValueError('找不到这条审核记录。')
        if batch_status['status'] == 'committing' and not allow_committing:
            raise ValueError('数据库正在写入此批次，暂时不能更改审核决定。')
        conn.execute('''UPDATE review_items SET review_status=?,decision=?,reviewed_rating=?,
            reviewed_class=?,review_note=?,resolved_existing_id=?,
            identity_status=COALESCE(?,identity_status),updated_at=? WHERE item_id=?''',
            (review_status, decision, reviewed_rating, reviewed_class,
             (review_note or '')[:1000] or None, resolved_existing_id,
             identity_status, _now(), item_id))


def set_written(batch_id, written_items):
    initialize()
    now = _now()
    with _connect() as conn:
        conn.executemany('''UPDATE review_items SET review_status='written',written_comment_id=?,updated_at=?
            WHERE item_id=? AND batch_id=?''', [(comment_id, now, item_id, batch_id)
                                                 for item_id, comment_id in written_items])


def list_items(batch_id, page=1, page_size=25, status='all'):
    initialize()
    where, params = 'batch_id=?', [batch_id]
    if status in {'needs_review', 'auto_pass', 'approved', 'rejected', 'written', 'identity_issue'}:
        if status == 'identity_issue':
            where += " AND identity_status NOT IN ('new','matched','resolved','manual_new','skipped')"
        else:
            where += ' AND review_status=?'
            params.append(status)
    offset = (page - 1) * page_size
    with _connect() as conn:
        total = conn.execute(f'SELECT COUNT(*) FROM review_items WHERE {where}', params).fetchone()[0]
        rows = conn.execute(f'''SELECT * FROM review_items WHERE {where}
            ORDER BY CASE WHEN review_status='needs_review' THEN 0 ELSE 1 END,item_id
            LIMIT ? OFFSET ?''', [*params, page_size, offset]).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item['candidate_ids'] = json.loads(item['candidate_ids'] or '[]')
            item['model_probabilities'] = json.loads(item['model_probabilities'] or '{}')
            items.append(item)
        counts = conn.execute('''SELECT
            SUM(CASE WHEN review_status='needs_review' THEN 1 ELSE 0 END) needs_review,
            SUM(CASE WHEN review_status='auto_pass' THEN 1 ELSE 0 END) auto_pass,
            SUM(CASE WHEN review_status='approved' THEN 1 ELSE 0 END) approved,
            SUM(CASE WHEN review_status='written' THEN 1 ELSE 0 END) written,
            SUM(CASE WHEN review_status='rejected' THEN 1 ELSE 0 END) rejected,
            SUM(CASE WHEN identity_status NOT IN ('new','matched','resolved','manual_new','skipped') THEN 1 ELSE 0 END) identity_issues
            FROM review_items WHERE batch_id=?''', (batch_id,)).fetchone()
    return {'items': items, 'total': total, 'counts': {k: int(v or 0) for k, v in dict(counts).items()}}


def get_item(item_id):
    initialize()
    with _connect() as conn:
        row = conn.execute('SELECT * FROM review_items WHERE item_id=?', (item_id,)).fetchone()
        if not row:
            return None
        item = dict(row)
        item['candidate_ids'] = json.loads(item['candidate_ids'] or '[]')
        item['model_probabilities'] = json.loads(item['model_probabilities'] or '{}')
        return item


def get_commit_items(batch_id):
    initialize()
    with _connect() as conn:
        rows = conn.execute('''SELECT * FROM review_items WHERE batch_id=?
            AND review_status IN ('auto_pass','approved') ORDER BY item_id''', (batch_id,)).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item['candidate_ids'] = json.loads(item['candidate_ids'] or '[]')
            items.append(item)
        return items


def get_batch_rows(batch_id):
    initialize()
    with _connect() as conn:
        rows = conn.execute('SELECT * FROM review_items WHERE batch_id=? ORDER BY row_number',
                            (batch_id,)).fetchall()
        return [dict(row) for row in rows]


def mark_skipped(item_id, note='人工选择跳过，不写入正式评论表'):
    update_decision(item_id, 'rejected', decision='skip', review_note=note)
