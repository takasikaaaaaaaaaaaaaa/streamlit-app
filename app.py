import streamlit as st
import datetime
import json
import os
import calendar
from streamlit_drawable_canvas import st_canvas

# ---------------------------------------------------------
# データ管理・設定
# ---------------------------------------------------------
DATA_FILE = "learning_app_data.json"
st.set_page_config(page_title="学習アプリ", layout="wide")

# セッション状態の初期化（画面が変わってもデータを忘れないようにする）
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"
if 'schedules' not in st.session_state:
    st.session_state.schedules = {}
if 'notebook_data' not in st.session_state:
    st.session_state.notebook_data = None # 画像データを保持するのは難しいため、簡易的な実装にします
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# データのロード関数
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                st.session_state.schedules = data.get('schedules', {})
                st.session_state.tasks = data.get('tasks', [])
                # ノートブックの描画データは複雑なため、今回はセッションのみで扱います
        except Exception:
            pass

# データのセーブ関数
def save_data():
    data = {
        'schedules': st.session_state.schedules,
        'tasks': st.session_state.tasks
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# アプリ起動時に一度だけロード
if 'data_loaded' not in st.session_state:
    load_data()
    st.session_state.data_loaded = True

# ページ切り替え関数
def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun() # 画面を更新

# ---------------------------------------------------------
# 1. Dashboard (ホーム画面)
# ---------------------------------------------------------
def render_dashboard():
    st.title("🏠 メインダッシュボード")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.subheader("📅 カレンダー")
            st.info("スケジュールの確認と編集ができます")
            if st.button("カレンダーを開く", use_container_width=True):
                navigate_to("calendar")

        with st.container(border=True):
            st.subheader("📝 デジタルノート")
            st.info("自由に描画やメモができます")
            if st.button("ノートを開く", use_container_width=True):
                navigate_to("notebook")

    with col2:
        with st.container(border=True):
            st.subheader("📋 タスクマネージャー")
            st.info("To-Doリストを管理します")
            if st.button("タスクを開く", use_container_width=True):
                navigate_to("tasks")
                
        with st.container(border=True):
            st.subheader("🎨 共有ホワイトボード")
            st.info("みんなで使えるボード（シミュレーション）")
            if st.button("ホワイトボードを開く", use_container_width=True):
                navigate_to("whiteboard")

# ---------------------------------------------------------
# 2. Notebook (デジタルノート)
# ---------------------------------------------------------
def render_notebook():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🏠 ホーム", use_container_width=True):
            navigate_to("dashboard")
    with col2:
        st.header("📝 デジタルノート")

    # ツールバー
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stroke_width = st.slider("線の太さ", 1, 25, 3)
    with c2:
        stroke_color = st.color_picker("ペンの色", "#000000")
    with c3:
        bg_color = st.color_picker("背景色", "#FFFFFF")
    with c4:
        drawing_mode = st.selectbox("モード", ("freedraw", "line", "rect", "circle", "transform"))

    st.write("▼ 下のキャンバスに自由に描けます")
    
    # キャンバスコンポーネント
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # 図形の塗りつぶし色
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=400,
        drawing_mode=drawing_mode,
        key="notebook_canvas",
    )

    st.caption("※Web版では、テキストカード機能の代わりに手書きまたは下のメモ欄を使用してください。")
    st.text_area("🗒️ テキストメモ", height=100, placeholder="ここに文字情報をメモできます...")

# ---------------------------------------------------------
# 3. Calendar (カレンダー)
# ---------------------------------------------------------
def render_calendar():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🏠 ホーム", use_container_width=True):
            navigate_to("dashboard")
    with col2:
        st.header("📅 詳細カレンダー")

    # 左側：日付選択、右側：予定編集
    c_left, c_right = st.columns([1, 2])
    
    with c_left:
        selected_date = st.date_input("日付を選択", datetime.date.today())
        date_str = str(selected_date)
        
        # 祝日判定（簡易版）
        jp_holidays = {
            "01-01": "元日", "02-11": "建国記念の日", "02-23": "天皇誕生日",
            "04-29": "昭和の日", "05-03": "憲法記念日", "05-04": "みどりの日", "05-05": "こどもの日",
            "11-03": "文化の日", "11-23": "勤労感謝の日"
        }
        md_str = date_str[5:] # MM-DD
        holiday_name = jp_holidays.get(md_str)
        
        if holiday_name:
            st.error(f"🎌 {holiday_name}")
        elif selected_date.weekday() == 6: # 日曜
            st.error("日曜日")
        elif selected_date.weekday() == 5: # 土曜
            st.info("土曜日")
        else:
            st.success("平日")

    with c_right:
        st.subheader(f"{selected_date.year}年{selected_date.month}月{selected_date.day}日の予定")
        
        current_schedule = st.session_state.schedules.get(date_str, "")
        new_schedule = st.text_area("予定の内容", value=current_schedule, height=150)
        
        if st.button("💾 予定を保存"):
            if new_schedule.strip():
                st.session_state.schedules[date_str] = new_schedule
            elif date_str in st.session_state.schedules:
                del st.session_state.schedules[date_str] # 空なら削除
            save_data()
            st.success("保存しました！")

