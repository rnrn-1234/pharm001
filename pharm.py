import pandas as pd
import altair as alt
import streamlit as st

st.title('店舗別 患者数・処方数')

#サイドバー
st.sidebar.write("""
## 表示内容選択
""")

np = st.sidebar.radio(
    "どちらかを選択してください",
    ('患者数','処方数')
)

st.sidebar.write("""
## 横軸幅選択（工事中）
""")
xmin , xmax = st.sidebar.slider(
    "範囲を指定してください",
    201707, 202103, (201707, 202103)
    )

st.sidebar.write("""
## 縦軸幅選択
""")
ymin , ymax = st.sidebar.slider(
    "範囲を指定してください",
    0, 5000, (0, 2000), 500
    )


# データ取得関数
@st.cache
def get_data(select_pharm, np):

    # csvデータ取得
    df = pd.read_csv('pharm_data.csv')
    # アイセイデータのみ抽出
    df_a = df[df['薬局チェーンID'].astype(int) == 1012]
    df_a = df_a.set_index('年月')

    df = pd.DataFrame()
    for pharmacy in select_pharm:
        df_pharm = df_a[df_a['店舗名称'] == pharmacy] # 対象店舗のデータを取得
        ninzu = df_pharm[[np]]                        # 患者数・処方数どちらかの数値を取得
        ninzu.columns = [pharmacy]                    # カラム名を店舗名に変更
        ninzu = ninzu.T # 軸変換
        ninzu.index.name = 'Name'  # indexの名前を"Name"に変更
        df = pd.concat([df, ninzu]) # データフレームに追加
    return df

@st.cache
def get_list():

    # csvデータ取得
    df = pd.read_csv('pharm_data.csv')
    # アイセイデータのみ抽出
    df_a = df[df['薬局チェーンID'].astype(int) == 1012]
    plist = df_a['店舗名称'].unique()
    return plist


# 薬局リストセット
select_pharm = get_list()

# データセット
df = get_data(select_pharm, np)

# 複数選択リスト
pharmacies = st.multiselect(
    '店舗を選択してください',
    list(select_pharm),
    ['アイセイ薬局富水店'],
)

if not pharmacies:
    st.error('少なくとも一軒選んでください')
else:
    if len(pharmacies) > 5:
        st.info('選択した店舗が5件を超えました')

    # 表データ取得
    data = df.loc[pharmacies]
    # 表のセット
    data_list = data
    # st.dataframe(data_list)

    # グラフ用データ整形
    data = data.T.reset_index()
    data = pd.melt(data, id_vars=['年月']).rename(columns={'Name':'店舗','value':f'{np}'})

    # グラフ設定
    chart = (
        alt.Chart(data)
        .mark_line(opacity=0.8, clip=True) #折れ線グラフ
        .encode(
            x="年月:N",
            y=alt.Y(f"{np}:Q", stack=None, scale=alt.Scale(domain=[ymin,ymax])),
            color='店舗:N',
            tooltip=["店舗",f"{np}"]
        )
    )
    # グラフセット
    st.altair_chart(chart, use_container_width=True)

    # 表のセット
    st.dataframe(data_list)

