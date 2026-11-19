import streamlit as st
import random
import itertools
import time
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

# ----------------------------------------------------
# --- 🎯 アプリケーション全体の初期設定 ---
# ----------------------------------------------------
st.set_page_config(
    page_title="三角比・三角関数クイズアプリ",
    layout="wide"
)

# セッションステートの初期化（画面管理用）
if 'page' not in st.session_state:
    st.session_state.page = 'top'
if 'category' not in st.session_state:
    st.session_state.category = 'trig_ratio'

# ----------------------------------------------------
# --- 共通の定数とCSS ---
# ----------------------------------------------------
# --- クイズ1 (補角・余角編) の定数 ---
Q1_FUNCTIONS = ["sin", "cos", "tan"]

# 度数法（三角比用）
Q1_OFFSETS_DEG = {
    "neg_t": r"(-\theta)",
    "p90_t": r"(90^\circ+\theta)",
    "m90_t": r"(90^\circ-\theta)",
    "p180_t": r"(180^\circ+\theta)",
    "m180_t": r"(180^\circ-\theta)",
    "p270_t": r"(270^\circ+\theta)",
    "m270_t": r"(-270^\circ+\theta)",
    "p360_t": r"(360^\circ+\theta)",
    "m360_t": r"(-360^\circ+\theta)",
    "mneg90_t": r"(-90^\circ+\theta)",
    "mneg90m_t": r"(-90^\circ-\theta)",
    "mneg180_t": r"(-180^\circ+\theta)",
    "mneg180m_t": r"(-180^\circ-\theta)",
    "mneg270_t": r"(-270^\circ+\theta)",
    "mneg270m_t": r"(-270^\circ-\theta)",
}

# 弧度法・ラジアン（三角関数用：係数1は分子に\pi、係数2以上は分数の横に\pi）
Q1_OFFSETS_RAD = {
    "neg_t": r"(-\theta)",
    "p90_t": r"\left(\dfrac{\pi}{2}+\theta\right)",
    "m90_t": r"\left(\dfrac{\pi}{2}-\theta\right)",
    "p180_t": r"(\pi+\theta)",
    "m180_t": r"(\pi-\theta)",
    "p270_t": r"\left(\dfrac{3}{2}\pi+\theta\right)",
    "m270_t": r"\left(-\dfrac{3}{2}\pi+\theta\right)",
    "p360_t": r"(2\pi+\theta)",
    "m360_t": r"(-2\pi+\theta)",
    "mneg90_t": r"\left(-\dfrac{\pi}{2}+\theta\right)",
    "mneg90m_t": r"\left(-\dfrac{\pi}{2}-\theta\right)",
    "mneg180_t": r"(-\pi+\theta)",
    "mneg180m_t": r"(-\pi-\theta)",
    "mneg270_t": r"\left(-\dfrac{3}{2}\pi+\theta\right)",
    "mneg270m_t": r"\left(-\dfrac{3}{2}\pi-\theta\right)",
}

Q1_OFFSET_RANGES = {
    "0~180": {
        "deg_label": r" $0^\circ \sim 180^\circ$ ",
        "rad_label": r" $0 \sim \pi$ ",
        "keys": ["m90_t", "p90_t", "m180_t"]
    },
    "0~360": {
        "deg_label": r" $0^\circ \sim 360^\circ$ ",
        "rad_label": r" $0 \sim 2\pi$ ",
        "keys": ["m90_t", "p90_t", "m180_t", "p180_t", "m270_t", "p270_t", "m360_t"]
    },
    "-180~180": {
        "deg_label": r" $-180^\circ \sim 180^\circ$ ",
        "rad_label": r" $-\pi \sim \pi$ ",
        "keys": ["neg_t", "m90_t", "p90_t", "m180_t", "mneg90_t", "mneg90m_t", "mneg180_t"]
    },
    "ALL": {
        "deg_label": "全範囲",
        "rad_label": "全範囲",
        "keys": list(Q1_OFFSETS_DEG.keys())
    }
}

