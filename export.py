import io
import csv
from datetime import datetime


def export_memos_to_csv(memos):
    """
    memos: list of tuples
        (id, timestamp, event_date, content, tags,
         stream_start, stream_end, stream_minutes,
         support_score, excitement_score)
    UTF-8 BOM付きCSVのbytesを返す
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "出来事の日付",
        "記録日時",
        "タグ",
        "配信開始",
        "配信終了",
        "配信時間(分)",
        "応援スコア",
        "盛り上がりスコア",
        "本文",
    ])

    for row in memos:
        _, timestamp, event_date, content, tags, \
            stream_start, stream_end, stream_minutes, \
            support_score, excitement_score = row

        writer.writerow([
            event_date,
            timestamp,
            tags or "",
            stream_start or "",
            stream_end or "",
            stream_minutes if stream_minutes is not None else "",
            support_score if support_score is not None else "",
            excitement_score if excitement_score is not None else "",
            content,
        ])

    csv_str = output.getvalue()
    return ("\ufeff" + csv_str).encode("utf-8")


def get_export_filename():
    today = datetime.now().strftime("%Y%m%d")
    return f"ink_memory_lite_export_{today}.csv"
