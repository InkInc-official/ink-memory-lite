import os
import sqlite3
from datetime import datetime


def get_db_path():
    APP_DATA = os.path.join(os.path.expanduser("~"), ".local", "share", "ink_memory_lite")
    os.makedirs(APP_DATA, exist_ok=True)
    return os.path.join(APP_DATA, "ink_memory_lite.db")


def get_conn():
    return sqlite3.connect(get_db_path(), check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS liver_info (
            id        INTEGER PRIMARY KEY,
            name      TEXT NOT NULL,
            first_stream TEXT,
            birthday  TEXT,
            platform  TEXT,
            memo      TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS memos (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp           TEXT NOT NULL,
            event_date          TEXT NOT NULL,
            content             TEXT NOT NULL,
            tags                TEXT,
            stream_start        TEXT,
            stream_end          TEXT,
            stream_minutes      INTEGER,
            support_score       INTEGER,
            excitement_score    INTEGER
        )
    """)

    # 既存DBへのマイグレーション（列がなければ追加）
    existing_cols = [row[1] for row in c.execute("PRAGMA table_info(memos)").fetchall()]
    migrations = [
        ("stream_start",     "TEXT"),
        ("stream_end",       "TEXT"),
        ("stream_minutes",   "INTEGER"),
        ("support_score",    "INTEGER"),
        ("excitement_score", "INTEGER"),
    ]
    for col, col_type in migrations:
        if col not in existing_cols:
            c.execute(f"ALTER TABLE memos ADD COLUMN {col} {col_type}")

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    defaults = [
        ("office_name", ""),
        ("activity_start_date", ""),
    ]
    for key, val in defaults:
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))

    conn.commit()
    return conn


# ─── settings ───────────────────────────────────────────
def get_setting(conn, key):
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    return row[0] if row else ""


def set_setting(conn, key, value):
    conn.cursor().execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)
    )
    conn.commit()


# ─── liver_info ──────────────────────────────────────────
def count_livers(conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM liver_info")
    return c.fetchone()[0]


def get_liver(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM liver_info LIMIT 1")
    return c.fetchone()


def insert_liver(conn, name, first_stream, birthday, platform, memo):
    conn.cursor().execute(
        "INSERT INTO liver_info (name, first_stream, birthday, platform, memo) VALUES (?,?,?,?,?)",
        (name, first_stream, birthday, platform, memo),
    )
    conn.commit()


def update_liver(conn, liver_id, first_stream, birthday, platform, memo):
    conn.cursor().execute(
        "UPDATE liver_info SET first_stream=?, birthday=?, platform=?, memo=? WHERE id=?",
        (first_stream, birthday, platform, memo, liver_id),
    )
    conn.commit()


def delete_liver(conn, liver_id):
    conn.cursor().execute("DELETE FROM liver_info WHERE id=?", (liver_id,))
    conn.commit()


# ─── memos ───────────────────────────────────────────────
def calc_stream_minutes(start: str, end: str):
    """
    HH:MM 形式の開始・終了から配信時間（分）を計算する。
    終了が開始より小さい場合は日またぎとして翌日扱い。
    """
    if not start or not end:
        return None
    try:
        sh, sm = map(int, start.split(":"))
        eh, em = map(int, end.split(":"))
        total_start = sh * 60 + sm
        total_end   = eh * 60 + em
        if total_end <= total_start:
            total_end += 24 * 60  # 日またぎ
        return total_end - total_start
    except Exception:
        return None


def insert_memo(
    conn,
    event_date,
    content,
    tags,
    stream_start="",
    stream_end="",
    support_score=None,
    excitement_score=None,
):
    now_ts = datetime.now().strftime("%Y/%m/%d %H:%M")
    formatted_tags = " ".join(
        [f"#{t.strip().replace('#', '')}" for t in tags.split() if t.strip()]
    )
    minutes = calc_stream_minutes(stream_start, stream_end)
    conn.cursor().execute(
        """INSERT INTO memos
           (timestamp, event_date, content, tags,
            stream_start, stream_end, stream_minutes,
            support_score, excitement_score)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (now_ts, event_date, content, formatted_tags,
         stream_start or None, stream_end or None, minutes,
         support_score, excitement_score),
    )
    conn.commit()


def get_memos(conn, keyword="", tag_filter="", date_from=None, date_to=None):
    query = """
        SELECT id, timestamp, event_date, content, tags,
               stream_start, stream_end, stream_minutes,
               support_score, excitement_score
        FROM memos WHERE 1=1
    """
    params = []

    if keyword:
        query += " AND (content LIKE ? OR tags LIKE ?)"
        params += [f"%{keyword}%", f"%{keyword}%"]

    if tag_filter:
        query += " AND tags LIKE ?"
        params.append(f"%{tag_filter}%")

    if date_from:
        query += " AND event_date >= ?"
        params.append(date_from)

    if date_to:
        query += " AND event_date <= ?"
        params.append(date_to)

    query += " ORDER BY event_date DESC, timestamp DESC"
    c = conn.cursor()
    c.execute(query, params)
    return c.fetchall()


def get_memo_by_id(conn, memo_id):
    c = conn.cursor()
    c.execute("SELECT * FROM memos WHERE id=?", (memo_id,))
    return c.fetchone()


def update_memo(
    conn,
    memo_id,
    event_date,
    content,
    tags,
    stream_start="",
    stream_end="",
    support_score=None,
    excitement_score=None,
):
    formatted_tags = " ".join(
        [f"#{t.strip().replace('#', '')}" for t in tags.split() if t.strip()]
    )
    minutes = calc_stream_minutes(stream_start, stream_end)
    conn.cursor().execute(
        """UPDATE memos
           SET event_date=?, content=?, tags=?,
               stream_start=?, stream_end=?, stream_minutes=?,
               support_score=?, excitement_score=?
           WHERE id=?""",
        (event_date, content, formatted_tags,
         stream_start or None, stream_end or None, minutes,
         support_score, excitement_score,
         memo_id),
    )
    conn.commit()


def delete_memo(conn, memo_id):
    conn.cursor().execute("DELETE FROM memos WHERE id=?", (memo_id,))
    conn.commit()


def count_memos(conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM memos")
    return c.fetchone()[0]