Q1_RESULT_OPTIONS = {
    "sin_t": r"\sin\theta",
    "-sin_t": r"-\sin\theta",
    "cos_t": r"\cos\theta",
    "-cos_t": r"-\cos\theta",
    "tan_t": r"\tan\theta",
    "-tan_t": r"-\tan\theta",
    "cot_t": r"\dfrac{1}{\tan\theta}",
    "-cot_t": r"-\dfrac{1}{\tan\theta}",
}

Q1_SIN_COS_OPTIONS_KEYS = ["sin_t", "-sin_t", "cos_t", "-cos_t"]
Q1_TAN_OPTIONS_KEYS = ["tan_t", "-tan_t", "cot_t", "-cot_t"]

Q1_TRANSFORM_ANSWERS = {
    "sin": {
        "neg_t": "-sin_t",
        "p90_t": "cos_t",
        "m90_t": "cos_t",
        "p180_t": "-sin_t",
        "m180_t": "sin_t",
        "p270_t": "-cos_t",
        "m270_t": "cos_t",
        "p360_t": "sin_t",
        "m360_t": "sin_t",
        "mneg90_t": "-cos_t",
        "mneg90m_t": "-cos_t",
        "mneg180_t": "-sin_t",
        "mneg180m_t": "sin_t",
        "mneg270_t": "cos_t",
        "mneg270m_t": "cos_t",
    },
    "cos": {
        "neg_t": "cos_t",
        "p90_t": "-sin_t",
        "m90_t": "sin_t",
        "p180_t": "-cos_t",
        "m180_t": "-cos_t",
        "p270_t": "sin_t",
        "m270_t": "sin_t",
        "p360_t": "cos_t",
        "m360_t": "cos_t",
        "mneg90_t": "sin_t",
        "mneg90m_t": "-sin_t",
        "mneg180_t": "-cos_t",
        "mneg180m_t": "-cos_t",
        "mneg270_t": "-sin_t",
        "mneg270m_t": "-sin_t",
    },
    "tan": {
        "neg_t": "-tan_t",
        "p90_t": "-cot_t",
        "m90_t": "cot_t",
        "p180_t": "tan_t",
        "m180_t": "-tan_t",
        "p270_t": "-cot_t",
        "m270_t": "-cot_t",
        "p360_t": "tan_t",
        "m360_t": "tan_t",
        "mneg90_t": "cot_t",
        "mneg90m_t": "cot_t",
        "mneg180_t": "tan_t",
        "mneg180m_t": "-tan_t",
        "mneg270_t": "cot_t",
        "mneg270m_t": "-cot_t",
    },
}
Q1_MAX_QUESTIONS = 10

# --- クイズ2 (有名角編) の定数 ---
Q2_FUNCTIONS = ["sin", "cos", "tan"]

Q2_ANSWERS = {
    "sin": {
        -360: "0", -330: "1/2", -315: "√2/2", -300: "√3/2", -270: "1", -240: "√3/2", -225: "√2/2", -210: "1/2",
        -180: "0", -150: "-1/2", -135: "-√2/2", -120: "-√3/2", -90: "-1", -60: "-√3/2", -45: "-√2/2", -30: "-1/2",
        0: "0", 30: "1/2", 45: "√2/2", 60: "√3/2", 90: "1", 120: "√3/2", 135: "√2/2", 150: "1/2",
        180: "0", 210: "-1/2", 225: "-√2/2", 240: "-√3/2", 270: "-1", 300: "-√3/2", 315: "-√2/2", 330: "-1/2",
        360: "0", 390: "1/2", 405: "√2/2", 420: "√3/2", 450: "1"
    },
    "cos": {
        -360: "1", -330: "√3/2", -315: "√2/2", -300: "1/2", -270: "0", -240: "-1/2", -225: "-√2/2", -210: "-√3/2",
        -180: "-1", -150: "-√3/2", -135: "-√2/2", -120: "-1/2", -90: "0", -60: "1/2", -45: "√2/2", -30: "√3/2",
        0: "1", 30: "√3/2", 45: "√2/2", 60: "1/2", 90: "0", 120: "-1/2", 135: "-√2/2", 150: "-√3/2",
        180: "-1", 210: "-√3/2", 225: "-√2/2", 240: "-1/2", 270: "0", 300: "1/2", 315: "√2/2", 330: "√3/2",
        360: "1", 390: "√3/2", 405: "√2/2", 420: "1/2", 450: "0"
    },
    "tan": {
        -360: "0", -330: "1/√3", -315: "1", -300: "√3", -270: "なし", -240: "-√3", -225: "-1", -210: "-1/√3",
        -180: "0", -150: "1/√3", -135: "1", -120: "√3", -90: "なし", -60: "-√3", -45: "-1", -30: "-1/√3",
        0: "0", 30: "1/√3", 45: "1", 60: "√3", 90: "なし", 120: "-√3", 135: "-1", 150: "-1/√3",
        180: "0", 210: "1/√3", 225: "1", 240: "√3", 270: "なし", 300: "-√3", 315: "-1", 330: "-1/√3",
        360: "0", 390: "1/√3", 405: "1", 420: "√3", 450: "なし"
    }
}

