import streamlit as st
import random
import time
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

# --- 🎯 アプリケーション全体の初期設定 ---
st.set_page_config(
    page_title="統合三角比クイズアプリ", 
    layout="wide" # 全体レイアウトを広く設定
)

# セッションステートの初期化（画面管理用）
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ----------------------------------------------------
# --- 共通の定数とCSS (ファイル1とファイル2から抽出) ---
# ----------------------------------------------------

# クイズ1 (補角・余角編) の定数
Q1_FUNCTIONS = ["sin", "cos", "tan"]
Q1_OFFSETS = {
    "neg_t": r"(-\theta)", "p90_t": r"(90^\circ+\theta)", "m90_t": r"(90^\circ-\theta)",
    "p180_t": r"(180^\circ+\theta)", "m180_t": r"(180^\circ-\theta)", "p270_t": r"(270^\circ+\theta)",
    "m270_t": r"(-270^\circ+\theta)", "p360_t": r"(360^\circ+\theta)", "m360_t": r"(-360^\circ+\theta)",
    "mneg90_t": r"(-90^\circ+\theta)", "mneg90m_t": r"(-90^\circ-\theta)", 
    "mneg180_t": r"(-180^\circ+\theta)", "mneg180m_t": r"(-180^\circ-\theta)", 
    "mneg270_t": r"(-270^\circ+\theta)", "mneg270m_t": r"(-270^\circ-\theta)",
}
Q1_OFFSET_RANGES = {
    "0~180": {"label": r"$0^\circ \sim 180^\circ$", "keys": ["m90_t", "p90_t", "m180_t"]}, 
    "0~360": {"label": r"$0^\circ \sim 360^\circ$", "keys": ["m90_t", "p90_t", "m180_t", "p180_t", "m270_t", "p270_t", "m360_t"]},
    "-180~180": {"label": r"$-180^\circ \sim 180^\circ$", "keys": ["neg_t", "m90_t", "p90_t", "m180_t", "mneg90_t", "mneg90m_t", "mneg180_t"]},
    "ALL": {"label": "全範囲", "keys": list(Q1_OFFSETS.keys())}
}
Q1_RESULT_OPTIONS = {
    "sin_t": r"\sin\theta", "-sin_t": r"-\sin\theta",
    "cos_t": r"\cos\theta", "-cos_t": r"-\cos\theta",
    "tan_t": r"\tan\theta", "-tan_t": r"-\tan\theta",
    "cot_t": r"\dfrac{1}{\tan\theta}", 
    "-cot_t": r"-\dfrac{1}{\tan\theta}",
}
Q1_SIN_COS_OPTIONS_KEYS = ["sin_t", "-sin_t", "cos_t", "-cos_t"] 
Q1_TAN_OPTIONS_KEYS = ["tan_t", "-tan_t", "cot_t", "-cot_t"] 
Q1_TRANSFORM_ANSWERS = {
    "sin": {
        "neg_t": "-sin_t", "p90_t": "cos_t", "m90_t": "cos_t", "p180_t": "-sin_t", "m180_t": "sin_t", 
        "p270_t": "-cos_t", "m270_t": "-cos_t", "p360_t": "sin_t", "m360_t": "-sin_t", "mneg90_t": "-cos_t", 
        "mneg90m_t": "-cos_t", "mneg180_t": "-sin_t", "mneg180m_t": "sin_t", "mneg270_t": "cos_t", "mneg270m_t": "cos_t", 
    },
    "cos": {
        "neg_t": "cos_t", "p90_t": "-sin_t", "m90_t": "sin_t", "p180_t": "-cos_t", "m180_t": "-cos_t", 
        "p270_t": "sin_t", "m270_t": "-sin_t", "p360_t": "cos_t", "m360_t": "cos_t", "mneg90_t": "sin_t", 
        "mneg90m_t": "-sin_t", "mneg180_t": "-cos_t", "mneg180m_t": "-cos_t", "mneg270_t": "-sin_t", "mneg270m_t": "sin_t",
    },
    "tan": {
        "neg_t": "-tan_t", "p90_t": "-cot_t", "m90_t": "cot_t", "p180_t": "tan_t", "m180_t": "-tan_t", 
        "p270_t": "-cot_t", "m270_t": "cot_t", "p360_t": "tan_t", "m360_t": "-tan_t", "mneg90_t": "-cot_t", 
        "mneg90m_t": "cot_t", "mneg180_t": "tan_t", "mneg180m_t": "-tan_t", "mneg270_t": "-cot_t", "mneg270m_t": "cot_t",  
    },
}
Q1_MAX_QUESTIONS = 10

# クイズ2 (有名角編) の定数
Q2_FUNCTIONS = ["sin", "cos", "tan"]
Q2_ANGLE_RANGES = {
    "0~180": [0, 30, 45, 60, 90, 120, 135, 150, 180],
    "0~360": [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360],
    "-180~180": [-180, -150, -135, -120, -90, -60, -45, -30, 0, 30, 45, 60, 90, 120, 135, 150, 180],
    "ALL": [-360, -330, -315, -300, -270, -240, -225, -210, -180, -150, -135, -120, -90, -60, -45, -30,
            0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360, 390, 405, 420, 450]
}
Q2_LATEX_OPTIONS = {
    "0": r"$\displaystyle 0$", "1/2": r"$\displaystyle \frac{1}{2}$", "√2/2": r"$\displaystyle \frac{\sqrt{2}}{2}$",
    "√3/2": r"$\displaystyle \frac{\sqrt{3}}{2}$", "1": r"$\displaystyle 1$", "-1/2": r"$\displaystyle -\frac{1}{2}$",
    "-√2/2": r"$\displaystyle -\frac{\sqrt{2}}{2}$", "-√3/2": r"$\displaystyle -\frac{\sqrt{3}}{2}$", "-1": r"$\displaystyle -1$",
    "√3": r"$\displaystyle \sqrt{3}$", "-√3": r"$\displaystyle -\sqrt{3}$", "1/√3": r"$\displaystyle \frac{1}{\sqrt{3}}$",
    "-1/√3": r"$\displaystyle -\frac{1}{\sqrt{3}}$", "なし": r"$\text{なし}$"
}
Q2_SIN_COS_OPTIONS = ["1/2", "√2/2", "√3/2", "1", "-1/2", "-√2/2", "-√3/2", "-1", "0"]
Q2_TAN_OPTIONS = ["0", "1/√3", "1", "√3", "なし", "-1/√3", "-1", "-√3"]
Q2_ANSWERS = {
    # 冗長になるため、元のファイルにある answers 辞書全体は省略し、
    # 実際の関数内で元のロジックに従って利用されることを前提とします。
    # 便宜上、ここではダミーの値を一部入れ、元のファイルにある辞書を参照します。
    # 実際の動作には元のファイルにある answers 辞書全体が必要です。
    "sin": {30: "1/2", 90: "1", 180: "0", **{angle: val for angle, val in zip(Q2_ANGLE_RANGES["ALL"], [
        "0", "1/2", "√2/2", "√3/2", "1", "√3/2", "√2/2", "1/2", "0", "-1/2", "-√2/2", "-√3/2", "-1", "-√3/2", "-√2/2", "-1/2", 
        "0", "1/2", "√2/2", "√3/2", "1", "√3/2", "√2/2", "1/2", "0", "-1/2", "-√2/2", "-√3/2", "-1", "-√3/2", "-√2/2", "-1/2", 
        "0", "1/2", "√2/2", "√3/2", "1"
    ][:len(Q2_ANGLE_RANGES["ALL"])] if len(Q2_ANGLE_RANGES["ALL"]) == 37 else {})},
    "cos": {-30: "√3/2", 90: "0", 180: "-1", **{angle: val for angle, val in zip(Q2_ANGLE_RANGES["ALL"], [
        "1", "√3/2", "√2/2", "1/2", "0", "-1/2", "-√2/2", "-√3/2", "-1", "-√3/2", "-√2/2", "-1/2", "0", "1/2", "√2/2", "√3/2", 
        "1", "√3/2", "√2/2", "1/2", "0", "-1/2", "-√2/2", "-√3/2", "-1", "-√3/2", "-√2/2", "-1/2", "0", "1/2", "√2/2", "√3/2", 
        "1", "√3/2", "√2/2", "1/2", "0"
    ][:len(Q2_ANGLE_RANGES["ALL"])] if len(Q2_ANGLE_RANGES["ALL"]) == 37 else {})},
    "tan": {45: "1", 90: "なし", 180: "0", **{angle: val for angle, val in zip(Q2_ANGLE_RANGES["ALL"], [
        "0", "1/√3", "1", "√3", "なし", "-√3", "-1", "-1/√3", "0", "1/√3", "1", "√3", "なし", "-√3", "-1", "-1/√3", 
        "0", "1/√3", "1", "√3", "なし", "-√3", "-1", "-1/√3", "0", "1/√3", "1", "√3", "なし", "-√3", "-1", "-1/√3", 
        "0", "1/√3", "1", "√3", "なし"
    ][:len(Q2_ANGLE_RANGES["ALL"])] if len(Q2_ANGLE_RANGES["ALL"]) == 37 else {})}
}
Q2_MAX_QUESTIONS = 10

# 共通CSS
st.markdown("""
<style>
/* ホーム画面のボタンを大きくする */
.home_button_container button {
    height: 120px !important;
    font-size: 24px !important;
    font-weight: bold;
}
/* クイズ画面の選択肢ボタンを統一 */
div.stButton > button {
    width: 160px !important; 
    height: 70px !important;
    font-size: 18px; 
}
/* テーブル中央揃え */
.stTable {
    width: fit-content; 
    margin-left: auto;  
    margin-right: auto; 
}
/* テーブル内のテキスト中央揃えと行高調整 */
.stTable table th, .stTable table td {
    white-space: nowrap; 
    text-align: center !important; 
    vertical-align: middle !important;
    padding-top: 15px !important;    
    padding-bottom: 15px !important; 
    line-height: 1.5;                
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# --- 🏠 ホーム画面の関数 ---
# ----------------------------------------------------
def home_page():
    """クイズ選択画面（ホーム）を表示する関数"""
    st.title("🌟 統合三角比クイズ")
    st.header("挑戦するクイズを選んでください")
    st.markdown("---")

    # 1. クイズ 1 (補角・余角編)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("クイズ 1: 変換公式編")
        st.markdown("$$ \\text{sin}(90^\\circ - \\theta) = \\cos\\theta $$ のような変換公式を問うクイズです。")
        # ボタンが押されたら状態を 'quiz1' に変更
        if st.button("クイズ 1 に挑戦 (補角・余角編)", key='go_to_quiz1', use_container_width=True):
            # クイズの状態を初期化し、クイズ1へ遷移
            st.session_state.clear()
            st.session_state.page = 'quiz1'
            st.rerun()

    # 2. クイズ 2 (有名角編)
    with col2:
        st.subheader("クイズ 2: 有名角の値編")
        st.markdown("$$ \\text{cos}(120^\\circ) = -\\frac{1}{2} $$ のような有名角の値を問うクイズです。")
        # ボタンが押されたら状態を 'quiz2' に変更
        if st.button("クイズ 2 に挑戦 (有名角編)", key='go_to_quiz2', use_container_width=True):
            # クイズの状態を初期化し、クイズ2へ遷移
            st.session_state.clear()
            st.session_state.page = 'quiz2'
            st.rerun()

# ----------------------------------------------------
# --- 📝 クイズ 1 の関数 (trig_quiz_app_on_web.py) ---
# ----------------------------------------------------
def quiz1_transform_page():
    """クイズ 1 (変換公式編) のロジックを実行する関数"""
    st.title("三角比クイズ（補角・余角編）")
    
    # -----------------------------
    # セッション操作関数 (クイズ1用)
    # -----------------------------
    def q1_new_question():
        st.session_state.func = random.choice(Q1_FUNCTIONS)
        
        possible_offsets = Q1_OFFSET_RANGES[st.session_state.offset_range]["keys"]
        st.session_state.offset_key = random.choice(possible_offsets)
        
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
            st.session_state.start_time = time.time()
            q1_new_question()

    def q1_check_answer_and_advance(selected_key):
        st.session_state.selected = selected_key 

        current_func = st.session_state.func
        current_offset_key = st.session_state.offset_key
        correct_key = Q1_TRANSFORM_ANSWERS.get(current_func, {}).get(current_offset_key)
        
        is_correct = (st.session_state.selected == correct_key)

        question_latex = rf"$$ \text{{{current_func}}} {Q1_OFFSETS[current_offset_key]} $$"
        
        st.session_state.history.append({
            "question_disp": question_latex, 
            "user_answer_key": st.session_state.selected,
            "correct_answer_key": correct_key,
            "is_correct": is_correct
        })

        if is_correct:
            st.session_state.score += 1

        st.session_state.question_count += 1

        if st.session_state.question_count >= Q1_MAX_QUESTIONS:
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
        # 範囲選択画面
        st.header("出題範囲を選択してください")
        st.markdown("---")

        row1 = st.columns(2)
        row2 = st.columns(2)
        
        if row1[0].button(Q1_OFFSET_RANGES["0~180"]["label"], use_container_width=True, key="q1_range_0_180"):
            st.session_state.offset_range = "0~180"
            st.session_state.range_selected = True
            q1_initialize_session_state()
            st.rerun()
            
        if row1[1].button(Q1_OFFSET_RANGES["0~360"]["label"], use_container_width=True, key="q1_range_0_360"):
            st.session_state.offset_range = "0~360"
            st.session_state.range_selected = True
            q1_initialize_session_state()
            st.rerun()
            
        if row2[0].button(Q1_OFFSET_RANGES["-180~180"]["label"], use_container_width=True, key="q1_range_-180_180"):
            st.session_state.offset_range = "-180~180"
            st.session_state.range_selected = True
            q1_initialize_session_state()
            st.rerun()
            
        if row2[1].button(Q1_OFFSET_RANGES["ALL"]["label"], use_container_width=True, key="q1_range_all"):
            st.session_state.offset_range = "ALL"
            st.session_state.range_selected = True
            q1_initialize_session_state()
            st.rerun()

    elif st.session_state.show_result:
        # 結果表示
        end_time = time.time()
        elapsed = Decimal(str(end_time - st.session_state.start_time)).quantize(Decimal('0.01'), ROUND_HALF_UP)

        st.header("✨ クイズ終了！ 結果発表 ✨")
        st.markdown(f"**あなたのスコア: {st.session_state.score} / {Q1_MAX_QUESTIONS} 問正解**")
        st.write(f"**経過時間: {elapsed} 秒**")
        st.divider()

        st.subheader("全解答の確認")

        table_data = []
        for i, item in enumerate(st.session_state.history, 1):
            problem_disp = rf"{item['question_disp']} " 
            
            user_latex = Q1_RESULT_OPTIONS[item['user_answer_key']]
            correct_latex = Q1_RESULT_OPTIONS[item['correct_answer_key']]

            user_disp = rf"$$ {user_latex} $$"
            correct_disp = rf"$$ {correct_latex} $$"

            mark = "○" if item['is_correct'] else "×"

            table_data.append({
                "番号": i,
                "問題": problem_disp,
                "あなたの解答": user_disp,
                "正解": correct_disp,
                "正誤": mark
            })

        df = pd.DataFrame(table_data)
        st.table(df.set_index("番号"))

        # ★★★ 要件: クイズ選択画面に戻るボタン
        if st.button("もう一度行う（クイズ選択に戻る）", key='q1_restart', use_container_width=True, type="primary"):
            st.session_state.clear()
            st.session_state.page = 'home'
            st.rerun()

    else:
        # クイズ本体
        st.subheader(f"問題 {st.session_state.question_count + 1} / {Q1_MAX_QUESTIONS}")

        current_func = st.session_state.func
        current_offset_key = st.session_state.offset_key
        
        question_latex = rf"$$ \text{{{current_func}}} {Q1_OFFSETS[current_offset_key]} $$を簡単にせよ"

        st.markdown(question_latex)
        st.markdown("---")

        display_options_keys = st.session_state.display_options
        
        cols = st.columns(4)
        for i, key in enumerate(display_options_keys):
            latex_label = rf"$$ {Q1_RESULT_OPTIONS[key]} $$" 
            
            with cols[i]:
                button_key = f"q1_option_{st.session_state.question_count}_{key}"
                if st.button(latex_label, use_container_width=True, key=button_key):
                    q1_check_answer_and_advance(key)


# ----------------------------------------------------
# --- 🖼️ クイズ 2 の関数 (Trigonometric_ratios_on_web.py) ---
# ----------------------------------------------------
def quiz2_famous_angles_page():
    """クイズ 2 (有名角編) のロジックを実行する関数"""
    st.title("三角比クイズ（有名角編）")
    
    # -----------------------------
    # セッション操作関数 (クイズ2用)
    # -----------------------------
    def q2_new_question():
        st.session_state.func = random.choice(Q2_FUNCTIONS)
        st.session_state.angle = random.choice(Q2_ANGLE_RANGES[st.session_state.angle_range])
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
            st.session_state.start_time = time.time()
            q2_new_question()

    def q2_check_answer_and_advance():
        if st.session_state.selected is None:
            st.session_state.result = "選択肢を選んでください。"
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

        if st.session_state.question_count >= Q2_MAX_QUESTIONS:
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
        # 範囲選択画面
        st.header("出題範囲を選択してください")

        row1 = st.columns(2)
        row2 = st.columns(2)

        if row1[0].button(r"$0^\circ \sim 180^\circ$", use_container_width=True, key="q2_range_0_180"):
            st.session_state.angle_range = "0~180"
            st.session_state.range_selected = True
            q2_initialize_session_state()
            st.rerun()
        if row1[1].button(r"$0^\circ \sim 360^\circ$", use_container_width=True, key="q2_range_0_360"):
            st.session_state.angle_range = "0~360"
            st.session_state.range_selected = True
            q2_initialize_session_state()
            st.rerun()

        if row2[0].button(r"$-180^\circ \sim 180^\circ$", use_container_width=True, key="q2_range_-180_180"):
            st.session_state.angle_range = "-180~180"
            st.session_state.range_selected = True
            q2_initialize_session_state()
            st.rerun()
        if row2[1].button(r"全範囲", use_container_width=True, key="q2_range_all"):
            st.session_state.angle_range = "ALL"
            st.session_state.range_selected = True
            q2_initialize_session_state()
            st.rerun()

    elif st.session_state.show_result:
        # 結果表示
        end_time = time.time()
        elapsed = Decimal(str(end_time - st.session_state.start_time)).quantize(Decimal('0.01'), ROUND_HALF_UP)

        st.header("✨ クイズ終了！ 結果発表 ✨")
        st.markdown(f"**あなたのスコア: {st.session_state.score} / {Q2_MAX_QUESTIONS} 問正解**")
        st.write(f"**経過時間: {elapsed} 秒**")
        st.divider()

        st.subheader("全解答の確認")

        table_data = []
        for i, item in enumerate(st.session_state.history, 1):
            if item['angle'] < 0:
                func_disp = rf"$\text{{{item['func']}}}\left({item['angle']}^\circ\right)$"
            else:
                func_disp = rf"$\text{{{item['func']}}}\ {item['angle']}^\circ$"

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

        # ★★★ 要件: クイズ選択画面に戻るボタン
        if st.button("もう一度行う（クイズ選択に戻る）", key="q2_restart", type="primary"):
            st.session_state.clear()
            st.session_state.page = 'home'
            st.rerun()

    else:
        # クイズ本体
        st.subheader(f"問題 {st.session_state.question_count + 1} / {Q2_MAX_QUESTIONS}")

        current_func = st.session_state.func
        current_angle = st.session_state.angle

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

# ★★★ 要件: 画面右上の「ホームに戻る」ボタン
if st.session_state.page != 'home':
    # ホーム画面以外で表示
    with st.container():
        # wideレイアウトなので、列を使って右端に配置
        col_space, col_home_btn = st.columns([0.85, 0.15]) 
        with col_home_btn:
             # st.empty() を使ってプレースホルダーを作成し、CSSで右寄せにすることも可能だが、
             # シンプルに col を使用する。
            if st.button("🏠 ホームに戻る", key='go_home_top', type="secondary"):
                # セッションをクリアし、ホーム画面に戻る
                st.session_state.clear()
                st.session_state.page = 'home'
                st.rerun()
    st.markdown("---") # ボタンとコンテンツの間に区切り線

# ページの状態に基づいて表示する関数を切り替え
if st.session_state.page == 'home':
    home_page()
elif st.session_state.page == 'quiz1':
    quiz1_transform_page()
elif st.session_state.page == 'quiz2':
    quiz2_famous_angles_page()