# ---------------------------------------------------------
# 4. Task Manager (タスク管理)
# ---------------------------------------------------------
def render_tasks():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🏠 ホーム", use_container_width=True):
            navigate_to("dashboard")
    with col2:
        st.header("✅ タスクマネージャー")

    # タスク追加フォーム
    with st.form("add_task_form", clear_on_submit=True):
        col_in, col_btn = st.columns([4, 1])
        with col_in:
            new_task_text = st.text_input("新しいタスクを入力")
        with col_btn:
            submitted = st.form_submit_button("追加")
        
        if submitted and new_task_text:
            max_id = max([t['id'] for t in st.session_state.tasks], default=0)
            st.session_state.tasks.append({
                "id": max_id + 1,
                "text": new_task_text,
                "completed": False
            })
            save_data()
            st.rerun()

    # タスク一覧表示
    if not st.session_state.tasks:
        st.info("タスクはまだありません。")
    else:
        # 未完了と完了を分ける
        incomplete_tasks = [t for t in st.session_state.tasks if not t['completed']]
        completed_tasks = [t for t in st.session_state.tasks if t['completed']]

        st.subheader(f"未完了 ({len(incomplete_tasks)})")
        for task in incomplete_tasks:
            c1, c2, c3 = st.columns([0.5, 4, 1])
            with c1:
                if st.button("⬜", key=f"check_{task['id']}"):
                    task['completed'] = True
                    save_data()
                    st.rerun()
            with c2:
                st.write(task['text'])
            with c3:
                if st.button("削除", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    save_data()
                    st.rerun()

        st.subheader(f"完了済み ({len(completed_tasks)})")
        for task in completed_tasks:
            c1, c2, c3 = st.columns([0.5, 4, 1])
            with c1:
                if st.button("✅", key=f"uncheck_{task['id']}"):
                    task['completed'] = False
                    save_data()
                    st.rerun()
            with c2:
                st.markdown(f"~~{task['text']}~~")
            with c3:
                if st.button("削除", key=f"del_comp_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    save_data()
                    st.rerun()

# ---------------------------------------------------------
# 5. Shared Whiteboard (共有ホワイトボード)
# ---------------------------------------------------------
def render_whiteboard():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🏠 ホーム", use_container_width=True):
            navigate_to("dashboard")
    with col2:
        st.header("🎨 共有ホワイトボード (デモ)")

    st.info("ここでは複数の生徒が同時に書き込んでいる様子をシミュレーションします。")

    students = [
        {"name": "佐藤太郎", "color": "#FF0000"},
        {"name": "田中花子", "color": "#0000FF"},
        {"name": "山本健太", "color": "#008000"},
    ]

    # タブで生徒を切り替える（Web画面の制約上、縦に並べるよりタブが見やすい）
    tabs = st.tabs([s["name"] for s in students])

    for i, tab in enumerate(tabs):
        with tab:
            st.caption(f"色: {students[i]['color']}")
            # 生徒ごとのキャンバス（独立して描画可能）
            st_canvas(
                stroke_width=3,
                stroke_color=students[i]['color'],
                background_color="#F0FFFF",
                height=250,
                key=f"wb_student_{i}",
            )

# ---------------------------------------------------------
# メインルーティング
# ---------------------------------------------------------
if st.session_state.page == "dashboard":
    render_dashboard()
elif st.session_state.page == "notebook":
    render_notebook()
elif st.session_state.page == "calendar":
    render_calendar()
elif st.session_state.page == "tasks":
    render_tasks()
elif st.session_state.page == "whiteboard":
    render_whiteboard()