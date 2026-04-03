import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import io
import math
import warnings
import requests
from PIL import Image
from io import BytesIO
import base64
import folium
from folium import plugins
from streamlit_folium import st_folium
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Analitik Data Sains & Sistem Pengambilan Keputusan Aksesibilitas PSC 119",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk mengambil gambar dari URL dan mengkonversinya ke base64
def get_image_base64(url):
    """Download image from URL and convert to base64"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            img_data = base64.b64encode(response.content).decode()
            content_type = response.headers.get('content-type', 'image/webp')
            return f"data:{content_type};base64,{img_data}"
        else:
            return None
    except Exception as e:
        return None

# URL gambar background header
header_bg_url = "https://static.honestdocs.id/989x500/webp/system/blog_articles/main_hero_images/000/007/431/original/ambulans_dan_mobil_jenazah.jpg"
header_bg_base64 = get_image_base64(header_bg_url)

# URL gambar background sidebar
sidebar_bg_url = "https://ambulancemed.com/wp-content/uploads/2021/08/MAN-Emergency-Ambulance-2.jpeg"
sidebar_bg_base64 = get_image_base64(sidebar_bg_url)

# Custom CSS untuk header dengan background gambar
if header_bg_base64:
    header_css = f"""
    <style>
    .main-header {{
        text-align: center;
        padding: 2rem 1rem;
        background-image: url('{header_bg_base64}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        position: relative;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .main-header h1, .main-header p {{
        position: relative;
        z-index: 2;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        background-color: rgba(0,0,0,0.4);
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 10px;
        backdrop-filter: blur(3px);
    }}
    .main-header h1 {{
        font-size: 2.5rem;
        margin: 0;
        font-weight: bold;
    }}
    .main-header p {{
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.95;
    }}
    </style>
    """
else:
    header_css = """
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #2c3e50 0%, #1a1a2e 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: bold;
    }
    .main-header p {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.95;
    }
    </style>
    """

st.markdown(header_css, unsafe_allow_html=True)

# Custom CSS untuk sidebar dengan background gambar
if sidebar_bg_base64:
    sidebar_css = f"""
    <style>
    [data-testid="stSidebar"] {{
        background-image: url('{sidebar_bg_base64}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    [data-testid="stSidebar"]::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
        z-index: 0;
    }}
    [data-testid="stSidebar"] > div {{
        position: relative;
        z-index: 1;
    }}
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stInfo,
    [data-testid="stSidebar"] .stButton,
    [data-testid="stSidebar"] .stImage,
    [data-testid="stSidebar"] .element-container {{
        color: white !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown strong,
    [data-testid="stSidebar"] .stMarkdown a,
    [data-testid="stSidebar"] .stInfo p,
    [data-testid="stSidebar"] .stAlert p,
    [data-testid="stSidebar"] .stAlert a,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    [data-testid="stSidebar"] .stAlert,
    [data-testid="stSidebar"] .stAlert > div,
    [data-testid="stSidebar"] [data-testid="stAlert"] {{
        color: white !important;
        background-color: rgba(0,0,0,0.35) !important;
        border-color: rgba(255,255,255,0.3) !important;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {{
        background-color: rgba(30,30,30,0.8);
        color: white !important;
    }}
    [data-testid="stSidebar"] .developer-card,
    [data-testid="stSidebar"] .developer-name,
    [data-testid="stSidebar"] .developer-title {{
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    [data-testid="stSidebar"] .placeholder-img {{
        background-color: rgba(0,0,0,0.5);
        border-radius: 10px;
    }}
    </style>
    """
else:
    sidebar_css = """
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stAlert,
    [data-testid="stSidebar"] .stAlert > div,
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        color: white !important;
        background-color: rgba(0,0,0,0.35) !important;
        border-color: rgba(255,255,255,0.3) !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {
        background-color: rgba(30,30,30,0.8);
        color: white !important;
    }
    </style>
    """

st.markdown(sidebar_css, unsafe_allow_html=True)

# Title dengan background gambar
st.markdown('<div class="main-header"><h1>🚑 Analitik Data Sains & Sistem Pengambilan Keputusan Aksesibilitas PSC 119</h1><p>Sistem Analisis dan Prediksi Response Time Ambulans</p></div>', unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'model' not in st.session_state:
    st.session_state.model = None
if 'features' not in st.session_state:
    st.session_state.features = None
# ✅ FIX: Tambah session state untuk menyimpan hasil dispatch agar persisten
if 'dispatch_result' not in st.session_state:
    st.session_state.dispatch_result = None

# ==================== SIDEBAR WITH DEVELOPER PHOTOS ====================
st.sidebar.title("📊 Navigasi")
menu = st.sidebar.selectbox(
    "Pilih Modul",
    ["1. Data Cleaning", "2. EDA & Visualisasi", "3. Analisis Korelasi",
     "4. Machine Learning", "5. Evaluasi Model", "6. Prediksi & Dispatch"],
    key="menu_selectbox"
)

# Team Developer Section
st.sidebar.markdown("---")
st.sidebar.markdown("## 👨‍💻 Team Developer")

# Fungsi untuk memuat gambar dari URL dengan error handling
def load_image_from_url(url):
    """Load image from URL with fallback to None if failed"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            return img
        else:
            return None
    except Exception as e:
        return None

# Developer 1: dr. Aurick Yudha Nagara, Sp.EM., KPEC.
st.sidebar.markdown('<div class="developer-card">', unsafe_allow_html=True)

aurick_url = "https://kanal24.co.id/wp-content/uploads/2025/01/20250130_093038-1024x576.jpg"
aurick_img = load_image_from_url(aurick_url)

if aurick_img:
    st.sidebar.image(aurick_img, width=250)
else:
    st.sidebar.markdown("""
    <div class="placeholder-img">
        <span style="font-size: 48px;">🩺</span>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown('<div class="developer-name">dr. Aurick Yudha Nagara, Sp.EM., KPEC.</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="developer-title">Concept &amp; Design</div>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")

# Developer 2: Adipandang Yudono, PhD
st.sidebar.markdown('<div class="developer-card">', unsafe_allow_html=True)

adipandang_url = "https://gravatar.com/avatar/cfb4beb7693d01d2219d9f2440cb6061?s=200"
adipandang_img = load_image_from_url(adipandang_url)

if adipandang_img:
    st.sidebar.image(adipandang_img, width=250)
else:
    st.sidebar.markdown("""
    <div class="placeholder-img">
        <span style="font-size: 48px;">🗺️</span>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown('<div class="developer-name">Adipandang Yudono, PhD</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="developer-title">GIS Engineering, Spatial Data Science, &amp; WebGIS Analytics</div>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")

# Footer di sidebar
st.sidebar.info(
    """
    **Analitik Data Sains & Sistem Pengambilan Keputusan Aksesibilitas PSC 119**

    Sistem analisis dan prediksi response time
    untuk optimalisasi layanan ambulans.

    © 2026 - PSC 119
    """
)

# ==================== FUNCTIONS ====================
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        return df
    return None

def clean_data(df):
    df_clean = df.copy()

    mask_scene = df_clean['Scene Time'].astype(str).str.lower().str.contains('nihil rujuk', na=False)
    df_clean.loc[mask_scene, 'Scene Time'] = 0

    mask_tkp_rs = df_clean['Jarak dari TKP ke RS (km)'].astype(str).str.lower().str.contains('nihil rujuk', na=False)
    df_clean.loc[mask_tkp_rs, 'Jarak dari TKP ke RS (km)'] = 0

    mask_rs_posko = df_clean['Jarak dari RS ke Posko (km)'].astype(str).str.lower().str.contains('nihil rujuk', na=False)
    df_clean.loc[mask_rs_posko, 'Jarak dari RS ke Posko (km)'] = df_clean.loc[mask_rs_posko, 'Jarak tempuh ke TKP (km)']

    mask_meninggal = df_clean['Keterangan'].astype(str).str.lower().str.contains('meninggal dunia', na=False)
    df_clean['Keadaan Pasien'] = 1
    df_clean.loc[mask_meninggal, 'Keadaan Pasien'] = 0

    numeric_cols = ['Scene Time', 'Jarak dari TKP ke RS (km)', 'Jarak dari RS ke Posko (km)']
    for col in numeric_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    return df_clean

def remove_outliers_iqr(data, columns):
    df_final = data.copy()
    initial_shape = df_final.shape[0]

    for col in columns:
        if col in df_final.columns:
            Q1 = df_final[col].quantile(0.25)
            Q3 = df_final[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df_final = df_final[(df_final[col] >= lower_bound) & (df_final[col] <= upper_bound)]

    return df_final, initial_shape

# ==================== MODULE 1: DATA CLEANING ====================
if menu == "1. Data Cleaning":
    st.header("📁 Data Cleaning & Preprocessing")

    uploaded_file = st.file_uploader("Upload file Excel (.xlsx)", type=['xlsx'])

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.session_state.df = df

        st.subheader("📊 Data Preview (Before Cleaning)")
        st.dataframe(df.head(10))

        if st.button("🧹 Run Data Cleaning"):
            with st.spinner("Cleaning data..."):
                df_clean = clean_data(df)
                st.session_state.df = df_clean

                st.success("✅ Data cleaning completed!")

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📊 Data Preview (After Cleaning)")
                    st.dataframe(df_clean.head(10))

                with col2:
                    st.subheader("📈 Data Info")
                    buffer = io.BytesIO()
                    df_clean.to_excel(buffer, index=False)
                    st.download_button(
                        label="📥 Download Cleaned Data",
                        data=buffer,
                        file_name="data_cleaned.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    st.metric("Total Rows", len(df_clean))
                    st.metric("Total Columns", len(df_clean.columns))

# ==================== MODULE 2: EDA & VISUALIZATION ====================
elif menu == "2. EDA & Visualisasi":
    st.header("📊 Exploratory Data Analysis & Visualisasi")

    if st.session_state.df is not None:
        df = st.session_state.df

        st.subheader("📈 Scatter Plot: Response Time vs Jarak ke TKP")

        col1, col2 = st.columns([2, 1])

        with col1:
            var_x = st.selectbox("Pilih Variabel X (Jarak)",
                                ['Jarak tempuh ke TKP (km)', 'Jarak dari TKP ke RS (km)', 'Jarak dari RS ke Posko (km)'],
                                key='scatter_x')
            var_y = st.selectbox("Pilih Variabel Y (Waktu)",
                                ['Response time', 'Travel time', 'Dispatch time', 'Chute time', 'Scene Time'],
                                key='scatter_y')

        with col2:
            show_regression = st.checkbox("Tampilkan Garis Regresi", value=True)
            color_by = st.selectbox("Warnai berdasarkan",
                                   ['None', 'Trauma / Non-Trauma', 'Keadaan Pasien', 'Jenis Kelamin'],
                                   key='color_by')

        if var_x and var_y:
            fig, ax = plt.subplots(figsize=(10, 6))

            df_plot = df.dropna(subset=[var_x, var_y])
            df_plot[var_x] = pd.to_numeric(df_plot[var_x], errors='coerce')
            df_plot[var_y] = pd.to_numeric(df_plot[var_y], errors='coerce')
            df_plot = df_plot.dropna(subset=[var_x, var_y])

            if color_by != 'None' and color_by in df_plot.columns:
                hue_data = df_plot[color_by].astype(str)
                sns.scatterplot(data=df_plot, x=var_x, y=var_y, hue=hue_data,
                              alpha=0.6, s=60, ax=ax)
            else:
                sns.scatterplot(data=df_plot, x=var_x, y=var_y, alpha=0.6, s=60, ax=ax)

            if show_regression:
                sns.regplot(data=df_plot, x=var_x, y=var_y, scatter=False,
                           color='red', ax=ax, line_kws={'linewidth': 2})

            ax.set_xlabel(var_x)
            ax.set_ylabel(f'{var_y} (menit)' if 'time' in var_y.lower() else var_y)
            ax.set_title(f'Scatter Plot: {var_y} vs {var_x}')
            ax.grid(True, alpha=0.3)

            st.pyplot(fig)

        st.subheader("📦 Deteksi Outliers")

        col1, col2 = st.columns(2)

        with col1:
            time_cols = ['Response time', 'Travel time', 'Dispatch time', 'Chute time', 'Scene Time']
            selected_col = st.selectbox("Pilih kolom untuk deteksi outlier", time_cols, key='outlier_col')

            if selected_col in df.columns:
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.boxplot(x=df[selected_col].dropna(), color='salmon', ax=ax)
                ax.set_title(f'Boxplot: {selected_col}')
                ax.set_xlabel(f'{selected_col} (menit)')
                st.pyplot(fig)

        with col2:
            if selected_col in df.columns:
                Q1 = df[selected_col].quantile(0.25)
                Q3 = df[selected_col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = df[(df[selected_col] < lower_bound) | (df[selected_col] > upper_bound)]

                st.metric("Jumlah Outliers", len(outliers))
                st.metric("Batas Bawah", f"{lower_bound:.2f}")
                st.metric("Batas Atas", f"{upper_bound:.2f}")

        if st.button("🧹 Hapus Outliers"):
            cols_to_clean = ['Response time', 'Travel time', 'Dispatch time', 'Jarak tempuh ke TKP (km)']
            df_cleaned, initial_rows = remove_outliers_iqr(df, cols_to_clean)
            st.session_state.df = df_cleaned

            st.success(f"✅ Data cleaned! Removed {initial_rows - len(df_cleaned)} rows")
            st.info(f"Total rows after cleaning: {len(df_cleaned)}")

# ==================== MODULE 3: CORRELATION ANALYSIS ====================
elif menu == "3. Analisis Korelasi":
    st.header("📈 Analisis Korelasi")

    if st.session_state.df is not None:
        df = st.session_state.df

        df_numeric = df.select_dtypes(include=['number'])

        if 'No' in df_numeric.columns:
            df_numeric = df_numeric.drop(columns=['No'])

        st.subheader("🔢 Matriks Korelasi (Heatmap)")

        fig, ax = plt.subplots(figsize=(14, 10))
        corr_matrix = df_numeric.corr()
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f',
                   linewidths=0.5, mask=mask, ax=ax,
                   annot_kws={"size": 8})
        ax.set_title('Matriks Korelasi Antar Variabel Numerik', fontsize=14, fontweight='bold')

        st.pyplot(fig)

        st.subheader("🎯 Korelasi dengan Response Time")

        target = 'Response time'
        if target in df_numeric.columns:
            correlations = df_numeric.corrwith(df_numeric[target]).sort_values(ascending=False)
            corr_df = pd.DataFrame({
                'Variable': correlations.index,
                'Correlation': correlations.values
            }).iloc[1:]

            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['green' if x > 0 else 'red' for x in corr_df['Correlation'].values]
            ax.barh(corr_df['Variable'], corr_df['Correlation'], color=colors)
            ax.set_xlabel('Korelasi Spearman')
            ax.set_title(f'Korelasi Variabel dengan {target}')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
            st.pyplot(fig)

            st.subheader("📊 Analisis Korelasi Spesifik")

            col1, col2 = st.columns(2)
            with col1:
                var1 = st.selectbox("Pilih Variabel 1", df_numeric.columns, key='corr_var1')
            with col2:
                var2 = st.selectbox("Pilih Variabel 2", df_numeric.columns, key='corr_var2')

            if var1 and var2 and var1 != var2:
                data_clean = df_numeric[[var1, var2]].dropna()
                rho, p_val = spearmanr(data_clean[var1], data_clean[var2])

                st.info(f"""
                **Hasil Analisis Spearman Correlation:**
                - Rho (Koefisien Korelasi): **{rho:.3f}**
                - P-value: **{p_val:.5f}**
                - Interpretasi: {'Signifikan' if p_val < 0.05 else 'Tidak Signifikan'}
                """)

# ==================== MODULE 4: MACHINE LEARNING ====================
elif menu == "4. Machine Learning":
    st.header("🤖 Machine Learning - Random Forest Regressor")

    if st.session_state.df is not None:
        df = st.session_state.df

        st.subheader("⚙️ Konfigurasi Model")

        default_features = ['Jarak tempuh ke TKP (km)', 'Usia (tahun)', 'Trauma / Non-Trauma',
                           'Jenis Kelamin', 'Kategori Waktu', 'Travel time', 'Dispatch time', 'Chute time']

        available_features = [col for col in default_features if col in df.columns]

        selected_features = st.multiselect(
            "Pilih fitur untuk training model",
            available_features,
            default=available_features[:5] if len(available_features) > 5 else available_features,
            key='feature_select'
        )

        target = st.selectbox("Pilih target variable",
                             ['Response time', 'Scene Time', 'Travel time'],
                             index=0,
                             key='target_select')

        if target not in df.columns:
            st.error(f"Target column '{target}' not found!")
        elif len(selected_features) == 0:
            st.warning("Please select at least one feature!")
        else:
            df_ml = df[selected_features + [target]].dropna()

            if len(df_ml) == 0:
                st.error("No valid data after removing missing values!")
            else:
                X = df_ml[selected_features]
                y = df_ml[target]

                test_size = st.slider("Test set size (%)", 10, 40, 20, key='test_size') / 100
                n_estimators = st.slider("Number of trees", 50, 300, 100, 50, key='n_estimators')

                if st.button("🚀 Train Model", key='train_btn'):
                    with st.spinner("Training model..."):
                        X_train, X_test, y_train, y_test = train_test_split(
                            X, y, test_size=test_size, random_state=42
                        )

                        model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
                        model.fit(X_train, y_train)

                        st.session_state.model = model
                        st.session_state.features = selected_features

                        y_pred = model.predict(X_test)

                        mae = mean_absolute_error(y_test, y_pred)
                        r2 = r2_score(y_test, y_pred)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("R² Score", f"{r2:.3f}")
                        with col2:
                            st.metric("MAE", f"{mae:.2f} menit")
                        with col3:
                            st.metric("Sample Size", len(df_ml))

                        st.subheader("📊 Feature Importance")

                        importance_df = pd.DataFrame({
                            'Feature': selected_features,
                            'Importance (%)': model.feature_importances_ * 100
                        }).sort_values('Importance (%)', ascending=True)

                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.barh(importance_df['Feature'], importance_df['Importance (%)'], color='teal')
                        ax.set_xlabel('Importance (%)')
                        ax.set_title('Feature Importance - Random Forest')

                        for i, v in enumerate(importance_df['Importance (%)']):
                            ax.text(v + 0.5, i, f'{v:.1f}%', va='center')

                        st.pyplot(fig)

                        model_data = {'model': model, 'features': selected_features}
                        joblib.dump(model_data, 'model_prediksi_respon_time.pkl')

                        with open('model_prediksi_respon_time.pkl', 'rb') as f:
                            st.download_button(
                                label="💾 Download Model",
                                data=f,
                                file_name="model_prediksi_respon_time.pkl",
                                mime="application/octet-stream",
                                key='download_btn'
                            )

# ==================== MODULE 5: MODEL EVALUATION ====================
elif menu == "5. Evaluasi Model":
    st.header("📈 Evaluasi Model Prediksi")

    if st.session_state.df is not None and st.session_state.model is not None:
        df = st.session_state.df
        model = st.session_state.model
        features = st.session_state.features

        target = 'Response time'

        if target in df.columns and all(f in df.columns for f in features):
            df_eval = df[features + [target]].dropna()
            X = df_eval[features]
            y = df_eval[target]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            y_pred = model.predict(X_test)

            st.subheader("📊 Model Performance Metrics")

            col1, col2, col3 = st.columns(3)
            with col1:
                r2 = r2_score(y_test, y_pred)
                st.metric("R² Score", f"{r2:.3f}",
                         delta="Good" if r2 > 0.7 else "Fair" if r2 > 0.5 else "Poor")
            with col2:
                mae = mean_absolute_error(y_test, y_pred)
                st.metric("Mean Absolute Error", f"{mae:.2f} menit")
            with col3:
                mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
                st.metric("MAPE", f"{mape:.1f}%")

            st.subheader("📈 Actual vs Predicted Values")

            fig, axes = plt.subplots(1, 2, figsize=(14, 6))

            axes[0].scatter(y_test, y_pred, alpha=0.5, color='blue')
            axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()],
                        'r--', lw=2, label='Perfect Prediction')
            axes[0].set_xlabel('Actual Response Time (minutes)')
            axes[0].set_ylabel('Predicted Response Time (minutes)')
            axes[0].set_title('Actual vs Predicted')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)

            residuals = y_test - y_pred
            axes[1].scatter(y_pred, residuals, alpha=0.5, color='green')
            axes[1].axhline(y=0, color='r', linestyle='--', linewidth=2)
            axes[1].set_xlabel('Predicted Values')
            axes[1].set_ylabel('Residuals')
            axes[1].set_title('Residual Plot')
            axes[1].grid(True, alpha=0.3)

            st.pyplot(fig)

            st.subheader("📊 Distribution of Errors")

            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(residuals, kde=True, ax=ax, color='purple', bins=30)
            ax.set_xlabel('Prediction Error (minutes)')
            ax.set_ylabel('Frequency')
            ax.set_title('Error Distribution')
            ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
            st.pyplot(fig)

        else:
            st.warning("Please train a model first in the Machine Learning module!")
    else:
        st.info("Please load data and train a model in the Machine Learning module first!")

# ==================== MODULE 6: PREDICTION & DISPATCH ====================
elif menu == "6. Prediksi & Dispatch":
    st.header("🚑 Prediksi Response Time & Sistem Dispatch")

    tab1, tab2 = st.tabs(["🎯 Prediksi Response Time", "🚨 Sistem Rekomendasi Dispatch"])

    with tab1:
        st.subheader("Prediksi Response Time Berdasarkan Parameter")

        if st.session_state.model is not None:
            model = st.session_state.model
            features = st.session_state.features

            st.info(f"Model menggunakan fitur: {', '.join(features)}")

            col1, col2 = st.columns(2)

            input_values = {}

            with col1:
                if 'Jarak tempuh ke TKP (km)' in features:
                    input_values['Jarak tempuh ke TKP (km)'] = st.number_input("Jarak ke TKP (km)",
                                                                               min_value=0.0, max_value=50.0, value=5.0, step=0.5,
                                                                               key='jarak_tkp')
                if 'Usia (tahun)' in features:
                    input_values['Usia (tahun)'] = st.number_input("Usia Pasien (tahun)",
                                                                  min_value=0, max_value=120, value=40,
                                                                  key='usia_pasien')
                if 'Travel time' in features:
                    input_values['Travel time'] = st.number_input("Travel Time (menit)",
                                                                 min_value=0.0, max_value=60.0, value=10.0, step=0.5,
                                                                 key='travel_time')

            with col2:
                if 'Dispatch time' in features:
                    input_values['Dispatch time'] = st.number_input("Dispatch Time (menit)",
                                                                   min_value=0.0, max_value=30.0, value=2.0, step=0.5,
                                                                   key='dispatch_time')
                if 'Chute time' in features:
                    input_values['Chute time'] = st.number_input("Chute Time (menit)",
                                                                min_value=0.0, max_value=30.0, value=1.0, step=0.5,
                                                                key='chute_time')
                if 'Trauma / Non-Trauma' in features:
                    trauma = st.selectbox("Jenis Kasus", ["Non-Trauma", "Trauma"], key='trauma_select_tab1')
                    input_values['Trauma / Non-Trauma'] = 1 if trauma == "Trauma" else 0
                if 'Jenis Kelamin' in features:
                    jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], key='jenis_kelamin_pred')
                    input_values['Jenis Kelamin'] = 1 if jk == "Laki-laki" else 0
                if 'Kategori Waktu' in features:
                    kat_waktu = st.selectbox("Kategori Waktu", ["Pagi", "Siang", "Sore", "Malam"], key='kategori_waktu_pred')
                    input_values['Kategori Waktu'] = {"Pagi": 0, "Siang": 1, "Sore": 2, "Malam": 3}[kat_waktu]

            # Isi nilai default untuk fitur yang tidak ada input UI-nya
            default_values = {
                'Jarak tempuh ke TKP (km)': 5.0,
                'Usia (tahun)': 40,
                'Travel time': 10.0,
                'Dispatch time': 2.0,
                'Chute time': 1.0,
                'Trauma / Non-Trauma': 0,
                'Jenis Kelamin': 0,
                'Kategori Waktu': 1,
            }
            for feat in features:
                if feat not in input_values:
                    input_values[feat] = default_values.get(feat, 0)

            input_df = pd.DataFrame([input_values])

            if st.button("🔮 Prediksi Response Time", type="primary", key='predict_btn'):
                try:
                    prediction = model.predict(input_df[features])[0]

                    st.success(f"### ⏱️ Prediksi Response Time: **{prediction:.1f} menit**")

                    if prediction <= 15:
                        st.info("✅ **Target Internasional Tercapai!** (< 15 menit)")
                    elif prediction <= 25:
                        st.warning("⚠️ **Target Nasional Tercapai** (15-25 menit)")
                    else:
                        st.error("❌ **Di Luar Target** (> 25 menit)")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat prediksi: {e}")
        else:
            st.warning("Please train a model first in the Machine Learning module!")

    with tab2:
        st.subheader("🗺️ Sistem Rekomendasi Dispatch Cerdas")
        st.markdown("Klik pada peta untuk menentukan lokasi TKP, lalu sistem akan menghitung rute tercepat dari posko ambulans terdekat.")

        # ---- Session state untuk koordinat TKP ----
        if 'tkp_lat' not in st.session_state:
            st.session_state.tkp_lat = -7.9797
        if 'tkp_lon' not in st.session_state:
            st.session_state.tkp_lon = 112.6304

        # ---- Konfigurasi parameter ----
        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        with col_cfg1:
            basemap = st.selectbox(
                "🗺️ Pilih Basemap",
                ["OpenStreetMap", "Citra Satelit", "Dark Theme"],
                key='basemap_select'
            )
        with col_cfg2:
            usia = st.number_input("👤 Usia Pasien", min_value=0, max_value=120, value=40, key='usia_dispatch')
        with col_cfg3:
            kasus = st.selectbox("🏥 Jenis Kasus", ["Non-Trauma", "Trauma"], key='kasus_select_tab2')

        # ---- Koordinat input manual ----
        col_lat, col_lon = st.columns(2)
        with col_lat:
            tkp_lat = st.number_input("📍 Latitude TKP", value=st.session_state.tkp_lat,
                                      format="%.6f", step=0.0001, key='tkp_lat_input')
        with col_lon:
            tkp_lon = st.number_input("📍 Longitude TKP", value=st.session_state.tkp_lon,
                                      format="%.6f", step=0.0001, key='tkp_lon_input')

        st.session_state.tkp_lat = tkp_lat
        st.session_state.tkp_lon = tkp_lon

        # ---- Definisi Posko ----
        POSKO = {
            "PMI Kota Malang": {
                "lat": -7.9731, "lon": 112.6186,
                "icon": "🏥", "color": "red",
                "alamat": "Jl. Brigjen Slamet Riadi No.4, Malang"
            },
            "RSUD dr. Saiful Anwar": {
                "lat": -7.9630, "lon": 112.6347,
                "icon": "🏨", "color": "blue",
                "alamat": "Jl. Jaksa Agung Suprapto No.2, Malang"
            },
            "FK Universitas Brawijaya": {
                "lat": -7.9523, "lon": 112.6137,
                "icon": "🎓", "color": "green",
                "alamat": "Jl. Veteran, Malang"
            },
        }

        # ---- Basemap tiles ----
        BASEMAP_TILES = {
            "OpenStreetMap": {
                "tiles": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "attr": "© OpenStreetMap contributors",
                "name": "OpenStreetMap"
            },
            "Citra Satelit": {
                "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                "attr": "© Esri World Imagery",
                "name": "Satelit"
            },
            "Dark Theme": {
                "tiles": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                "attr": "© CartoDB Dark Matter",
                "name": "Dark"
            }
        }

        selected_tile = BASEMAP_TILES[basemap]

        # ---- Hitung jarak Haversine ----
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return R * 2 * math.asin(math.sqrt(a))

        # ---- Fetch rute dari OSRM (gratis, open source) ----
        def get_osrm_route(lat1, lon1, lat2, lon2):
            try:
                url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("routes"):
                        route = data["routes"][0]
                        coords = route["geometry"]["coordinates"]
                        distance_km = route["distance"] / 1000
                        duration_min = route["duration"] / 60
                        # OSRM returns [lon, lat], flip to [lat, lon] for Folium
                        latlon_coords = [[c[1], c[0]] for c in coords]
                        return latlon_coords, distance_km, duration_min
            except Exception:
                pass
            return None, None, None

        # ---- Helper fungsi status ----
        def get_status(waktu):
            if waktu <= 15:
                return "🟢 Target Internasional (Aman)"
            elif waktu <= 25:
                return "🟡 Target Nasional (Waspada)"
            else:
                return "🔴 Terlambat (>25 menit)"

        # ---- Build Folium map (peta input TKP) ----
        m = folium.Map(
            location=[-7.9797, 112.6304],
            zoom_start=13,
            tiles=selected_tile["tiles"],
            attr=selected_tile["attr"]
        )

        # Marker TKP
        folium.Marker(
            location=[tkp_lat, tkp_lon],
            popup=folium.Popup(f"<b>📍 TKP</b><br>Lat: {tkp_lat:.5f}<br>Lon: {tkp_lon:.5f}", max_width=200),
            tooltip="📍 Lokasi TKP (klik untuk pindah)",
            icon=folium.Icon(color="orange", icon="exclamation-sign", prefix="glyphicon")
        ).add_to(m)

        # Marker tiap Posko
        for nama, info in POSKO.items():
            jarak_lurus = haversine(tkp_lat, tkp_lon, info["lat"], info["lon"])
            folium.Marker(
                location=[info["lat"], info["lon"]],
                popup=folium.Popup(
                    f"<b>{info['icon']} {nama}</b><br>{info['alamat']}<br>Jarak lurus: {jarak_lurus:.2f} km",
                    max_width=250
                ),
                tooltip=f"{info['icon']} {nama}",
                icon=folium.Icon(color=info["color"], icon="plus-sign", prefix="glyphicon")
            ).add_to(m)

        m.add_child(folium.LatLngPopup())

        st.info("💡 **Petunjuk:** Klik pada peta untuk mendapatkan koordinat TKP, lalu salin ke kolom Latitude/Longitude di atas.")
        map_data = st_folium(m, width="100%", height=450, key="dispatch_map")

        # Update koordinat jika peta diklik
        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            st.session_state.tkp_lat = round(clicked["lat"], 6)
            st.session_state.tkp_lon = round(clicked["lng"], 6)
            st.success(f"✅ Koordinat TKP diperbarui: Lat {st.session_state.tkp_lat}, Lon {st.session_state.tkp_lon}")
            st.rerun()

        st.markdown("---")

        # ✅ FIX: Reset hasil dispatch jika koordinat TKP berubah
        if st.session_state.dispatch_result is not None:
            saved = st.session_state.dispatch_result
            if (saved["tkp_lat"] != tkp_lat or saved["tkp_lon"] != tkp_lon or
                    saved["kasus"] != kasus):
                st.session_state.dispatch_result = None

        # ---- Tombol Cari Unit & Tampilkan Rute ----
        if st.button("🏆 Cari Unit Tercepat & Tampilkan Rute", type="primary", key='cari_unit_btn'):

            pengurang_trauma = 10.0 if kasus == "Trauma" else 0.0

            with st.spinner("🔍 Mengambil rute jalan dari OSRM..."):
                hasil_rute = []
                for nama, info in POSKO.items():
                    coords, dist_km, dur_min = get_osrm_route(
                        info["lat"], info["lon"], tkp_lat, tkp_lon
                    )
                    if dist_km is None:
                        dist_km = haversine(tkp_lat, tkp_lon, info["lat"], info["lon"]) * 1.3
                        dur_min = None
                    est_waktu = 15.3 + (0.93 * dist_km) + (0.10 * usia) - pengurang_trauma
                    hasil_rute.append({
                        "nama": nama,
                        "info": info,
                        "coords": coords,
                        "dist_km": dist_km,
                        "dur_min": dur_min,
                        "est_waktu": est_waktu,
                    })

                hasil_rute.sort(key=lambda x: x["est_waktu"])

                # ✅ FIX: Simpan seluruh hasil ke session_state agar persisten antar re-run
                st.session_state.dispatch_result = {
                    "hasil_rute": hasil_rute,
                    "tkp_lat": tkp_lat,
                    "tkp_lon": tkp_lon,
                    "kasus": kasus,
                    "selected_tile": selected_tile,
                }

        # ✅ FIX: Render peta hasil & rekomendasi dari session_state
        # Blok ini selalu dieksekusi setiap re-run sehingga peta tidak hilang
        if st.session_state.dispatch_result is not None:
            res = st.session_state.dispatch_result
            hasil_rute = res["hasil_rute"]
            _tkp_lat = res["tkp_lat"]
            _tkp_lon = res["tkp_lon"]
            _kasus = res["kasus"]
            _tile = res["selected_tile"]
            tercepat = hasil_rute[0]

            ROUTE_COLORS = ["#FF4136", "#0074D9", "#2ECC40", "#FF851B"]

            m2 = folium.Map(
                location=[_tkp_lat, _tkp_lon],
                zoom_start=13,
                tiles=_tile["tiles"],
                attr=_tile["attr"]
            )

            # Marker TKP
            folium.Marker(
                location=[_tkp_lat, _tkp_lon],
                popup=folium.Popup(f"<b>📍 Lokasi TKP</b><br>Lat: {_tkp_lat:.5f}<br>Lon: {_tkp_lon:.5f}", max_width=200),
                tooltip="📍 TKP",
                icon=folium.Icon(color="orange", icon="exclamation-sign", prefix="glyphicon")
            ).add_to(m2)

            for i, hasil in enumerate(hasil_rute):
                info = hasil["info"]
                color_hex = ROUTE_COLORS[i % len(ROUTE_COLORS)]
                label = "★ TERCEPAT" if i == 0 else f"#{i+1}"
                status = get_status(hasil["est_waktu"])

                popup_html = f"""
                <b>{info['icon']} {hasil['nama']}</b><br>
                {info['alamat']}<br><hr>
                <b>Jarak Jalan:</b> {hasil['dist_km']:.2f} km<br>
                <b>Est. Response Time:</b> {hasil['est_waktu']:.1f} menit<br>
                <b>Status:</b> {status}<br>
                <b>{label}</b>
                """
                folium.Marker(
                    location=[info["lat"], info["lon"]],
                    popup=folium.Popup(popup_html, max_width=280),
                    tooltip=f"{info['icon']} {hasil['nama']} — {hasil['est_waktu']:.1f} mnt ({label})",
                    icon=folium.Icon(color=info["color"], icon="plus-sign", prefix="glyphicon")
                ).add_to(m2)

                if hasil["coords"]:
                    weight = 6 if i == 0 else 3
                    opacity = 1.0 if i == 0 else 0.5
                    dash = None if i == 0 else "8 6"
                    line = folium.PolyLine(
                        locations=hasil["coords"],
                        color=color_hex,
                        weight=weight,
                        opacity=opacity,
                        tooltip=f"{hasil['nama']}: {hasil['dist_km']:.2f} km | {hasil['est_waktu']:.1f} mnt",
                        dash_array=dash
                    )
                    line.add_to(m2)

                    if len(hasil["coords"]) > 2:
                        mid = hasil["coords"][len(hasil["coords"])//2]
                        folium.Marker(
                            location=mid,
                            icon=folium.DivIcon(
                                html=f'<div style="background:{color_hex};color:white;padding:2px 6px;border-radius:8px;font-size:11px;font-weight:bold;white-space:nowrap;">{label} {hasil["est_waktu"]:.1f} mnt</div>',
                                icon_size=(120, 24),
                                icon_anchor=(60, 12)
                            )
                        ).add_to(m2)
                else:
                    # Fallback garis lurus jika OSRM gagal
                    folium.PolyLine(
                        locations=[[info["lat"], info["lon"]], [_tkp_lat, _tkp_lon]],
                        color=color_hex,
                        weight=3,
                        opacity=0.5,
                        dash_array="10 5",
                        tooltip=f"{hasil['nama']} (estimasi lurus)"
                    ).add_to(m2)

            # Fit bounds ke semua titik
            all_points = [[_tkp_lat, _tkp_lon]] + [[h["info"]["lat"], h["info"]["lon"]] for h in hasil_rute]
            m2.fit_bounds(all_points)

            st.markdown("### 🗺️ Peta Network Analysis Origin-Destination")
            st_folium(m2, width="100%", height=500, key="route_map")

            # ---- Hasil Rekomendasi ----
            st.markdown("---")
            st.markdown(f"""
            ### 🎯 REKOMENDASI UTAMA

            ## {tercepat['info']['icon']} {tercepat['nama']}
            📍 {tercepat['info']['alamat']}

            | Parameter | Nilai |
            |-----------|-------|
            | ⏱️ Est. Response Time | **{tercepat['est_waktu']:.1f} menit** |
            | 🛣️ Jarak Jalan | **{tercepat['dist_km']:.2f} km** |
            | 📍 Koordinat TKP | **{_tkp_lat:.5f}, {_tkp_lon:.5f}** |
            | 🏥 Jenis Kasus | **{_kasus}** |

            **Status:** {get_status(tercepat['est_waktu'])}
            """)

            if tercepat['est_waktu'] > 15:
                st.warning("⚠️ **PERINGATAN:** Unit di luar jangkauan ideal. Segera hubungi faskes terdekat!")
            else:
                st.success("✅ Unit dalam jangkauan ideal. Segera lakukan dispatch!")

            st.markdown("---")
            st.markdown("### 📊 Perbandingan Semua Posko")

            cols_r = st.columns(len(hasil_rute))
            for i, h in enumerate(hasil_rute):
                with cols_r[i]:
                    label = "🥇 Tercepat" if i == 0 else f"#{i+1}"
                    st.metric(
                        label=f"{h['info']['icon']} {h['nama']}",
                        value=f"{h['est_waktu']:.1f} mnt",
                        delta=f"{h['dist_km']:.2f} km jalan | {label}"
                    )

# ==================== APP FOOTER ====================
st.markdown("---")
st.markdown("""
<style>
.app-footer {
    background-image: url('https://cdn-assets-eu.frontify.com/s3/frontify-enterprise-files-eu/eyJvYXV0aCI6eyJjbGllbnRfaWQiOiJmcm9udGlmeS1maW5kZXIifSwicGF0aCI6ImloaC1oZWFsdGhjYXJlLWJlcmhhZFwvYWNjb3VudHNcL2MzXC80MDAwNjI0XC9wcm9qZWN0c1wvMjA5XC9hc3NldHNcLzEzXC8zODYyN1wvOWMxZTZiNzIyOTExYjNhM2IzYzkwNjI0YjYwNTlkNGItMTY1ODMwMjcwOS5qcGcifQ:ihh-healthcare-berhad:zOZW-7xDeRWRElxFHAOmqabzJivPI5ELSJAwHPd3mJU?format=webp');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    position: relative;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
    color: white;
    overflow: hidden;
}
.app-footer::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(10,10,40,0.82) 0%, rgba(15,30,80,0.78) 50%, rgba(5,15,50,0.85) 100%);
    border-radius: 16px;
    z-index: 0;
}
.app-footer > * {
    position: relative;
    z-index: 1;
}
.app-footer .footer-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 2rem;
    margin-bottom: 1.5rem;
}
.app-footer h3 {
    color: #FFD700;
    font-size: 1.1rem;
    margin-bottom: 0.6rem;
    letter-spacing: 0.5px;
}
.app-footer h4 {
    color: #FFD700;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}
.app-footer p, .app-footer li {
    color: rgba(255,255,255,0.85);
    font-size: 0.82rem;
    line-height: 1.7;
    margin: 0.15rem 0;
}
.app-footer ul {
    padding-left: 1.1rem;
    margin: 0;
}
.app-footer .badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 0.6rem;
}
.app-footer .badge {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    color: white;
}
.app-footer .footer-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.15);
    margin: 1rem 0;
}
.app-footer .footer-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
}
.app-footer .footer-bottom p {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.6);
    margin: 0;
}
.app-footer .credit-name {
    color: #FFD700;
    font-weight: bold;
}
</style>

<div class="app-footer">
    <div class="footer-grid">
        <div>
            <h3>🚑 Analitik Data Sains & Sistem Pengambilan Keputusan Aksesibilitas PSC 119</h3>
            <p>Platform analitik data sains & sistem pengambilan keputusan berbasis <strong>Machine Learning</strong> yang dirancang
            khusus untuk memantau, menganalisis, dan memprediksi <em>response time</em> ambulans
            layanan PSC 119 Kota Malang secara akurat dan real-time.</p>
            <p style="margin-top:0.5rem;">Aplikasi ini mengintegrasikan data rekam medis darurat,
            analisis spasial, dan kecerdasan buatan untuk mendukung pengambilan keputusan klinis
            dan operasional layanan kegawatdaruratan pra-rumah sakit.</p>
            <div class="badge-row">
                <span class="badge">🐍 Python 3.x</span>
                <span class="badge">📡 Streamlit</span>
                <span class="badge">🌍 GIS</span>
                <span class="badge">🧠 Random Forest</span>
                <span class="badge">📊 Scikit-learn</span>
                <span class="badge">📈 Seaborn</span>
                <span class="badge">🔢 Pandas</span>
            </div>
        </div>
        <div>
            <h4>🎯 Fitur Utama</h4>
            <ul>
                <li>📁 Data Cleaning otomatis</li>
                <li>📊 EDA &amp; Visualisasi Interaktif</li>
                <li>🔗 Analisis Korelasi Spearman</li>
                <li>🤖 Prediksi ML Real-time</li>
                <li>📈 Evaluasi Model Komprehensif</li>
                <li>🚨 Sistem Dispatch Cerdas</li>
            </ul>
        </div>
        <div>
            <h4>👨‍💻 Tim Pengembang</h4>
            <p><span class="credit-name">dr. Aurick Yudha Nagara</span><br>
            Sp.EM., KPEC.<br>
            <em>Concept &amp; Design</em></p>
            <br>
            <p><span class="credit-name">Adipandang Yudono, PhD</span><br>
            <em>GIS Engineering, Spatial Data Science, &amp;<br>WebGIS Developer</em></p>
            <br>
            <h4>🏥 Institusi</h4>
            <p>PSC 119<br>Dinas Kesehatan<br>Kota Malang</p>
        </div>
    </div>
    <hr class="footer-divider">
    <div class="footer-bottom">
        <p>© 2026 PSC 119 Kota Malang — Hak Cipta Dilindungi Undang-Undang</p>
        <p>Dikembangkan untuk optimalisasi layanan kegawatdaruratan medis pra-rumah sakit</p>
        <p>⚕️ <em>Setiap detik menyelamatkan nyawa</em></p>
    </div>
</div>
""", unsafe_allow_html=True)