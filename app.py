import pandas as pd
import streamlit as st

st.set_page_config(page_title="機種評価・希望台数ツール", layout="wide")

st.title("📱 機種評価・希望台数まとめツール")

# マスタデータ設定
STORES = [
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
RANKS = ["A", "B+", "B", "B-", "C", "None"]

MODELS = [
    ("L 怪盗天使ツインエンジェル2 FX", 5000),
    ("e シャングリラ・フロンティア", 15000),
    ("L アカマターL1", 1000),
    ("L ブルーリフレクション帝L1", 5000),
    ("e ルパン三世15HAM5", 8000),
    ("e いわせべ 逆転劇への道 ver.FKX", 2000),
    ("e 東京喰種MW", 2500),
    ("L 東京喰種FT", 2500),
]

# セッション状態の初期化
if "eval_df" not in st.session_state:
    df_eval = pd.DataFrame(
        {"機種名": [m[0] for m in MODELS], "販売台数": [m[1] for m in MODELS]}
    )
    for store in STORES:
        df_eval[store] = "None"
    st.session_state.eval_df = df_eval

if "qty_df" not in st.session_state:
    df_qty = pd.DataFrame(
        {"機種名": [m[0] for m in MODELS], "販売台数": [m[1] for m in MODELS]}
    )
    for store in STORES:
        df_qty[store] = 0
    st.session_state.qty_df = df_qty

# タブ切り替え
tab1, tab2 = st.tabs(["📝 データ入力", "📊 貼り付け用データ生成"])

with tab1:
    with st.expander("1. 機種評価の入力（タップで開閉）", expanded=True):
        edited_eval = st.data_editor(
            st.session_state.eval_df,
            column_config={
                store: st.column_config.SelectboxColumn(
                    store, options=RANKS, required=True, width="small"
                )
                for store in STORES
            },
            use_container_width=True,
            hide_index=True,
            key="editor_eval",
        )

    with st.expander("2. 希望台数の入力（タップで開閉）", expanded=True):
        edited_qty = st.data_editor(
            st.session_state.qty_df,
            column_config={
                store: st.column_config.NumberColumn(
                    store, min_value=0, step=1, width="small"
                )
                for store in STORES
            },
            use_container_width=True,
            hide_index=True,
            key="editor_qty",
        )

    # 分かりやすい保存ボタンを追加
    st.markdown("---")
    if st.button("💾 入力内容を保存する", type="primary", use_container_width=True):
        st.session_state.eval_df = edited_eval
        st.session_state.qty_df = edited_qty
        st.success("✅ 入力したデータを保存しました！「貼り付け用データ生成」タブで確認できます。")

with tab2:
    st.subheader("貼り付け用データ")

    # 評価集計
    eval_melted = st.session_state.eval_df.melt(
        id_vars=["機種名", "販売台数"],
        value_vars=STORES,
        var_name="店舗",
        value_name="評価",
    )
    eval_pivot = eval_melted.pivot(
        index="店舗", columns="機種名", values="評価"
    ).reindex(STORES)

    # 希望台数集計
    qty_melted = st.session_state.qty_df.melt(
        id_vars=["機種名", "販売台数"],
        value_vars=STORES,
        var_name="店舗",
        value_name="希望台数",
    )
    qty_pivot = qty_melted.pivot(
        index="店舗", columns="機種名", values="希望台数"
    ).reindex(STORES)

    st.write("▼ 機種評価マトリクス")
    st.dataframe(eval_pivot, use_container_width=True)

    st.write("▼ 希望台数マトリクス")
    st.dataframe(qty_pivot, use_container_width=True)

    st.write("▼ 希望台数マトリクス")
    st.dataframe(qty_pivot, use_container_width=True)