# 角度（整数値）→ ラジアン分数表記の対応表（係数1は分子に\pi、係数2以上は分数の横に\pi）
Q2_RADIAN_LABELS = {
    -360: r"-2\pi",
    -330: r"-\dfrac{11}{6}\pi",
    -315: r"-\dfrac{7}{4}\pi",
    -300: r"-\dfrac{5}{3}\pi",
    -270: r"-\dfrac{3}{2}\pi",
    -240: r"-\dfrac{4}{3}\pi",
    -225: r"-\dfrac{5}{4}\pi",
    -210: r"-\dfrac{7}{6}\pi",
    -180: r"-\pi",
    -150: r"-\dfrac{5}{6}\pi",
    -135: r"-\dfrac{3}{4}\pi",
    -120: r"-\dfrac{2}{3}\pi",
    -90: r"-\dfrac{\pi}{2}",
    -60: r"-\dfrac{\pi}{3}",
    -45: r"-\dfrac{\pi}{4}",
    -30: r"-\dfrac{\pi}{6}",
    0: r"0",
    30: r"\dfrac{\pi}{6}",
    45: r"\dfrac{\pi}{4}",
    60: r"\dfrac{\pi}{3}",
    90: r"\dfrac{\pi}{2}",
    120: r"\dfrac{2}{3}\pi",
    135: r"\dfrac{3}{4}\pi",
    150: r"\dfrac{5}{6}\pi",
    180: r"\pi",
    210: r"\dfrac{7}{6}\pi",
    225: r"\dfrac{5}{4}\pi",
    240: r"\dfrac{4}{3}\pi",
    270: r"\dfrac{3}{2}\pi",
    300: r"\dfrac{5}{3}\pi",
    315: r"\dfrac{7}{4}\pi",
    330: r"\dfrac{11}{6}\pi",
    360: r"2\pi",
    390: r"\dfrac{13}{6}\pi",
    405: r"\dfrac{9}{4}\pi",
    420: r"\dfrac{7}{3}\pi",
    450: r"\dfrac{5}{2}\pi",
}

Q2_ANGLE_RANGES = {
    "0~180": [0, 30, 45, 60, 90, 120, 135, 150, 180],
    "0~360": [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360],
    "-180~180": [-180, -150, -135, -120, -90, -60, -45, -30, 0, 30, 45, 60, 90, 120, 135, 150, 180],
    "ALL": list(Q2_ANSWERS["sin"].keys())
}

Q2_RANGE_LABELS = {
    "0~180": {"deg": r"$0^\circ \sim 180^\circ$", "rad": r"$0 \sim \pi$"},
    "0~360": {"deg": r"$0^\circ \sim 360^\circ$", "rad": r"$0 \sim 2\pi$"},
    "-180~180": {"deg": r"$-180^\circ \sim 180^\circ$", "rad": r"$-\pi \sim \pi$"},
    "ALL": {"deg": "全範囲", "rad": "全範囲"},
}

