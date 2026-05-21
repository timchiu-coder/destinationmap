import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. 設定網頁標題與配置
st.set_page_config(page_title="全球機場航點地緣政治分析", page_icon="✈️", layout="wide")

st.title("✈️ 全球機場航點與地緣政治視覺化儀表板")
st.markdown("本系統會自動偵測資料夾內的 CSV 檔案。你可以在左側自由切換不同機場，或上傳新機場的數據。")

# 設定支援的欄位名稱（防呆）
CODE_COLS = ['機場代碼', 'airport_code', 'code', 'IATA']
COUNTRY_COLS = ['目的地與國家', 'country', 'Country']

# 2. 自動偵測目前資料夾下所有的 CSV 檔案
csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
airport_options = [f.split('.')[0] for f in csv_files]

# 3. 側邊欄控制區
st.sidebar.header("📂 數據源選擇")

# 模式切換：可以選用現有檔案，或是上傳新檔案
mode = st.sidebar.radio("選擇資料來源：", ["使用資料夾內現有機場", "上傳全新機場 CSV"])

selected_file = None
airport_name = ""

if mode == "使用資料夾內現有機場":
    if airport_options:
        airport_name = st.sidebar.selectbox("請選擇要分析的機場：", airport_options)
        selected_file = f"{airport_name}.csv"
    else:
        st.sidebar.warning("📁 目前資料夾內沒有任何 CSV 檔案，請切換至上傳模式。")
else:
    uploaded_file = st.sidebar.file_uploader("請上傳機場航點 CSV 檔案", type=["csv"])
    if uploaded_file is not None:
        selected_file = uploaded_file
        airport_name = uploaded_file.name.split('.')[0]

# 4. 主要核心分析邏輯
if selected_file is not None:
    try:
        # 讀取資料
        df = pd.read_csv(selected_file)
        
        # 自動偵測欄位
        code_col = next((c for c in df.columns if c in CODE_COLS), None)
        country_col = next((c for c in df.columns if c in COUNTRY_COLS), None)
        
        if not code_col or not country_col:
            st.error("❌ 檔案欄位不匹配！CSV 檔案內必須包含「機場代碼」與「目的地與國家」這兩個欄位。")
        else:
            # 資料清理與統計 (樞紐分析)
            country_data = df[country_col].value_counts().reset_index()
            country_data.columns = ['Country', 'Routes']
            
            st.sidebar.success(f"✅ 成功載入 {airport_name} 的數據！")
            
            # 5. 頂部數據儀表板 (KPI Metrics)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("總直飛航點數", f"{len(df)} 個")
            with col2:
                st.metric("直飛覆蓋國家數", f"{len(country_data)} 個")
            with col3:
                top_country = country_data.iloc[0]['Country'] if len(country_data) > 0 else "無"
                st.metric("最主要連接國家", f"{top_country} ({country_data.iloc[0]['Routes']}航點)")

            st.divider()

            # 6. 佈局：左邊放互動世界地圖，右邊放前20名長條圖
            left_chart, right_chart = st.columns([3, 2])

            with left_chart:
                st.subheader(f"🗺️ {airport_name} 全球直飛航點密度地圖")
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
                fig_bar, ax = plt.subplots(figsize=(10, 7))
                sns.barplot(data=country_data.head(20), x='Routes', y='Country', palette='viridis', ax=ax)
                ax.set_xlabel("直飛航線數")
                ax.set_ylabel("國家")
                st.pyplot(fig_bar)

            st.divider()

            # 7. 底部：原始數據明細
            st.subheader("📂 原始航點數據明細")
            search_term = st.text_input("🔍 輸入國家名稱進行過濾：")
            if search_term:
                filtered_df = df[df[country_col].str.contains(search_term, case=False, na=False)]
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)
                
    except Exception as e:
        st.error(f"❌ 解析檔案時發生錯誤: {e}")
else:
    st.info("💡 請在左側選取現有機場，或上傳新的機場 CSV 檔案以開始分析。")