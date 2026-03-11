import os
import base64
from datetime import datetime, date

import streamlit as st

from db import (
    init_db,
    get_setting, set_setting,
    get_liver, insert_liver, update_liver, delete_liver,
    insert_memo, get_memos, update_memo, delete_memo,
    count_memos,
)
from export import export_memos_to_csv, get_export_filename

# ─── ページ設定 ──────────────────────────────────────────
st.set_page_config(
    page_title="Ink Memory Lite",
    page_icon="🖋️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── フォント ────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(BASE_DIR, "fonts", "ZenOldMincho-Regular.ttf")


def get_font_css(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"""
    <style>
    @font-face {{
        font-family: 'Zen Old Mincho';
        src: url(data:font/ttf;base64,{data}) format('truetype');
    }}
    html, body, [class*="css"] {{
        font-family: 'Zen Old Mincho', serif;
    }}
    .stMarkdown, p, label, .stSelectbox div, h1, h2, h3 {{
        font-family: 'Zen Old Mincho', serif !important;
    }}
    textarea, input {{
        font-family: 'Zen Old Mincho', serif !important;
    }}
    </style>
    """


if os.path.exists(font_path):
    st.markdown(get_font_css(font_path), unsafe_allow_html=True)

# ─── テーマCSS ───────────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background-color: #0f0f0f;
    color: #e8e8e8;
}
[data-testid="stSidebar"] {
    background-color: #141414;
    border-right: 1px solid #2a2a2a;
}
.stTabs [data-baseweb="tab-list"] {
    background-color: #141414;
    border-bottom: 1px solid #2a2a2a;
}
.stTabs [data-baseweb="tab"] { color: #888; }
.stTabs [aria-selected="true"] {
    color: #e8e8e8 !important;
    border-bottom: 2px solid #e8e8e8 !important;
}
.stButton > button {
    background-color: #1a1a1a;
    color: #e8e8e8;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background-color: #2a2a2a;
    border-color: #888;
}
.stButton > button[kind="primary"] {
    background-color: #e8e8e8;
    color: #0f0f0f;
    border: none;
    font-weight: bold;
}
.stButton > button[kind="primary"]:hover { background-color: #ffffff; }
.stTextArea textarea, .stTextInput input {
    background-color: #1a1a1a !important;
    color: #e8e8e8 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 4px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #888 !important;
    box-shadow: none !important;
}
.stSelectbox > div > div {
    background-color: #1a1a1a !important;
    color: #e8e8e8 !important;
    border: 1px solid #2a2a2a !important;
}
.stDateInput input {
    background-color: #1a1a1a !important;
    color: #e8e8e8 !important;
}
.stNumberInput input {
    background-color: #1a1a1a !important;
    color: #e8e8e8 !important;
    border: 1px solid #2a2a2a !important;
}
.stAlert {
    background-color: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    color: #e8e8e8 !important;
}
hr { border-color: #2a2a2a !important; }
.streamlit-expanderHeader {
    background-color: #1a1a1a !important;
    color: #e8e8e8 !important;
}
.stCaption { color: #666 !important; }
.pro-banner {
    background-color: #1a1a1a;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    padding: 12px 16px;
    margin-top: 8px;
    text-align: center;
}
.pro-banner a {
    color: #e8e8e8;
    text-decoration: none;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
}
.pro-banner a:hover { text-decoration: underline; }
.pro-label {
    font-size: 0.7rem;
    color: #888;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.score-hint {
    font-size: 0.72rem;
    color: #555;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# ─── DB初期化 ────────────────────────────────────────────
conn = init_db()

# ─── サイドバー ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🖋️ Ink Memory Lite")
    st.divider()

    start_date_str = get_setting(conn, "activity_start_date")
    if start_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, "%Y/%m/%d")
            days_elapsed = (datetime.now() - start_dt).days
            today = datetime.now()
            try:
                next_anniv = start_dt.replace(year=today.year)
                if next_anniv <= today:
                    next_anniv = start_dt.replace(year=today.year + 1)
            except ValueError:
                next_anniv = start_dt.replace(year=today.year + 1, day=28)
            days_to_anniv = (next_anniv - today).days

            st.subheader("📅 活動の歩み")
            st.caption(f"活動開始から : **{days_elapsed}** 日目")
            st.caption(f"次の記念日まで : あと **{days_to_anniv}** 日")
            st.write("")
        except ValueError:
            pass

    liver = get_liver(conn)
    if liver:
        _, name, first_stream, birthday, platform, _ = liver

        if birthday:
            try:
                this_year = datetime.now().year
                bday_dt = datetime.strptime(f"{this_year}/{birthday}", "%Y/%m/%d")
                if bday_dt.date() < date.today():
                    bday_dt = datetime.strptime(f"{this_year + 1}/{birthday}", "%Y/%m/%d")
                days_to_bday = (bday_dt.date() - date.today()).days
                st.subheader("🎂 誕生日まで")
                if days_to_bday == 0:
                    st.caption(f"🎉 今日は {name} の誕生日！")
                else:
                    st.caption(f"{name} : あと **{days_to_bday}** 日")
                st.write("")
            except ValueError:
                pass

        if first_stream:
            try:
                fs_md = datetime.strptime(first_stream, "%Y/%m/%d").strftime("%m/%d")
                this_year = datetime.now().year
                fest_dt = datetime.strptime(f"{this_year}/{fs_md}", "%Y/%m/%d")
                if fest_dt.date() < date.today():
                    fest_dt = datetime.strptime(f"{this_year + 1}/{fs_md}", "%Y/%m/%d")
                days_to_fest = (fest_dt.date() - date.today()).days
                st.subheader("🎊 配信記念日まで")
                if days_to_fest == 0:
                    st.caption(f"🎉 今日は {name} の配信記念日！")
                else:
                    st.caption(f"{name} : あと **{days_to_fest}** 日")
                st.write("")
            except ValueError:
                pass

    total = count_memos(conn)
    st.subheader("📝 総ログ数")
    st.caption(f"**{total}** 件")
    st.divider()

    st.markdown("""
<div class="pro-banner">
    <div class="pro-label">Ink Memory Pro</div>
    <a href="https://inkinc-hp.vercel.app/" target="_blank">
        Ink Inc. では本ツールの<br>Pro版を運用しています<br><br>
        <strong>Ink Inc. を見る →</strong>
    </a>
</div>
""", unsafe_allow_html=True)

# ─── メイン画面 ──────────────────────────────────────────
st.title("🖋️ Ink Memory Lite")
st.caption("配信活動ログ管理ツール — by Ink Inc.")
st.divider()

tabs = st.tabs(["📝 ログ追加", "📜 ログ閲覧", "✏️ 編集", "📚 名鑑", "📤 エクスポート", "⚙️ 設定"])

# ═══════════════════════════════════════════════════════
# 1. ログ追加
# ═══════════════════════════════════════════════════════
with tabs[0]:
    st.subheader("📝 活動ログの追加")
    st.caption("日々の配信活動を記録します。")

    event_date = st.date_input("出来事の日付", value=date.today(), key="add_date")
    tags_input = st.text_input(
        "タグ",
        placeholder="例：配信 ランクアップ コラボ　（スペース区切りで複数入力）",
        key="add_tags",
    )

    st.write("")
    st.markdown("**配信時間**")
    col_s, col_e = st.columns(2)
    with col_s:
        stream_start = st.text_input(
            "配信開始時間 (HH:MM)",
            placeholder="例：22:00",
            key="add_start",
        )
    with col_e:
        stream_end = st.text_input(
            "配信終了時間 (HH:MM)",
            placeholder="例：01:30",
            key="add_end",
        )
    st.markdown('<div class="score-hint">※ 日をまたぐ場合も終了時間をそのまま入力してください（自動計算します）</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("**スコア**")
    col_sc1, col_sc2 = st.columns(2)
    with col_sc1:
        support_score = st.number_input(
            "応援スコア",
            min_value=0,
            max_value=99999,
            value=None,
            step=1,
            placeholder="数値のみ",
            key="add_support",
        )
    with col_sc2:
        excitement_score = st.number_input(
            "盛り上がりスコア",
            min_value=0,
            max_value=99999,
            value=None,
            step=1,
            placeholder="数値のみ",
            key="add_excitement",
        )

    st.write("")
    memo_content = st.text_area(
        "本文（事実ログ）",
        placeholder="例：初めてのコラボ配信。視聴者数が過去最高を記録した。",
        height=220,
        key="add_memo",
    )

    st.write("")
    if st.button("保存する", type="primary", use_container_width=True):
        if not memo_content.strip():
            st.warning("本文を入力してください。")
        else:
            ev_date_str = event_date.strftime("%Y/%m/%d")
            insert_memo(
                conn,
                ev_date_str,
                memo_content.strip(),
                tags_input,
                stream_start=stream_start.strip(),
                stream_end=stream_end.strip(),
                support_score=int(support_score) if support_score is not None else None,
                excitement_score=int(excitement_score) if excitement_score is not None else None,
            )
            for k in ["add_date", "add_tags", "add_start", "add_end",
                      "add_support", "add_excitement", "add_memo"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.success(f"【{ev_date_str}】の記録を保存しました。")
            st.rerun()

# ═══════════════════════════════════════════════════════
# 2. ログ閲覧
# ═══════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("📜 活動ログの閲覧")

    col1, col2 = st.columns(2)
    with col1:
        keyword = st.text_input("キーワード検索", placeholder="配信　コラボ　など", key="view_keyword")
    with col2:
        tag_filter = st.text_input("タグで絞り込み", placeholder="ランクアップ", key="view_tag")

    col3, col4 = st.columns(2)
    with col3:
        date_from = st.date_input("開始日", value=None, key="view_from")
    with col4:
        date_to = st.date_input("終了日", value=None, key="view_to")

    date_from_str = date_from.strftime("%Y/%m/%d") if date_from else None
    date_to_str   = date_to.strftime("%Y/%m/%d")   if date_to   else None

    memos = get_memos(conn, keyword, tag_filter, date_from_str, date_to_str)

    st.caption(f"{len(memos)} 件")
    st.divider()

    if memos:
        for row in memos:
            (_, timestamp, event_date_r, content, tags,
             s_start, s_end, s_min, sup_sc, exc_sc) = row

            # ヘッダー行を組み立て
            header = f"📅 {event_date_r}　{tags or ''}"
            with st.expander(header):
                st.write(content)

                # 配信時間・スコアの表示（入力がある場合のみ）
                meta_parts = []
                if s_start and s_end:
                    meta_parts.append(f"配信 : {s_start} → {s_end}")
                if s_min is not None:
                    meta_parts.append(f"({s_min} 分)")
                if sup_sc is not None:
                    meta_parts.append(f"応援スコア : {sup_sc}")
                if exc_sc is not None:
                    meta_parts.append(f"盛り上がりスコア : {exc_sc}")
                if meta_parts:
                    st.caption("　".join(meta_parts))

                st.caption(f"記録日時 : {timestamp}")
    else:
        st.info("条件に一致するログはありません。")

# ═══════════════════════════════════════════════════════
# 3. 編集
# ═══════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("✏️ ログの編集・削除")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        edit_keyword = st.text_input("キーワード", key="edit_keyword")
    with col_e2:
        edit_date = st.date_input("日付で絞り込み", value=None, key="edit_date")

    edit_date_str = edit_date.strftime("%Y/%m/%d") if edit_date else None
    edit_memos = get_memos(conn, keyword=edit_keyword,
                           date_from=edit_date_str, date_to=edit_date_str)

    if not edit_memos:
        st.info("条件に一致するログはありません。")
    else:
        placeholder = "-- 編集するログを選択してください --"
        options = [placeholder] + [
            f"{r[2]} | {r[4] or ''} | {r[3][:25]}..." for r in edit_memos
        ]
        selected = st.selectbox("ログを選択", options, key="edit_select")

        if selected != placeholder:
            idx = options.index(selected) - 1
            target = edit_memos[idx]
            (memo_id, _, ev_date_r, content_r, tags_r,
             s_start_r, s_end_r, _, sup_sc_r, exc_sc_r) = target

            with st.form("edit_form"):
                try:
                    ev_dt = datetime.strptime(ev_date_r, "%Y/%m/%d").date()
                except ValueError:
                    ev_dt = date.today()

                new_date    = st.date_input("出来事の日付", value=ev_dt)
                new_content = st.text_area("本文", value=content_r, height=180)
                new_tags    = st.text_input("タグ", value=tags_r or "")

                st.write("")
                st.markdown("**配信時間**")
                col_es, col_ee = st.columns(2)
                with col_es:
                    new_start = st.text_input("配信開始時間 (HH:MM)", value=s_start_r or "")
                with col_ee:
                    new_end   = st.text_input("配信終了時間 (HH:MM)", value=s_end_r or "")

                st.write("")
                st.markdown("**スコア**")
                col_esc1, col_esc2 = st.columns(2)
                with col_esc1:
                    new_sup = st.number_input(
                        "応援スコア",
                        min_value=0, max_value=99999,
                        value=int(sup_sc_r) if sup_sc_r is not None else None,
                        step=1, placeholder="数値のみ",
                    )
                with col_esc2:
                    new_exc = st.number_input(
                        "盛り上がりスコア",
                        min_value=0, max_value=99999,
                        value=int(exc_sc_r) if exc_sc_r is not None else None,
                        step=1, placeholder="数値のみ",
                    )

                st.write("")
                col_a, col_b = st.columns(2)
                if col_a.form_submit_button("✅ 更新", use_container_width=True):
                    update_memo(
                        conn, memo_id,
                        new_date.strftime("%Y/%m/%d"),
                        new_content, new_tags,
                        stream_start=new_start.strip(),
                        stream_end=new_end.strip(),
                        support_score=int(new_sup) if new_sup is not None else None,
                        excitement_score=int(new_exc) if new_exc is not None else None,
                    )
                    st.success("更新しました。")
                    st.rerun()

                if col_b.form_submit_button("🗑️ 削除", use_container_width=True):
                    delete_memo(conn, memo_id)
                    st.success("削除しました。")
                    st.rerun()

# ═══════════════════════════════════════════════════════
# 4. 名鑑
# ═══════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("📚 名鑑")
    st.caption("登録は1名まで。あなた自身の情報を登録してください。")

    liver = get_liver(conn)

    if liver is None:
        st.info("まだ登録がありません。配信者情報を登録してください。")
        with st.form("new_liver_form"):
            n = st.text_input("配信者名", placeholder="黒井葉跡")
            f = st.text_input("初配信日 (YYYY/MM/DD)", placeholder="2024/01/01")
            b = st.text_input("誕生日 (MM/DD)", placeholder="04/01")
            p = st.selectbox(
                "主な活動プラットフォーム",
                ["IRIAM", "YouTube", "Twitch", "ニコ生", "その他"],
            )
            m = st.text_area("備考")

            if st.form_submit_button("登録する", type="primary", use_container_width=True):
                if not n.strip():
                    st.error("配信者名を入力してください。")
                else:
                    insert_liver(conn, n.strip(),
                                 f.replace("-", "/"),
                                 b.replace("-", "/"), p, m)
                    st.success(f"【{n}】を登録しました。")
                    st.rerun()
    else:
        liver_id, name, first_stream, birthday, platform, memo = liver
        st.write(f"**{name}** / {platform}")
        st.caption(f"初配信 : {first_stream}　　誕生日 : {birthday}")
        if memo:
            st.caption(f"備考 : {memo}")

        st.divider()
        mode = st.radio("操作", ["編集", "削除"], horizontal=True)

        if mode == "編集":
            with st.form("edit_liver_form"):
                ef = st.text_input("初配信日 (YYYY/MM/DD)",
                                   value=str(first_stream or "").replace("-", "/"))
                eb = st.text_input("誕生日 (MM/DD)",
                                   value=str(birthday or "").replace("-", "/"))
                ep = st.selectbox(
                    "主な活動プラットフォーム",
                    ["IRIAM", "YouTube", "Twitch", "ニコ生", "その他"],
                    index=["IRIAM", "YouTube", "Twitch", "ニコ生", "その他"].index(platform)
                    if platform in ["IRIAM", "YouTube", "Twitch", "ニコ生", "その他"] else 0,
                )
                em = st.text_area("備考", value=memo or "")

                if st.form_submit_button("✅ 更新", type="primary", use_container_width=True):
                    update_liver(conn, liver_id,
                                 ef.replace("-", "/"),
                                 eb.replace("-", "/"), ep, em)
                    st.success("更新しました。")
                    st.rerun()
        else:
            st.warning(f"【{name}】の登録を削除します。ログは残ります。")
            if st.button("削除する", type="primary", use_container_width=True):
                delete_liver(conn, liver_id)
                st.success("削除しました。")
                st.rerun()

# ═══════════════════════════════════════════════════════
# 5. エクスポート
# ═══════════════════════════════════════════════════════
with tabs[4]:
    st.subheader("📤 CSVエクスポート")
    st.caption("ログをCSVに書き出して、外部AIに分析を依頼できます。")

    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        ex_from = st.date_input("開始日（任意）", value=None, key="ex_from")
    with col_ex2:
        ex_to = st.date_input("終了日（任意）", value=None, key="ex_to")

    ex_from_str = ex_from.strftime("%Y/%m/%d") if ex_from else None
    ex_to_str   = ex_to.strftime("%Y/%m/%d")   if ex_to   else None

    export_memos = get_memos(conn, date_from=ex_from_str, date_to=ex_to_str)
    st.caption(f"出力対象 : {len(export_memos)} 件")

    if export_memos:
        csv_bytes = export_memos_to_csv(export_memos)
        st.download_button(
            label="📥 CSVをダウンロード",
            data=csv_bytes,
            file_name=get_export_filename(),
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )
    else:
        st.info("出力対象のログがありません。")

    st.divider()
    st.subheader("🤖 外部AI向けプロンプト例文")
    st.caption("CSVをダウンロードしたら、以下のプロンプトをコピーして Claude・ChatGPT・Gemini に投げてください。")

    prompts = [
        (
            "基本分析",
            """あなたは配信者のマネージャーです。
添付のCSVは私の配信活動ログです。
日付・タグ・配信時間・本文をもとに、以下の観点で分析してください。

1. 活動の傾向（どんな内容が多いか）
2. 配信時間の傾向（長い・短い・深夜が多いなど）
3. 成長が見られる点
4. 改善できそうな点
5. 今後1ヶ月の方針アドバイス

厳しめに、でも建設的にお願いします。""",
        ),
        (
            "タグ分析",
            """あなたは配信分析の専門家です。
CSVの「タグ」列に注目し、どのジャンルの配信が多いかを分析してください。
また、タグの偏りから見えるリスクと、
新しく試すべき配信スタイルを提案してください。""",
        ),
        (
            "成長ストーリー",
            """CSVの「本文」列を時系列で読み、
私の配信者としての変化・成長を物語として語ってください。
その上で、半年後の理想像と、そこへの具体的なステップを提示してください。""",
        ),
        (
            "課題発見",
            """配信活動ログのCSVを見て、
繰り返し登場しているネガティブな要素や停滞のパターンを抽出してください。
そのうえで、最も優先的に対処すべき課題を1つ選び、
具体的な改善策を提示してください。""",
        ),
        (
            "配信時間分析",
            """CSVの「配信時間(分)」列を集計し、以下を分析してください。

1. 合計配信時間・平均配信時間
2. 配信時間が長い日・短い日の傾向
3. 理想的な配信時間帯・長さのアドバイス

「応援スコア」「盛り上がりスコア」が記入されている場合は、
配信時間との相関も考察してください。""",
        ),
    ]

    for title, prompt_text in prompts:
        with st.expander(f"📋 {title}"):
            st.code(prompt_text, language=None)

# ═══════════════════════════════════════════════════════
# 6. 設定
# ═══════════════════════════════════════════════════════
with tabs[5]:
    st.subheader("⚙️ 設定")
    st.caption("ダッシュボードの表示に使用します。")

    current_name  = get_setting(conn, "office_name")
    current_start = get_setting(conn, "activity_start_date")

    with st.form("settings_form"):
        new_name = st.text_input(
            "活動名・配信者名",
            value=current_name,
            placeholder="例：黒井葉跡",
        )
        new_start = st.text_input(
            "活動開始日 (YYYY/MM/DD)",
            value=current_start,
            placeholder="例：2024/04/01",
            help="サイドバーの「活動の歩み」カウントの基準日です。",
        )

        if st.form_submit_button("保存する", type="primary", use_container_width=True):
            set_setting(conn, "office_name", new_name.strip())
            set_setting(conn, "activity_start_date",
                        new_start.strip().replace("-", "/"))
            st.success("設定を保存しました。")
            st.rerun()