Q2_LATEX_OPTIONS = {
    "0": r"$0$",
    "1/2": r"$\dfrac{1}{2}$",
    "√2/2": r"$\dfrac{\sqrt{2}}{2}$",
    "√3/2": r"$\dfrac{\sqrt{3}}{2}$",
    "1": r"$1$",
    "-1/2": r"$-\dfrac{1}{2}$",
    "-√2/2": r"$-\dfrac{\sqrt{2}}{2}$",
    "-√3/2": r"$-\dfrac{\sqrt{3}}{2}$",
    "-1": r"$-1$",
    "√3": r"$\sqrt{3}$",
    "-√3": r"$-\sqrt{3}$",
    "1/√3": r"$\dfrac{1}{\sqrt{3}}$",
    "-1/√3": r"$-\dfrac{1}{\sqrt{3}}$",
    "なし": "なし"
}

Q2_SIN_COS_OPTIONS = ["1/2", "√2/2", "√3/2", "1", "-1/2", "-√2/2", "-√3/2", "-1", "0"]
Q2_TAN_OPTIONS = ["0", "1/√3", "1", "√3", "なし", "-1/√3", "-1", "-√3"]
Q2_MAX_QUESTIONS = 10

# ----------------------------------------------------
# 共通CSS（ボタンサイズ統一 ＆ 結果テーブルのコンパクト整形）
# ----------------------------------------------------
st.markdown("""
<style>
/* ボタンの高さ・幅を完全に統一 */
div.stButton,
div[data-testid="stButton"] {
    width: 100% !important;
}
div.stButton > button,
button[data-testid="stBaseButton-secondary"],
button[data-testid="stBaseButton-primary"] {
    width: 100% !important;
    height: 80px !important;
    min-height: 80px !important;
    max-height: 80px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 8px !important;
    box-sizing: border-box !important;
}
div.stButton > button p,
button[data-testid="stBaseButton-secondary"] p,
button[data-testid="stBaseButton-primary"] p,
div.stButton > button .katex-display {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
}

/* 結果確認テーブルをコンパクトで整ったデザインに調整（分数も上下にゆとりを持たせて綺麗に描画） */
div[data-testid="stTable"] {
    max-width: 640px !important;
    margin: 0 auto 1.2rem auto !important;
}
div[data-testid="stTable"] table {
    width: 100% !important;
    border-collapse: collapse !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    font-size: 0.95rem !important;
}
div[data-testid="stTable"] thead tr th {
    background-color: rgba(128, 128, 128, 0.12) !important;
    font-weight: 600 !important;
    text-align: center !important;
    vertical-align: middle !important;
    padding: 10px 8px !important;
    white-space: nowrap !important;
}
div[data-testid="stTable"] tbody tr th,
div[data-testid="stTable"] tbody tr td {
    text-align: center !important;
    vertical-align: middle !important;
    padding: 11px 8px !important;
    line-height: 1.4 !important;
}
div[data-testid="stTable"] tbody tr th {
    width: 56px !important;
    font-weight: 600 !important;
}
div[data-testid="stTable"] tbody tr td:last-child {
    width: 56px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# --- 画面遷移ヘルパー関数 ---
# ----------------------------------------------------
def navigate_to(page, category=None):
    """選択中の分野(category)を維持しながら画面遷移する"""
    current_category = category if category is not None else st.session_state.get('category', 'trig_ratio')
    st.session_state.clear()
    st.session_state.category = current_category
    st.session_state.page = page
    st.rerun()

# ----------------------------------------------------
# --- 🌐 トップ画面（分野選択）の関数 ---
# ----------------------------------------------------
def top_page():
    """最上位の分野選択画面（三角比クイズ / 三角関数クイズ）を表示する関数"""
    st.title("三角比・三角関数クイズ")
    st.header("挑戦する分野を選んでください")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("三角比クイズ")
        st.markdown(r"度数法（$0^\circ \sim 360^\circ$ など）での変換公式や有名角の三角比を問うクイズです。")
        if st.button("三角比クイズ", key='go_to_trig_ratio', use_container_width=True):
            navigate_to('home', category='trig_ratio')

    with col2:
        st.subheader("三角関数クイズ")
        st.markdown(r"弧度法（$0 \sim 2\pi$ など）での変換公式や有名角の三角関数を問うクイズです。")
        if st.button("三角関数クイズ", key='go_to_trig_func', use_container_width=True):
            navigate_to('home', category='trig_func')

# ----------------------------------------------------
# --- 🏠 クイズ選択画面の関数 ---
# ----------------------------------------------------
def home_page():
    """クイズ選択画面を表示する関数"""
    is_func = (st.session_state.get('category') == 'trig_func')
    category_title = "三角関数クイズ" if is_func else "三角比クイズ"
    quiz2_label = "有名角の三角関数" if is_func else "有名角の三角比"

    st.title(category_title)
    st.header("挑戦するクイズを選んでください")
    st.markdown("---")

    # 1. クイズ 1 (補角・余角)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("補角・余角")
        if is_func:
            st.markdown(r"$$ \sin\left(\dfrac{\pi}{2} - \theta\right) = \ ? $$ のような変換公式を問うクイズです。")
        else:
            st.markdown(r"$$ \text{sin}(90^\circ - \theta) = \ ? $$ のような変換公式を問うクイズです。")
        if st.button("補角・余角", key='go_to_quiz1', use_container_width=True):
            navigate_to('quiz1')

    # 2. クイズ 2 (有名角の三角比 / 三角関数)
    with col2:
        st.subheader(quiz2_label)
        if is_func:
            st.markdown(r"$$ \cos\dfrac{2}{3}\pi = \ ? $$ のような有名角の三角関数を問うクイズです。")
        else:
            st.markdown(r"$$ \text{cos}{120^\circ} = \ ? $$ のような有名角の三角比を問うクイズです。")
        if st.button(quiz2_label, key='go_to_quiz2', use_container_width=True):
            navigate_to('quiz2')

# ----------------------------------------------------
# --- 📝 クイズ 1 の関数 ---
# ----------------------------------------------------
def quiz1_transform_page():
    """クイズ (補角・余角) のロジックを実行する関数"""
    is_func = (st.session_state.get('category') == 'trig_func')
    offsets_dict = Q1_OFFSETS_RAD if is_func else Q1_OFFSETS_DEG
    label_key = "rad_label" if is_func else "deg_label"

    st.title("クイズ（補角・余角）")

    # -----------------------------
    # セッション操作関数 (クイズ1用)
    # -----------------------------
    def q1_new_question():
        func, offset_key = st.session_state.q1_pool.pop()
        st.session_state.func = func
        st.session_state.offset_key = offset_key
        
        if st.session_state.func in ["sin", "cos"]:
            options_base = Q1_SIN_COS_OPTIONS_KEYS
        else:
            options_base = Q1_TAN_OPTIONS_KEYS
            
        st.session_state.display_options = options_base
        st.session_state.selected = None
        st.session_state.show_result = False

    def q1_initialize_session_state():
        if 'range_selected' not in st.session_state:
            st.session_state.range_selected = False
            st.session_state.offset_range = "ALL"
        
        if 'score' not in st.session_state and st.session_state.range_selected:
            st.session_state.score = 0
            st.session_state.question_count = 0
            st.session_state.history = []
            st.session_state.show_result = False

            # 全組み合わせをシャッフルして重複を防止
            possible_offsets = Q1_OFFSET_RANGES[st.session_state.offset_range]["keys"]
            pool = list(itertools.product(Q1_FUNCTIONS, possible_offsets))
            random.shuffle(pool)

            st.session_state.q1_pool = pool
            st.session_state.max_questions = min(Q1_MAX_QUESTIONS, len(pool))
            st.session_state.start_time = time.time()
            q1_new_question()

    def q1_check_answer_and_advance(selected_key):
        st.session_state.selected = selected_key 

        current_func = st.session_state.func
        current_offset_key = st.session_state.offset_key
        correct_key = Q1_TRANSFORM_ANSWERS.get(current_func, {}).get(current_offset_key)
        
        is_correct = (st.session_state.selected == correct_key)

        question_inline = "$ \\" + current_func + " " + offsets_dict[current_offset_key] + " $"
        
        st.session_state.history.append({
            "question_disp": question_inline, 
            "user_answer_key": st.session_state.selected,
            "correct_answer_key": correct_key,
            "is_correct": is_correct
        })

        if is_correct:
            st.session_state.score += 1

        st.session_state.question_count += 1

        if st.session_state.question_count >= st.session_state.max_questions:
            st.session_state.show_result = True
        else:
            q1_new_question()

        st.rerun()

    # 初期化呼び出し
    q1_initialize_session_state()

    # -----------------------------------------------
    # クイズ1の描画
    # -----------------------------------------------
    if not st.session_state.range_selected:
        st.header("出題範囲を選択してください")
        st.markdown("---")

        row1 = st.columns(2)
        row2 = st.columns(2)
        
        if row1[0].button(Q1_OFFSET_RANGES["0~180"][label_key], use_container_width=True, key="q1_range_0_180"):
            st.session_state.offset_range = "0~180"
            st.session_state.range_selected = True
            q1_initialize_session_state()
            st.rerun()
            
        if row1[1].button(Q1_OFFSET_RANGES["0~360"][label_key], use_container_width=True, key="q1_range_0_360"):
            st.session_state.offset_range = "0~360"
            st.session_state.range_selected = True
            q1_initialize_session_state()
            st.rerun()
            
        if row2[0].button(Q1_OFFSET_RANGES["-180~180"][label_key], use_container_width=True, key="q1_range_-180_180"):
            st.session_state.offset_range = "-180~180"
            st.session_state.range_selected = True
            q1_initialize_session_state()
            st.rerun()
            
        if row2[1].button(Q1_OFFSET_RANGES["ALL"][label_key], use_container_width=True, key="q1_range_all"):
            st.session_state.offset_range = "ALL"
            st.session_state.range_selected = True
            q1_initialize_session_state()
            st.rerun()

    elif st.session_state.show_result:
        end_time = time.time()
        elapsed = Decimal(str(end_time - st.session_state.start_time)).quantize(Decimal('0.01'), ROUND_HALF_UP)

        st.header("✨ クイズ終了！ 結果発表 ✨")
        st.markdown(f"**あなたのスコア: {st.session_state.score} / {st.session_state.max_questions} 問正解**")
        st.write(f"**経過時間: {elapsed} 秒**")
        st.divider()

        _, center_col, _ = st.columns([1, 2.2, 1])
        with center_col:
            st.subheader("全解答の確認")
            table_data = []
            for i, item in enumerate(st.session_state.history, 1):
                user_latex = Q1_RESULT_OPTIONS[item['user_answer_key']]
                correct_latex = Q1_RESULT_OPTIONS[item['correct_answer_key']]
                user_disp = "$ " + user_latex + " $"
                correct_disp = "$ " + correct_latex + " $"
                mark = "○" if item['is_correct'] else "×"
                table_data.append({
                    "番号": i,
                    "問題": item['question_disp'],
                    "あなたの解答": user_disp,
                    "正解": correct_disp,
                    "正誤": mark
                })
            df = pd.DataFrame(table_data)
            st.table(df.set_index("番号"))

            if st.button("もう一度行う", key='q1_restart', use_container_width=True, type="primary"):
                navigate_to('quiz1')

    else:
        st.subheader(f"問題 {st.session_state.question_count + 1} / {st.session_state.max_questions}")

        current_func = st.session_state.func
        current_offset_key = st.session_state.offset_key
        
        question_latex = "$$ \\" + current_func + " " + offsets_dict[current_offset_key] + " $$を簡単にせよ"

        st.markdown(question_latex)
        st.markdown("---")

        display_options_keys = st.session_state.display_options
        
        cols = st.columns(4)
        for i, key in enumerate(display_options_keys):
            latex_label = f"$$ {Q1_RESULT_OPTIONS[key]} $$"
            
            with cols[i]:
                button_key = f"q1_option_{st.session_state.question_count}_{key}"
                if st.button(latex_label, use_container_width=True, key=button_key):
                    q1_check_answer_and_advance(key)

# ----------------------------------------------------
# --- 🖼️ クイズ 2 の関数 ---
# ----------------------------------------------------
def quiz2_famous_angles_page():
    """クイズ 2 (有名角の三角比 / 三角関数) のロジックを実行する関数"""
    is_func = (st.session_state.get('category') == 'trig_func')
    range_mode = "rad" if is_func else "deg"
    st.title("クイズ（有名角の三角関数）" if is_func else "クイズ（有名角の三角比）")

    # -----------------------------
    # セッション操作関数 (クイズ2用)
    # -----------------------------
    def q2_new_question():
        func, angle = st.session_state.q2_pool.pop()
        st.session_state.func = func
        st.session_state.angle = angle
        st.session_state.selected = None
        st.session_state.result = ""
        st.session_state.show_result = False

    def q2_initialize_session_state():
        if 'range_selected' not in st.session_state:
            st.session_state.range_selected = False
            st.session_state.angle_range = "ALL"
        
        if 'func' not in st.session_state and st.session_state.range_selected:
            st.session_state.score = 0
            st.session_state.question_count = 0
            st.session_state.history = []
            st.session_state.show_result = False

            # 全組み合わせをシャッフルして重複を防止
            possible_angles = Q2_ANGLE_RANGES[st.session_state.angle_range]
            pool = list(itertools.product(Q2_FUNCTIONS, possible_angles))
            random.shuffle(pool)

            st.session_state.q2_pool = pool
            st.session_state.max_questions = min(Q2_MAX_QUESTIONS, len(pool))
            st.session_state.start_time = time.time()
            q2_new_question()

    def q2_check_answer_and_advance():
        if st.session_state.selected is None:
            return

        current_func = st.session_state.func
        current_angle = st.session_state.angle
        correct = Q2_ANSWERS[current_func][current_angle]

        is_correct = (st.session_state.selected == correct)

        st.session_state.history.append({
            "func": current_func,
            "angle": current_angle,
            "user_answer": st.session_state.selected,
            "correct_answer": correct,
            "is_correct": is_correct
        })

        if is_correct:
            st.session_state.score += 1

        st.session_state.question_count += 1

        if st.session_state.question_count >= st.session_state.max_questions:
            st.session_state.show_result = True
        else:
            q2_new_question()

        st.rerun()

    # 初期化呼び出し
    q2_initialize_session_state()

    # -----------------------------------------------
    # クイズ2の描画
    # -----------------------------------------------
    if not st.session_state.range_selected:
        st.header("出題範囲を選択してください")

        row1 = st.columns(2)
        row2 = st.columns(2)

        if row1[0].button(Q2_RANGE_LABELS["0~180"][range_mode], use_container_width=True, key="q2_range_0_180"):
            st.session_state.angle_range = "0~180"
            st.session_state.range_selected = True
            q2_initialize_session_state()
            st.rerun()
        if row1[1].button(Q2_RANGE_LABELS["0~360"][range_mode], use_container_width=True, key="q2_range_0_360"):
            st.session_state.angle_range = "0~360"
            st.session_state.range_selected = True
            q2_initialize_session_state()
            st.rerun()

        if row2[0].button(Q2_RANGE_LABELS["-180~180"][range_mode], use_container_width=True, key="q2_range_-180_180"):
            st.session_state.angle_range = "-180~180"
            st.session_state.range_selected = True
            q2_initialize_session_state()
            st.rerun()
        if row2[1].button(Q2_RANGE_LABELS["ALL"][range_mode], use_container_width=True, key="q2_range_all"):
            st.session_state.angle_range = "ALL"
            st.session_state.range_selected = True
            q2_initialize_session_state()
            st.rerun()

    elif st.session_state.show_result:
        end_time = time.time()
        elapsed = Decimal(str(end_time - st.session_state.start_time)).quantize(Decimal('0.01'), ROUND_HALF_UP)

        st.header("✨ クイズ終了！ 結果発表 ✨")
        st.markdown(f"**あなたのスコア: {st.session_state.score} / {st.session_state.max_questions} 問正解**")
        st.write(f"**経過時間: {elapsed} 秒**")
        st.divider()

        _, center_col, _ = st.columns([1, 2.2, 1])
        with center_col:
            st.subheader("全解答の確認")
            table_data = []
            for i, item in enumerate(st.session_state.history, 1):
                if is_func:
                    rad_str = Q2_RADIAN_LABELS[item['angle']]
                    if item['angle'] < 0:
                        func_disp = "$\\" + item['func'] + "\\left(" + rad_str + "\\right)$"
                    else:
                        func_disp = "$\\" + item['func'] + " " + rad_str + "$"
                else:
                    if item['angle'] < 0:
                        func_disp = "$\\text{" + item['func'] + "}\\left(" + str(item['angle']) + "^\\circ\\right)$"
                    else:
                        func_disp = "$\\text{" + item['func'] + "}\\ " + str(item['angle']) + "^\\circ$"

                user_disp = Q2_LATEX_OPTIONS.get(item['user_answer'], item['user_answer'])
                correct_disp = Q2_LATEX_OPTIONS.get(item['correct_answer'], item['correct_answer'])
                mark = "○" if item['is_correct'] else "×"

                table_data.append({
                    "番号": i,
                    "問題": func_disp,
                    "あなたの解答": user_disp,
                    "正解": correct_disp,
                    "正誤": mark
                })
            df = pd.DataFrame(table_data)
            st.table(df.set_index("番号"))

            if st.button("もう一度行う", key="q2_restart", use_container_width=True, type="primary"):
                navigate_to('quiz2')

    else:
        st.subheader(f"問題 {st.session_state.question_count + 1} / {st.session_state.max_questions}")

        current_func = st.session_state.func
        current_angle = st.session_state.angle

        if is_func:
            rad_str = Q2_RADIAN_LABELS[current_angle]
            if current_angle < 0:
                question_latex = "$$ \\" + current_func + "\\left(" + rad_str + "\\right)\\ の値は？ $$"
            else:
                question_latex = "$$ \\" + current_func + " " + rad_str + "\\ の値は？ $$"
        else:
            if current_angle < 0:
                question_latex = rf"$$ \{current_func}\left({current_angle}^\circ\right)\ の値は？ $$"
            else:
                question_latex = rf"$$ \{current_func} {current_angle}^\circ\ の値は？ $$"

        st.markdown(question_latex)

        if current_func in ["sin", "cos"]:
            display_options = Q2_SIN_COS_OPTIONS
        else:
            display_options = Q2_TAN_OPTIONS

        cols = st.columns(4)
        for i, key in enumerate(display_options):
            with cols[i % 4]:
                button_key = f"q2_option_{st.session_state.question_count}_{key}"
                if st.button(Q2_LATEX_OPTIONS[key], use_container_width=True, key=button_key):
                    st.session_state.selected = key
                    q2_check_answer_and_advance()

# ----------------------------------------------------
# --- 🚀 メインアプリケーションロジック ---
# ----------------------------------------------------
# 画面右上の階層ナビゲーションボタン（トップ画面以外で表示）
if st.session_state.page == 'home':
    with st.container():
        col_space, col_top_btn = st.columns([0.8, 0.2])
        with col_top_btn:
            if st.button("トップ画面に戻る", key='go_top_from_home', type="secondary", use_container_width=True):
                navigate_to('top')
    st.markdown("---")
elif st.session_state.page in ['quiz1', 'quiz2']:
    with st.container():
        col_space, col_home_btn, col_top_btn = st.columns([0.6, 0.2, 0.2])
        with col_home_btn:
            if st.button("クイズ選択画面に戻る", key='go_home_top', type="secondary", use_container_width=True):
                navigate_to('home')
        with col_top_btn:
            if st.button("トップ画面に戻る", key='go_top_from_quiz', type="secondary", use_container_width=True):
                navigate_to('top')
    st.markdown("---")

# ページの状態に基づいて表示する関数を切り替え
if st.session_state.page == 'top':
    top_page()
elif st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'quiz1':
    quiz1_transform_page()
elif st.session_state.page == 'quiz2':
    quiz2_famous_angles_page()

# 最終更新日時: 2026-11-19 19:25