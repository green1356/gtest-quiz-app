import os
import streamlit as st
import google.generativeai as genai
import json
import random

# ========================
#  APIキーを取得する関数
# ========================
def get_gemini_api_key() -> str:
    # 1) .streamlit/secrets.toml
    try:
        if "general" in st.secrets and "GEMINI_API_KEY" in st.secrets["general"]:
            return st.secrets["general"]["GEMINI_API_KEY"]
    except Exception:
        pass

    # 2) 環境変数（あれば）
    if os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY")

    # 3) どこにも無ければ空
    return ""

# 実際にAPIキーを取得
API_KEY = get_gemini_api_key()

# ▼ ここで session_state に初期値として入れておく
if "api_key" not in st.session_state:
    st.session_state.api_key = API_KEY

# ページ設定
st.set_page_config(page_title="G検定 問題集")

# --- Chrome 等の自動翻訳を無効化（「問題に耐える」対策） ---
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# ---- ここから CSS -------------------------------------------------
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded');

/* 本文フォント */
html, body, [class*="st-"] {
    font-family: 'Zen Maru Gothic', sans-serif !important;
}

/* Markdownコンテナで影をクリップしないようにする */
[data-testid="stMarkdownContainer"],
.stMarkdown {
    overflow: visible !important;
}

/* ヘッダー（上の白い帯を机の色に揃える） */
[data-testid="stHeader"] {
    background-color: #d6c9ae !important;
}
[data-testid="stHeader"]::before {
    background: none !important;
}

/* アプリ全体の背景（机の色） */
[data-testid="stAppViewContainer"] {
    background-color: #d6c9ae;
}

/* サイドバー（カード風） */
[data-testid="stSidebar"] {
    background-color: #e7e2d8;
    border-right: 1px solid #cbbba0;
}

/* メインコンテンツのレイアウト */
section.main > div.block-container {
    background: none;
    box-shadow: none;
    max-width: 900px;
}

/* タイトル */
h1 {
    color: #333132;
}

/* テーマタグ */
.sub-topic-tag {
    font-size: 14px;
    color: #fff;
    background-color: #a69485;
    padding: 4px 12px;
    clip-path: polygon(0% 0%, 100% 0%, 95% 50%, 100% 100%, 0% 100%, 5% 50%);
    margin-bottom: 10px;
    display: inline-block;
}

/* 質問カード（問題文） */
.question-card {
    background-color: #fffdf7;
    border-left: 6px solid #b8976b;
    border-radius: 8px;
    padding: 24px 28px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.08);
    margin: 24px 0 16px 0;
    color: #3f3225;
    font-size: 18px;
    line-height: 1.8;
}

/* 回答カード（radio 全体をカード化） */
[data-testid="stRadio"] {
    background-color: #ffffff;
    border-left: 6px solid #c3b4a0;
    border-radius: 8px;
    padding: 20px 28px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.06);
    margin: 12px 0 24px 0;
}
[data-testid="stRadio"] label {
    line-height: 1.7;
}

/* 解説ボックス（左側アクセント＋影） */
.explanation-box {
    background-color: #fffaf0;
    padding: 20px 24px;
    border-left: 5px solid #a69485;
    border-radius: 6px;
    color: #594a3c;
    line-height: 1.8;
    box-shadow: 0 3px 8px rgba(0,0,0,0.05);
}

/* ボタン（色味をなじませる） */
button[kind="secondary"], button[kind="primary"] {
    background-color: #fdfcf5 !important;
    border: 1px solid #bfaea2 !important;
    color: #594a3c !important;
}

/* サイドの設定トグル用アイコンを「記号フォント」で表示 */
[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
    font-size: 24px !important;
}

