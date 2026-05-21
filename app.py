import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 設定網頁標題與圖示
st.set_page_config(page_title="羅馬機場航點分析", page_icon="✈️", layout="wide")

st.title("✈️ 羅馬達文西機場 (FCO) 全球航點與地緣政治視覺化")
st.markdown("這個儀表板透過 FCO 的 247 個直飛航點數據，呈現義大利與全球的經貿、移民與歷史連結。")

# 2. 讀取資料
@st.cache_data  # 讓資料快取，提升網頁載入速度
def load_data():
    df = pd.read_csv('FCO.csv')
    country_data = df['目的地與國家'].value_counts().reset_index()
    country_data.columns = ['Country', 'Routes']
    return df, country_data

try:
    df, country_data = load_data()
    
    # 3. 頂部數據儀表板 (KPI Metrics)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("總直飛航點數", f"{len(df)} 個")
    with col2:
        st.metric("直飛覆蓋國家數", f"{len(country_data)} 個")
    with col3:
        st.metric("國內線航點數", f"{len(df[df['目的地與國家'] == 'Italy'])} 個")

    st.divider()

    # 4. 佈局：左邊放互動世界地圖，右邊放前20名長條圖
    left_chart, right_chart = st.columns([3, 2])

    with left_chart:
        st.subheader("🗺️ 全球直飛航點密度地圖 (可點擊/縮放)")
        # 使用 Plotly 畫互動地圖
        fig_map = px.choropleth(country_data, 
                                locations="Country", 
                                locationmode="country names",
                                color="Routes", 
                                hover_name="Country",
                                color_continuous_scale=px.colors.sequential.YlOrRd,
                                labels={'Routes': '航點數量'})
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with right_chart:
        st.subheader("📊 直飛航點前 20 名國家")
        # 使用 Matplotlib / Seaborn 畫長條圖
        fig_bar, ax = plt.subplots(figsize=(10, 7))
        sns.barplot(data=country_data.head(20), x='Routes', y='Country', palette='viridis', ax=ax)
        ax.set_xlabel("直飛航線數")
        ax.set_ylabel("國家")
        st.pyplot(fig_bar)

    st.divider()

    # 5. 底部放原始數據查看器
    st.subheader("📂 FCO 原始航點數據清單")
    search_term = st.text_input("🔍 輸入國家名稱進行過濾：")
    if search_term:
        filtered_df = df[df['目的地與國家'].str.contains(search_term, case=False, na=False)]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

except FileNotFoundError:
    st.error("❌ 找不到 'FCO.csv' 檔案！請確保該 CSV 檔案與 app.py 放在同一個資料夾中。")