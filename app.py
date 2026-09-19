import io
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

# ① 「None」ではなく「-」（未選択）に変更して重複選択エラーを回避
RANKS = ["-", "A", "B+", "B", "B-", "C"]

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

# 初期データの作成関数
def create_default_eval():
    df = pd.DataFrame(
        {"機種名": [m[0] for m in MODELS], "販売台数": [m[1] for m in MODELS]}
    )
    for store in STORES:
        df[store] = "-"
    return df

def create_default_qty():
    df = pd.DataFrame(
        {"機種名": [m[0] for m in MODELS], "販売台数": [m[1] for m in MODELS]}
    )
    for store in STORES:
        df[store] = 0
    return df

# セッション状態の初期化
if "eval_df" not in st.session_state:
    st.session_state.eval_df = create_default_eval()

if "qty_df" not in st.session_state:
    st.session_state.qty_df = create_default_qty()

# サイドバー：データの保存と復元（CSV）
st.sidebar.header("📁 データの保存・読み込み")

# ②-1 CSVでデータダウンロード（保存）
combined_df = pd.concat(
    [
        st.session_state.eval_df.assign(データ種別="評価"),
        st.session_state.qty_df.assign(データ種別="希望台数"),
    ]
)
csv_data = combined_df.to_csv(index=False).encode("utf-8-sig")

st.sidebar.download_button(
    label="💾 バックアップをダウンロード (CSV)",
    data=csv_data,
    file_name="syuukei_data.csv",
    mime="text/csv",
    use_container_width=True,
)

# ②-2 保存したCSVの読み込み（復元）
uploaded_file = st.sidebar.file_uploader(
    "📂 前回保存したCSVを読み込む", type=["csv"]
)
if uploaded_file is not None:
    try:
        loaded_df = pd.read_csv(uploaded_file)
        eval_loaded = loaded_df[loaded_df["データ種別"] == "評価"].drop(
            columns=["データ種別"]
        )
        qty_loaded = loaded_df[loaded_df["データ種別"] == "希望台数"].drop(
            columns=["データ種別"]
        )

        st.session_state.eval_df = eval_loaded
        st.session_state.qty_df = qty_loaded
        st.sidebar.success("✅ データを読み込みました！")
    except Exception as e:
        st.sidebar.error("ファイルの読み込みに失敗しました。")

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

    st.markdown("---")
    if st.button("💾 一時保存する", type="primary", use_container_width=True):
        st.session_state.eval_df = edited_eval
        st.session_state.qty_df = edited_qty
        st.success("✅ 画面上の入力を反映しました！次回以降も残す場合は左メニューからCSVをダウンロードしてください。")

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