/* ===============================
   スマホ表示向けの微調整
=============================== */
@media (max-width: 600px) {
    section.main > div.block-container {
        max-width: 100% !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .question-card,
    .answer-card,
    .explanation-box {
        padding: 16px 18px;
        font-size: 16px;
    }

    h1 {
        font-size: 22px;
    }
}

/* ===============================
   タイトル（マスキングテープ＋影）
=============================== */

/* タイトル全体を中央に寄せるラッパー */
.title-center-wrapper {
    text-align: center;
    margin-top: 24px;
    margin-bottom: 14px;
}

/* マステ＋影をまとめるラッパー */
.title-tape-wrapper {
    display: inline-block;
    position: relative;
}

/* 影専用レイヤー（ぼかした長方形） */
.title-tape-shadow {
    position: absolute;
    left: 50%;
    top: 65%;
    transform: translateX(-50%);
    width: 115%;
    height: 26px;
    background: rgba(0, 0, 0, 0.50);
    filter: blur(22px);
    opacity: 0.9;
    border-radius: 999px;
    z-index: 0;
}

/* マスキングテープ本体 */
.title-tape {
    position: relative;
    z-index: 1;
    display: inline-block;
    padding: 12px 30px;
    background-color: #a69485;
    color: #ffffff;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 0.55em;
    clip-path: polygon(0% 0%, 100% 0%, 95% 50%, 100% 100%, 0% 100%, 5% 50%);
    border-radius: 10px;
}

/* タイトル下の仕切り線 */
.title-underline {
    width: 100%;
    height: 2px;
    background-color: #bfae9a;
    margin: 6px 0 26px 0;
}

/* ===============================
   タブ（マステ風デザイン）
=============================== */

/* タブ全体（横並びのコンテナ） */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: none !important;
    display: flex;
    justify-content: center;   /* タイトル下で中央寄せに配置 */
    align-items: flex-end;
}

/* デフォルトのボタン装飾を消す */
.stTabs [data-baseweb="tab-list"] button {
    background: none;
    border: none;
    padding: 0;
}

/* タブのラベル（Markdownコンテナ）をマステ化 */
.stTabs [data-baseweb="tab-list"] button > div[data-testid="stMarkdownContainer"] {
    background-color: #a69485;
    color: #ffffff;
    padding: 6px 18px;
    clip-path: polygon(0% 0%, 100% 0%, 95% 50%, 100% 100%, 0% 100%, 5% 50%);
    border-radius: 10px;
    font-weight: 700;
    letter-spacing: 0.25em;
    font-size: 12px;
    box-shadow: none;
    border-bottom: none;
    white-space: nowrap;
}

/* 選択中のタブだけ、少し色を変える */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] > div[data-testid="stMarkdownContainer"] {
    background-color: #b49a80;
}

/* 下に出る赤いハイライト線を消す */
.stTabs [data-baseweb="tab-highlight"] {
    background: none !important;
}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ---- CSS ここまで --------------------------------------------------


# --- 3. 出題範囲の詳細データベース ---
detailed_topics = {
    "人工知能（AI）の定義と歴史": [
        "ダートマス会議", "チューリングテスト", "中国語の部屋", "シンギュラリティ",
        "第1次AIブーム（探索と推論）", "第2次AIブーム（エキスパートシステム）",
        "第3次AIブーム（機械学習・DL）", "フレーム問題", "シンボルグラウンディング問題"
    ],
    "機械学習の具体的な手法": [
        "教師あり学習（回帰・分類）", "教師なし学習（クラスタリング）", "強化学習",
        "ロジスティック回帰", "サポートベクターマシン(SVM)", "決定木・ランダムフォレスト",
        "k-means法", "主成分分析(PCA)", "k近傍法", "アンサンブル学習"
    ],
    "ディープラーニングの概要": [
        "ニューラルネットワークの基礎", "単純パーセプトロン", "多層パーセプトロン",
        "活性化関数（シグモイド・ReLU等）", "誤差逆伝播法", "勾配消失問題",
        "過学習（Overfitting）", "ドロップアウト", "正則化", "バッチ正規化"
    ],
    "ディープラーニングの手法": [
        "CNN（畳み込みニューラルネットワーク）", "RNN（再帰型ニューラルネットワーク）",
        "LSTM / GRU", "オートエンコーダ", "GAN（敵対的生成ネットワーク）",
        "Transformer", "Attention機構", "転移学習・ファインチューニング"
    ],
    "ディープラーニングの研究分野": [
        "画像認識（物体検出・セグメンテーション）", "自然言語処理（BERT・GPT）",
        "音声認識", "強化学習（深層強化学習・AlphaGo）", "生成モデル"
    ],
    "AIの社会実装と法律・倫理": [
        "著作権法（第30条の4等）", "個人情報保護法", "AI倫理指針",
        "GDPR（EU一般データ保護規則）", "説明可能なAI (XAI)",
        "自動運転のレベル定義", "バイアスと公平性", "ディープフェイク"
    ]
}

# --- 4. サイドバー設定 ---
with st.sidebar:
    st.subheader("出題設定")

    selected_main_topic = st.selectbox("出題範囲（大項目）", list(detailed_topics.keys()))
    st.session_state.selected_main_topic = selected_main_topic

    review_mode = st.checkbox(
        "❗ 間違えた問題だけ復習する",
        value=st.session_state.get("review_mode", False)
    )
    st.session_state.review_mode = review_mode

    weak_mode = st.checkbox(
        "📉 苦手分野を優先して出題",
        value=st.session_state.get("weak_mode", False)
    )
    st.session_state.weak_mode = weak_mode

    if st.button("設定をリセット"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.header("⚙ 設定")

    api_key_input = st.text_input(
        "Gemini APIキー（自動設定されます）",
        value=st.session_state.api_key,
        type="password"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    model_name_input = st.text_input(
        "使用するモデル名",
        value=st.session_state.get("model_name", "models/gemini-2.5-flash")
    )
    st.session_state.model_name = model_name_input

# --- 5. タイトル（マステ＋影） ---
st.markdown(
    """
    <div class="title-center-wrapper">
        <div class="title-tape-wrapper">
            <div class="title-tape-shadow"></div>
            <div class="title-tape">G検定 問題集</div>
        </div>
    </div>
    <div class="title-underline"></div>
    """,
    unsafe_allow_html=True
)

# --- APIキー必須チェック ---
if not API_KEY and not st.session_state.api_key:
    st.error("Gemini APIキーが設定されていません。.streamlit/secrets.toml またはサイドバーを確認してください。")
    st.stop()

if not st.session_state.api_key:
    st.error("Gemini APIキーが設定されていません。.streamlit/secrets.toml またはサイドバーを確認してください。")
    st.stop()

# Gemini モデルの初期化
genai.configure(api_key=st.session_state.api_key)
model_name = st.session_state.get("model_name", "models/gemini-2.5-flash")
model = genai.GenerativeModel(model_name)

# --- 6. セッション状態の初期化 ---
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "user_answered" not in st.session_state:
    st.session_state.user_answered = False
if "current_sub_topic" not in st.session_state:
    st.session_state.current_sub_topic = ""
if "total_count" not in st.session_state:
    st.session_state.total_count = 0
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0
if "wrong_history" not in st.session_state:
    st.session_state.wrong_history = []
if "all_history" not in st.session_state:
    st.session_state.all_history = []
if "topic_stats" not in st.session_state:
    st.session_state.topic_stats = {}

# ミニ模試用
if "exam_mode" not in st.session_state:
    st.session_state.exam_mode = False
if "exam_total" not in st.session_state:
    st.session_state.exam_total = 10
if "exam_count" not in st.session_state:
    st.session_state.exam_count = 0
if "exam_correct" not in st.session_state:
    st.session_state.exam_correct = 0
if "exam_history" not in st.session_state:
    st.session_state.exam_history = []

# --- 7. 問題生成関数 ---
def generate_question():
    """通常出題 / 復習モード / 苦手分野優先を切り替えて問題を生成する"""
    review_mode_flag = st.session_state.get("review_mode", False)
    weak_mode_flag = st.session_state.get("weak_mode", False)

    # 1) 復習モード：間違えた問題から出題
    if review_mode_flag and st.session_state.wrong_history:
        q_data = random.choice(st.session_state.wrong_history)
        st.session_state.quiz_data = q_data
        st.session_state.user_answered = False
        st.session_state.current_sub_topic = q_data.get("sub_topic", "")
        return

    # 2) 苦手分野優先モード：正答率が低い大項目を選ぶ
    if weak_mode_flag and st.session_state.topic_stats:
        weakest_topic = None
        weakest_rate = None
        for topic, stats in st.session_state.topic_stats.items():
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)
            rate = (correct / total) if total > 0 else 0.0
            if weakest_rate is None or rate < weakest_rate:
                weakest_rate = rate
                weakest_topic = topic
        selected_main_topic = weakest_topic or st.session_state.get(
            "selected_main_topic", list(detailed_topics.keys())[0]
        )
    else:
        # 通常モード：サイドバーで選んだ大項目
        selected_main_topic = st.session_state.get(
            "selected_main_topic", list(detailed_topics.keys())[0]
        )

    sub_topic_list = detailed_topics[selected_main_topic]
    chosen_keyword = random.choice(sub_topic_list)
    st.session_state.current_sub_topic = chosen_keyword

    prompt = f"""
    あなたはG検定（JDLA Deep Learning for GENERAL）の作問担当者です。
    以下のテーマと重要キーワードに基づいて、本番形式の4択問題を作成してください。
    
    【大テーマ】: {selected_main_topic}
    【今回の重点出題キーワード】: {chosen_keyword}
    
    ※指示:
    - "{chosen_keyword}" の概念や仕組み、関連する知識を問う問題にすること。
    - 単純な用語の意味だけでなく、活用事例や特徴を問う実践的な内容も混ぜること。
    - 解説は、なぜ正解なのかだけでなく、他の選択肢がなぜ違うのかも詳しく書くこと。
    
    出力形式(JSON):
    {{
        "question": "問題文",
        "options": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"],
        "answer": "正解の選択肢（文字列完全一致）",
        "explanation": "詳しい解説"
    }}
    """

    with st.spinner("📝 問題を作成中です…"):
        try:
            response = model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            data["sub_topic"] = chosen_keyword
            data["main_topic"] = selected_main_topic
            st.session_state.quiz_data = data
            st.session_state.user_answered = False
        except Exception as e:
            st.error(f"エラー: {e}")
            st.warning("モデル名を変更して再試行してください。")


# --- 8. タブ（5つ） ---
tab_quiz, tab_score, tab_notes, tab_progress, tab_list = st.tabs(
    ["問題にチャレンジ", "スコア・履歴", "参考ノート", "進捗状況", "出題一覧"]
)

# ==========================
#  タブ1：問題に答える
# ==========================
with tab_quiz:
    # ミニ模試モード切り替えボタン（中央寄せ＆幅そろえ）
    col_space_left, col_mode1, col_mode2, col_space_right = st.columns([1, 2, 2, 1])

    with col_mode1:
        if st.button(
            "通常モードに切り替え",
            disabled=not st.session_state.exam_mode,
            use_container_width=True
        ):
            st.session_state.exam_mode = False
            st.session_state.exam_count = 0
            st.session_state.exam_correct = 0
            st.session_state.quiz_data = None
            st.session_state.user_answered = False
            st.rerun()

    with col_mode2:
        if st.button(
            "ミニ模試（10問）を開始",
            disabled=st.session_state.exam_mode,
            use_container_width=True
        ):
            st.session_state.exam_mode = True
            st.session_state.exam_total = 10
            st.session_state.exam_count = 0
            st.session_state.exam_correct = 0
            st.session_state.quiz_data = None
            st.session_state.user_answered = False
            st.rerun()

    st.markdown("---")

    exam_mode = st.session_state.get("exam_mode", False)
    exam_total = st.session_state.get("exam_total", 10)
    exam_count = st.session_state.get("exam_count", 0)

    # 状態に応じてガイダンスを表示
    if exam_mode:
        st.info(f"🔔 現在：ミニ模試モード（{exam_count} / {exam_total} 問）")
    else:
        st.caption("現在：通常モード（1問ずつ練習）")

    # ここで自動的に最初の問題を作成（ボタンなし）
    if st.session_state.quiz_data is None:
        generate_question()

    q_data = st.session_state.quiz_data

    # テーマタグ
    st.markdown(
        f'<div class="sub-topic-tag">テーマ：{st.session_state.current_sub_topic}</div>',
        unsafe_allow_html=True
    )

    # 問題カード
    st.markdown(
        f'<div class="question-card">Q. {q_data["question"]}</div>',
        unsafe_allow_html=True
    )

    # 回答ラジオ
    user_choice = st.radio(
        "回答を選択：",
        q_data["options"],
        key="choice",
        label_visibility="collapsed",
        disabled=st.session_state.user_answered
    )

    # --- 回答前 ---
    if not st.session_state.user_answered:
        if st.button("解答と解説", key="answer_button"):
            correct_answer = q_data["answer"]
            is_correct = (user_choice == correct_answer)

            # 通算カウント
            st.session_state.total_count += 1
            if is_correct:
                st.session_state.correct_count += 1
            else:
                st.session_state.wrong_history.append(q_data)

            # 分野別統計
            topic = q_data.get("main_topic", st.session_state.get("selected_main_topic"))
            stats = st.session_state.topic_stats.get(topic, {"total": 0, "correct": 0})
            stats["total"] += 1
            if is_correct:
                stats["correct"] += 1
            st.session_state.topic_stats[topic] = stats

            # 全履歴
            history_entry = {
                "main_topic": topic,
                "sub_topic": q_data.get("sub_topic", st.session_state.current_sub_topic),
                "question": q_data["question"],
                "options": q_data["options"],
                "answer": correct_answer,
                "explanation": q_data["explanation"],
                "user_choice": user_choice,
                "correct": is_correct,
            }
            st.session_state.all_history.append(history_entry)

            # ミニ模試モードのカウント
            if st.session_state.exam_mode:
                st.session_state.exam_count += 1
                if is_correct:
                    st.session_state.exam_correct += 1

            st.session_state.user_answered = True
            st.rerun()

    # --- 回答後 ---
    else:
        st.markdown("---")
        correct_answer = q_data["answer"]
        last_choice = st.session_state.all_history[-1]["user_choice"]
        is_correct = (last_choice == correct_answer)

        if is_correct:
            st.success("🎉 正解！")
        else:
            st.error("😢 残念… 不正解です。")
            st.markdown(f"正解: **{correct_answer}**")

        # 通算進捗
        if st.session_state.total_count > 0:
            rate = st.session_state.correct_count / st.session_state.total_count * 100
            st.markdown(
                f"📊 **進捗：{st.session_state.total_count}問中 "
                f"{st.session_state.correct_count}問正解（正答率 {rate:.1f}%）**"
            )

        # 解説
        with st.expander("🔍 解説を表示する（クリックで開閉）"):
            st.markdown(
                f'<div class="explanation-box"><b>【解説】</b><br>{q_data["explanation"]}</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # 次へ進む・模試終了の制御
        if st.session_state.exam_mode:
            if st.session_state.exam_count < st.session_state.exam_total:
                if st.button("➡️ 次の問題へ"):
                    st.session_state.user_answered = False
                    generate_question()
                    st.rerun()
            else:
                exam_total = st.session_state.exam_total
                exam_correct = st.session_state.exam_correct
                exam_rate = exam_correct / exam_total * 100 if exam_total > 0 else 0.0

                st.success("🎓 ミニ模試（10問）が終了しました。")
                st.markdown(
                    f"- 出題数：**{exam_total}問**  \n"
                    f"- 正解数：**{exam_correct}問**  \n"
                    f"- 正答率：**{exam_rate:.1f}%**"
                )

                if st.button("結果を保存して通常モードに戻る"):
                    st.session_state.exam_history.append(
                        {"total": exam_total, "correct": exam_correct, "rate": exam_rate}
                    )
                    st.session_state.exam_mode = False
                    st.session_state.exam_count = 0
                    st.session_state.exam_correct = 0
                    st.session_state.quiz_data = None
                    st.session_state.user_answered = False
                    st.rerun()
        else:
            if st.button("➡️ 次の問題へ"):
                st.session_state.user_answered = False
                generate_question()
                st.rerun()

# ==========================
#  タブ2：スコア・履歴
# ==========================
with tab_score:
    st.subheader("📊 現在のスコア")

    if st.session_state.total_count == 0:
        st.info("まずは問題を解いてみてください。")
    else:
        rate = st.session_state.correct_count / st.session_state.total_count * 100
        st.markdown(
            f"- 解いた問題数：**{st.session_state.total_count}問**  \n"
            f"- 正解数：**{st.session_state.correct_count}問**  \n"
            f"- 正答率：**{rate:.1f}%**"
        )

    st.markdown("---")
    st.subheader("🎓 直近のミニ模試結果")

    if st.session_state.exam_history:
        last = st.session_state.exam_history[-1]
        exam_total = last["total"]
        exam_correct = last["correct"]
        exam_rate = last["rate"]
        st.markdown(
            f"- 出題数：**{exam_total}問**  \n"
            f"- 正解数：**{exam_correct}問**  \n"
            f"- 正答率：**{exam_rate:.1f}%**"
        )
    else:
        st.caption("ミニ模試を完走すると、ここに結果が表示されます。")

    st.markdown("---")
    st.subheader("📚 学習履歴")

    if not st.session_state.all_history:
        st.info("保存された学習履歴はまだありません。")
    else:
        for i, h in enumerate(reversed(st.session_state.all_history), start=1):
            mark = "✅" if h["correct"] else "❌"
            st.markdown(
                f"**{i}. {mark} {h['main_topic']}｜{h['sub_topic']}**  \n"
                f"Q. {h['question']}"
            )

# ==========================
#  タブ3：参考ノート
# ==========================
with tab_notes:
    st.subheader("📘 参考ノート（解説まとめ）")

    if not st.session_state.all_history:
        st.info("問題を解くと、ここに解説ノートが自動でたまっていきます。")
    else:
        for i, h in enumerate(reversed(st.session_state.all_history), start=1):
            st.markdown(
                f"**{i}. {h['main_topic']}｜{h['sub_topic']}**  \n"
                f"Q. {h['question']}",
            )
            st.markdown(
                f'<div class="explanation-box"><b>【解説】</b><br>{h["explanation"]}</div>',
                unsafe_allow_html=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

# ==========================
#  タブ4：進捗
# ==========================
with tab_progress:
    st.subheader("📈 分野別の進捗")

    if not st.session_state.topic_stats:
        st.info("まだ分野別の統計はありません。問題に回答すると、自動的に集計されます。")
    else:
        for topic, stats in st.session_state.topic_stats.items():
            total = stats["total"]
            correct = stats["correct"]
            rate = correct / total * 100 if total > 0 else 0.0
            st.markdown(
                f"**{topic}**  \n"
                f"- 解いた数：{total}問  \n"
                f"- 正解数：{correct}問  \n"
                f"- 正答率：{rate:.1f}%"
            )
            st.markdown("---")

# ==========================
#  タブ5：出題一覧
# ==========================
with tab_list:
    st.subheader("🔍 出題一覧")

    if not st.session_state.all_history:
        st.info("まだ出題された問題はありません。")
    else:
        for i, h in enumerate(reversed(st.session_state.all_history), start=1):
            mark = "✅" if h["correct"] else "❌"
            st.markdown(
                f"**{i}. {mark} {h['main_topic']}｜{h['sub_topic']}**  \n"
                f"Q. {h['question']}"
            )

# --- 最初からやり直すボタン ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("最初からやり直す"):
    st.session_state.quiz_data = None
    st.session_state.user_answered = False
    st.session_state.total_count = 0
    st.session_state.correct_count = 0
    st.session_state.wrong_history = []
    st.session_state.all_history = []
    st.session_state.topic_stats = {}
    st.session_state.exam_mode = False
    st.session_state.exam_count = 0
    st.session_state.exam_correct = 0
    st.session_state.exam_history = []
    st.rerun()
