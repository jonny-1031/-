import pandas as pd
import streamlit as st

st.set_page_config(page_title="機種評価・希望台数集計ツール", layout="wide")

st.title("📊 機種評価・希望台数 集計ツール")

# 初期データの定義
TENPO_LIST = [
    "羽曳野",
    "松原",
    "布施",
    "東大阪",
    "きずり",
    "八尾",
    "水走",
    "中石切",
    "大東",
]
HYOUKA_OPTIONS = ["", "A", "B+", "B", "B-", "C"]

# --- セッション状態の初期化 ---
if "df_hyouka" not in st.session_state:
    st.session_state.df_hyouka = pd.DataFrame(
        {
            "機種名": [
                "L 怪盗天使ツインエンジェル2 FX",
                "eシャングリラ・フロンティア",
                "LアカマターL1",
                "Lブルーリフレクション帝L1",
                "eルパン三世15HAM5",
                "eいわせべ 逆転劇への道ver.FKX",
                "e東京喰種MW",
                "L東京喰種FT",
            ],
            "販売台数": [5000, 15000, 1000, 5000, 8000, 2000, 2500, 2500],
            **{t: "" for t in TENPO_LIST},
        }
    )

if "df_kibou" not in st.session_state:
    st.session_state.df_kibou = pd.DataFrame(
        {
            "機種名": st.session_state.df_hyouka["機種名"],
            "販売台数": st.session_state.df_hyouka["販売台数"],
            **{t: 0 for t in TENPO_LIST},
        }
    )

# --- タブ表示 ---
tab1, tab2 = st.tabs(["📝 データ入力", "📋 貼り付け用データ生成"])

with tab1:
    st.subheader("1. 機種評価の入力")
    df_hyouka_edited = st.data_editor(
        st.session_state.df_hyouka,
        column_config={
            t: st.column_config.SelectboxColumn(options=HYOUKA_OPTIONS)
            for t in TENPO_LIST
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_hyouka",
    )

    st.subheader("2. 希望台数の入力")
    df_kibou_edited = st.data_editor(
        st.session_state.df_kibou,
        column_config={
            t: st.column_config.NumberColumn(min_value=0, step=1)
            for t in TENPO_LIST
        },
        num_rows="dynamic",
        use_container_width=True,
        key="editor_kibou",
    )

with tab2:
    st.subheader("貼り付け用マトリクス（店舗 × 機種）")

    # 機種評価マトリクスの作成（行：店舗、列：機種）
    hyouka_matrix = (
        df_hyouka_edited.melt(
            id_vars=["機種名"], value_vars=TENPO_LIST, var_name="店舗", value_name="評価"
        )
        .pivot(index="店舗", columns="機種名", values="評価")
        .reindex(TENPO_LIST)
    )

    # 希望台数マトリクスの作成
    kibou_matrix = (
        df_kibou_edited.melt(
            id_vars=["機種名"],
            value_vars=TENPO_LIST,
            var_name="店舗",
            value_name="台数",
        )
        .pivot(index="店舗", columns="機種名", values="台数")
        .reindex(TENPO_LIST)
    )

    col1, col2 = st.columns(2)

    with col1:
        st.write("**【評価】貼り付け用表**")
        st.dataframe(hyouka_matrix, use_container_width=True)

    with col2:
        st.write("**【希望台数】貼り付け用表**")
        st.dataframe(kibou_matrix, use_container_width=True)

    # Excel出力機能
    import io

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        hyouka_matrix.to_excel(writer, sheet_name="機種評価_貼り付け用")
        kibou_matrix.to_excel(writer, sheet_name="希望台数_貼り付け用")

    st.download_button(
        label="📥 貼り付け用データ(Excel)をダウンロード",
        data=output.getvalue(),
        file_name="集計結果_貼り付け用.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )