import streamlit as st
import streamlit.components.v1 as components
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

# =====================================================================
# MUSIC PLAYER — pakai components.v1.html agar HTML+JS benar-benar
# di-render oleh browser, bukan ditampilkan sebagai teks mentah.
# Sidebar controls mengirim perintah via postMessage ke iframe player.
# =====================================================================

MUSIC_URL = "https://raw.githubusercontent.com/AdipandangUB/dss_akses_psc/main/James%20Bond%20Theme.mp4"

# ── 1. Player utama (fixed bottom-right) ─────────────────────────────
PLAYER_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:transparent;overflow:hidden}}
#wrap{{
  position:fixed;bottom:20px;right:20px;z-index:9999;
  background:linear-gradient(135deg,rgba(0,0,0,0.93),rgba(20,20,20,0.9));
  backdrop-filter:blur(14px);border-radius:14px;
  padding:10px 14px 8px;border:1px solid rgba(255,215,0,.55);
  box-shadow:0 4px 28px rgba(0,0,0,.6);width:310px;
  font-family:'Segoe UI',Tahoma,sans-serif;
  transition:border-color .3s,box-shadow .3s;
}}
#wrap:hover{{border-color:rgba(255,215,0,.9);box-shadow:0 6px 32px rgba(255,215,0,.2)}}
#title{{font-size:11px;color:#FFD700;text-align:center;margin-bottom:7px;
  font-weight:bold;letter-spacing:.5px;animation:pulse 2.5s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:.7}}50%{{opacity:1}}}}
#ctrls{{display:flex;align-items:center;gap:8px;margin-bottom:6px}}
#ppbtn{{
  background:rgba(255,215,0,.12);border:1px solid rgba(255,215,0,.45);
  color:#FFD700;border-radius:8px;padding:5px 12px;cursor:pointer;
  font-size:14px;white-space:nowrap;
  transition:background .2s,border-color .2s,transform .1s
}}
#ppbtn:hover{{background:rgba(255,215,0,.28);border-color:#FFD700}}
#ppbtn:active{{transform:scale(.95)}}
#volrow{{display:flex;align-items:center;gap:6px;flex:1}}
.lbl{{color:rgba(255,255,255,.75);font-size:11px;white-space:nowrap}}
#vol{{flex:1;accent-color:#FFD700;cursor:pointer;height:4px}}
#volpct{{color:rgba(255,215,0,.85);font-size:11px;min-width:30px;text-align:right}}
#progwrap{{width:100%;height:3px;background:rgba(255,255,255,.12);
  border-radius:3px;margin-top:4px;overflow:hidden}}
#progbar{{height:100%;width:0%;
  background:linear-gradient(90deg,#FFD700,#FFA500);border-radius:3px}}
#timedisp{{color:rgba(255,215,0,.6);font-size:10px;text-align:right;margin-top:4px}}
audio{{display:none}}
</style>
</head><body>
<div id="wrap">
  <div id="title">🎵 James Bond Theme &mdash; Background Music 🎵</div>
  <audio id="aud" loop preload="auto">
    <source src="{MUSIC_URL}" type="audio/mp4">
  </audio>
  <div id="ctrls">
    <button id="ppbtn" onclick="doToggle()">▶️ Play</button>
    <div id="volrow">
      <span class="lbl">🔊</span>
      <input id="vol" type="range" min="0" max="100" value="70" oninput="doVol(this.value)">
      <span id="volpct">70%</span>
    </div>
  </div>
  <div id="progwrap"><div id="progbar"></div></div>
  <div id="timedisp">0:00 / 0:00</div>
</div>
<script>
(function(){{
  var aud=document.getElementById('aud');
  var btn=document.getElementById('ppbtn');
  var volEl=document.getElementById('vol');
  var pct=document.getElementById('volpct');
  var prog=document.getElementById('progbar');
  var tdisp=document.getElementById('timedisp');

  function fmt(s){{
    if(!isFinite(s))return'0:00';
    var m=Math.floor(s/60),sc=Math.floor(s%60);
    return m+':'+(sc<10?'0':'')+sc;
  }}
  function syncBtn(paused){{btn.textContent=paused?'▶️ Play':'⏸️ Pause';}}

  // Restore volume
  var sv=localStorage.getItem('jbVol');
  if(sv!==null){{aud.volume=Math.min(Math.max(parseInt(sv),0),100)/100;volEl.value=sv;pct.textContent=sv+'%';}}
  else{{aud.volume=0.70;}}

  aud.addEventListener('timeupdate',function(){{
    tdisp.textContent=fmt(aud.currentTime)+' / '+fmt(aud.duration);
    if(aud.duration)prog.style.width=((aud.currentTime/aud.duration)*100).toFixed(1)+'%';
  }});
  aud.addEventListener('play', function(){{syncBtn(false);localStorage.setItem('jbPaused','false');}});
  aud.addEventListener('pause',function(){{syncBtn(true); localStorage.setItem('jbPaused','true'); }});

  // Autoplay
  if(localStorage.getItem('jbPaused')==='true'){{syncBtn(true);}}
  else{{aud.play().catch(function(){{syncBtn(true);}});}}

  window.doToggle=function(){{aud.paused?aud.play().catch(function(){{}}):aud.pause();}};
  window.doVol=function(v){{
    var iv=Math.min(Math.max(parseInt(v),0),100);
    aud.volume=iv/100;volEl.value=iv;pct.textContent=iv+'%';
    localStorage.setItem('jbVol',iv);
  }};

  // Terima perintah dari sidebar iframe via postMessage
  window.addEventListener('message',function(e){{
    if(!e.data)return;
    if(e.data.cmd==='play')  aud.play().catch(function(){{}});
    if(e.data.cmd==='pause') aud.pause();
    if(e.data.cmd==='vol' && e.data.v!==undefined) window.doVol(e.data.v);
  }});
}})();
</script>
</body></html>"""

# ── 2. Sidebar controls — mengirim postMessage ke iframe player ────────
SIDEBAR_CTRL_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:transparent;overflow:hidden;font-family:'Segoe UI',Tahoma,sans-serif}
.info-box{
  background:rgba(0,0,0,0.55);padding:10px;border-radius:10px;
  margin-bottom:10px;text-align:center;border:1px solid #FFD700;
}
.info-box .np{font-size:12px;color:#FFD700;font-weight:bold}
.info-box .sub{font-size:10px;color:rgba(255,255,255,.75)}
.section-title{color:#FFD700;font-size:13px;font-weight:bold;margin-bottom:8px}
.btn-row{display:flex;gap:8px;margin-bottom:10px}
.btn{
  flex:1;background:rgba(255,215,0,0.13);
  border:1px solid rgba(255,215,0,0.5);
  color:#FFD700;border-radius:8px;padding:8px 0;
  cursor:pointer;font-size:14px;font-weight:bold;
  transition:background .2s,border-color .2s,transform .1s;
}
.btn:hover{background:rgba(255,215,0,0.3);border-color:#FFD700}
.btn:active{transform:scale(.96)}
.vol-row{display:flex;align-items:center;gap:8px}
.vlbl{color:rgba(255,255,255,.85);font-size:12px;white-space:nowrap}
#sv{flex:1;accent-color:#FFD700;cursor:pointer;height:5px}
#spct{color:rgba(255,215,0,.85);font-size:11px;min-width:34px;text-align:right}
</style>
</head><body>
<div class="info-box">
  <div class="np">🎵 Now Playing: James Bond Theme</div>
  <div class="sub">🎧 007 Background Music</div>
</div>
<div class="section-title">🎮 Music Controls</div>
<div class="btn-row">
  <button class="btn" onclick="send('play')">▶️ Play</button>
  <button class="btn" onclick="send('pause')">⏸️ Pause</button>
</div>
<div class="vol-row">
  <span class="vlbl">🔊 Volume</span>
  <input id="sv" type="range" min="0" max="100" value="70"
         oninput="sendVol(this.value)">
  <span id="spct">70%</span>
</div>
<script>
// Cari iframe player di parent document
function getPlayerFrame(){
  try{
    var frames=window.parent.document.querySelectorAll('iframe');
    for(var i=0;i<frames.length;i++){
      if(frames[i].contentWindow && frames[i].src && frames[i].src.indexOf('srcdoc')!==-1) continue;
      // coba kirim ke semua iframe, player akan merespons yang relevan
    }
    return frames;
  }catch(e){return [];}
}

function send(cmd){
  // broadcast ke semua iframe di halaman
  try{
    var iframes=window.parent.document.querySelectorAll('iframe');
    for(var i=0;i<iframes.length;i++){
      try{iframes[i].contentWindow.postMessage({cmd:cmd},'*');}catch(e){}
    }
  }catch(e){}
  // juga coba langsung ke parent window
  try{window.parent.postMessage({cmd:cmd},'*');}catch(e){}
}

function sendVol(v){
  var iv=parseInt(v);
  document.getElementById('spct').textContent=iv+'%';
  try{
    var iframes=window.parent.document.querySelectorAll('iframe');
    for(var i=0;i<iframes.length;i++){
      try{iframes[i].contentWindow.postMessage({cmd:'vol',v:iv},'*');}catch(e){}
    }
  }catch(e){}
  try{window.parent.postMessage({cmd:'vol',v:iv},'*');}catch(e){}
  localStorage.setItem('jbVol',iv);
}

// Restore saved volume
(function(){
  var sv=localStorage.getItem('jbVol');
  if(sv!==null){
    document.getElementById('sv').value=sv;
    document.getElementById('spct').textContent=sv+'%';
  }
})();
</script>
</body></html>"""

# Set page config — HARUS sebelum st.set_page_config dipanggil lagi
st.set_page_config(
    page_title="Analitik Data Sains & Decision Support Systems (DSS) Aksesibilitas PSC 119",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Render player utama via components.html (bukan st.markdown) ────────
components.html(PLAYER_HTML, height=0, scrolling=False)

# Fungsi untuk mengambil gambar dari URL dan mengkonversinya ke base64
def get_image_base64(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            img_data = base64.b64encode(response.content).decode()
            content_type = response.headers.get('content-type', 'image/webp')
            return f"data:{content_type};base64,{img_data}"
        return None
    except:
        return None

header_bg_url = "https://static.honestdocs.id/989x500/webp/system/blog_articles/main_hero_images/000/007/431/original/ambulans_dan_mobil_jenazah.jpg"
header_bg_base64 = get_image_base64(header_bg_url)

sidebar_bg_url = "https://ambulancemed.com/wp-content/uploads/2021/08/MAN-Emergency-Ambulance-2.jpeg"
sidebar_bg_base64 = get_image_base64(sidebar_bg_url)

if header_bg_base64:
    header_css = f"""
    <style>
    .main-header {{
        text-align: center; padding: 2rem 1rem;
        background-image: url('{header_bg_base64}');
        background-size: cover; background-position: center;
        color: white; border-radius: 10px; margin-bottom: 2rem;
        position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .main-header h1, .main-header p {{
        position: relative; z-index: 2;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        background-color: rgba(0,0,0,0.4); display: inline-block;
        padding: 0.5rem 1.5rem; border-radius: 10px; backdrop-filter: blur(3px);
    }}
    .main-header h1 {{ font-size: 2.5rem; margin: 0; font-weight: bold; }}
    .main-header p  {{ font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.95; }}
    </style>"""
else:
    header_css = """
    <style>
    .main-header {
        text-align: center; padding: 2rem 1rem;
        background: linear-gradient(135deg, #2c3e50 0%, #1a1a2e 100%);
        color: white; border-radius: 10px; margin-bottom: 2rem;
    }
    .main-header h1 { font-size: 2.5rem; margin: 0; font-weight: bold; }
    .main-header p  { font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.95; }
    </style>"""

st.markdown(header_css, unsafe_allow_html=True)

if sidebar_bg_base64:
    sidebar_css = f"""
    <style>
    [data-testid="stSidebar"] {{
        background-image: url('{sidebar_bg_base64}');
        background-size: cover; background-position: center;
    }}
    [data-testid="stSidebar"]::before {{
        content:''; position:absolute; top:0; left:0; right:0; bottom:0;
        background: linear-gradient(135deg,rgba(255,255,255,0.15) 0%,rgba(255,255,255,0.05) 100%);
        z-index:0;
    }}
    [data-testid="stSidebar"] > div {{ position:relative; z-index:1; }}
    [data-testid="stSidebar"] * {{ color:white !important; }}
    [data-testid="stSidebar"] .stAlert,
    [data-testid="stSidebar"] .stAlert > div {{
        color:white !important; background-color:rgba(0,0,0,0.35) !important;
        border-color:rgba(255,255,255,0.3) !important;
    }}
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {{
        background-color:rgba(30,30,30,0.8); color:white !important;
    }}
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {{
        color:white !important; text-shadow:1px 1px 2px rgba(0,0,0,0.5);
    }}
    </style>"""
else:
    sidebar_css = """
    <style>
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%); }
    [data-testid="stSidebar"] * { color: white !important; }
    </style>"""

st.markdown(sidebar_css, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🚑 Analitik Data Sains & Decision Support Systems (DSS) Aksesibilitas PSC 119</h1><p>Sistem Analisis dan Prediksi Response Time Ambulans</p></div>', unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:            st.session_state.df = None
if 'model' not in st.session_state:         st.session_state.model = None
if 'features' not in st.session_state:      st.session_state.features = None
if 'dispatch_result' not in st.session_state: st.session_state.dispatch_result = None

# ── SIDEBAR ────────────────────────────────────────────────────────────
st.sidebar.title("📊 Navigasi")
menu = st.sidebar.selectbox(
    "Pilih Modul",
    ["1. Data Cleaning", "2. EDA & Visualisasi", "3. Analisis Korelasi",
     "4. Machine Learning", "5. Evaluasi Model", "6. Prediksi & Dispatch"],
    key="menu_selectbox"
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 👨‍💻 Team Developer")

def load_image_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        return None
    except:
        return None

# Developer 1
aurick_img = load_image_from_url("https://kanal24.co.id/wp-content/uploads/2025/01/20250130_093038-1024x576.jpg")
if aurick_img:
    st.sidebar.image(aurick_img, width=250)
else:
    st.sidebar.markdown('<div style="font-size:48px;text-align:center">🩺</div>', unsafe_allow_html=True)
st.sidebar.markdown("**dr. Aurick Yudha Nagara, Sp.EM., KPEC.**")
st.sidebar.markdown("*Concept & Design*")

st.sidebar.markdown("---")

# Developer 2
adipandang_img = load_image_from_url("https://gravatar.com/avatar/cfb4beb7693d01d2219d9f2440cb6061?s=200")
if adipandang_img:
    st.sidebar.image(adipandang_img, width=250)
else:
    st.sidebar.markdown('<div style="font-size:48px;text-align:center">🗺️</div>', unsafe_allow_html=True)
st.sidebar.markdown("**Adipandang Yudono, PhD**")
st.sidebar.markdown("*GIS Engineering, Spatial Data Science, & WebGIS Analytics*")

st.sidebar.markdown("---")

# ── Sidebar Music Controls — render via components.html ───────────────
# Ini adalah PERBAIKAN UTAMA: gunakan components.html, BUKAN st.sidebar.markdown
# agar HTML+JS di-render nyata oleh browser, tidak ditampilkan sebagai teks.
with st.sidebar:
    components.html(SIDEBAR_CTRL_HTML, height=160, scrolling=False)

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
        return pd.read_excel(uploaded_file)
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
    for col in ['Scene Time', 'Jarak dari TKP ke RS (km)', 'Jarak dari RS ke Posko (km)']:
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
            df_final = df_final[(df_final[col] >= Q1 - 1.5*IQR) & (df_final[col] <= Q3 + 1.5*IQR)]
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
                    st.download_button("📥 Download Cleaned Data", data=buffer,
                        file_name="data_cleaned.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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
                ['Jarak tempuh ke TKP (km)','Jarak dari TKP ke RS (km)','Jarak dari RS ke Posko (km)'], key='scatter_x')
            var_y = st.selectbox("Pilih Variabel Y (Waktu)",
                ['Response time','Travel time','Dispatch time','Chute time','Scene Time'], key='scatter_y')
        with col2:
            show_regression = st.checkbox("Tampilkan Garis Regresi", value=True)
            color_by = st.selectbox("Warnai berdasarkan",
                ['None','Trauma / Non-Trauma','Keadaan Pasien','Jenis Kelamin'], key='color_by')
        if var_x and var_y:
            fig, ax = plt.subplots(figsize=(10, 6))
            df_plot = df.dropna(subset=[var_x, var_y]).copy()
            df_plot[var_x] = pd.to_numeric(df_plot[var_x], errors='coerce')
            df_plot[var_y] = pd.to_numeric(df_plot[var_y], errors='coerce')
            df_plot = df_plot.dropna(subset=[var_x, var_y])
            if color_by != 'None' and color_by in df_plot.columns:
                sns.scatterplot(data=df_plot, x=var_x, y=var_y, hue=df_plot[color_by].astype(str), alpha=0.6, s=60, ax=ax)
            else:
                sns.scatterplot(data=df_plot, x=var_x, y=var_y, alpha=0.6, s=60, ax=ax)
            if show_regression:
                sns.regplot(data=df_plot, x=var_x, y=var_y, scatter=False, color='red', ax=ax, line_kws={'linewidth':2})
            ax.set_xlabel(var_x); ax.set_ylabel(var_y); ax.set_title(f'Scatter Plot: {var_y} vs {var_x}'); ax.grid(True, alpha=0.3)
            st.pyplot(fig)

        st.subheader("📦 Deteksi Outliers")
        col1, col2 = st.columns(2)
        time_cols = ['Response time','Travel time','Dispatch time','Chute time','Scene Time']
        with col1:
            selected_col = st.selectbox("Pilih kolom untuk deteksi outlier", time_cols, key='outlier_col')
            if selected_col in df.columns:
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.boxplot(x=df[selected_col].dropna(), color='salmon', ax=ax)
                ax.set_title(f'Boxplot: {selected_col}'); ax.set_xlabel(f'{selected_col} (menit)')
                st.pyplot(fig)
        with col2:
            if selected_col in df.columns:
                Q1 = df[selected_col].quantile(0.25); Q3 = df[selected_col].quantile(0.75); IQR = Q3-Q1
                outliers = df[(df[selected_col] < Q1-1.5*IQR) | (df[selected_col] > Q3+1.5*IQR)]
                st.metric("Jumlah Outliers", len(outliers))
                st.metric("Batas Bawah", f"{Q1-1.5*IQR:.2f}")
                st.metric("Batas Atas",  f"{Q3+1.5*IQR:.2f}")
        if st.button("🧹 Hapus Outliers"):
            df_cleaned, initial_rows = remove_outliers_iqr(df, ['Response time','Travel time','Dispatch time','Jarak tempuh ke TKP (km)'])
            st.session_state.df = df_cleaned
            st.success(f"✅ Removed {initial_rows - len(df_cleaned)} rows")
            st.info(f"Total rows after cleaning: {len(df_cleaned)}")

# ==================== MODULE 3: CORRELATION ANALYSIS ====================
elif menu == "3. Analisis Korelasi":
    st.header("📈 Analisis Korelasi")
    if st.session_state.df is not None:
        df = st.session_state.df
        df_numeric = df.select_dtypes(include=['number'])
        if 'No' in df_numeric.columns: df_numeric = df_numeric.drop(columns=['No'])
        st.subheader("🔢 Matriks Korelasi (Heatmap)")
        fig, ax = plt.subplots(figsize=(14, 10))
        corr_matrix = df_numeric.corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5,
                    mask=np.triu(np.ones_like(corr_matrix, dtype=bool)), ax=ax, annot_kws={"size":8})
        ax.set_title('Matriks Korelasi Antar Variabel Numerik', fontsize=14, fontweight='bold')
        st.pyplot(fig)

        target = 'Response time'
        if target in df_numeric.columns:
            st.subheader("🎯 Korelasi dengan Response Time")
            correlations = df_numeric.corrwith(df_numeric[target]).sort_values(ascending=False)
            corr_df = pd.DataFrame({'Variable': correlations.index, 'Correlation': correlations.values}).iloc[1:]
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(corr_df['Variable'], corr_df['Correlation'], color=['green' if x > 0 else 'red' for x in corr_df['Correlation']])
            ax.set_xlabel('Korelasi'); ax.set_title(f'Korelasi Variabel dengan {target}'); ax.axvline(x=0, color='black', linewidth=0.5)
            st.pyplot(fig)

            st.subheader("📊 Analisis Korelasi Spesifik")
            col1, col2 = st.columns(2)
            with col1: var1 = st.selectbox("Pilih Variabel 1", df_numeric.columns, key='corr_var1')
            with col2: var2 = st.selectbox("Pilih Variabel 2", df_numeric.columns, key='corr_var2')
            if var1 and var2 and var1 != var2:
                data_clean = df_numeric[[var1, var2]].dropna()
                rho, p_val = spearmanr(data_clean[var1], data_clean[var2])
                st.info(f"""
                **Hasil Analisis Spearman Correlation:**
                - Rho: **{rho:.3f}**
                - P-value: **{p_val:.5f}**
                - Interpretasi: {'Signifikan' if p_val < 0.05 else 'Tidak Signifikan'}
                """)

# ==================== MODULE 4: MACHINE LEARNING ====================
elif menu == "4. Machine Learning":
    st.header("🤖 Machine Learning - Random Forest Regressor")
    if st.session_state.df is not None:
        df = st.session_state.df
        st.subheader("⚙️ Konfigurasi Model")
        default_features = ['Jarak tempuh ke TKP (km)','Usia (tahun)','Trauma / Non-Trauma',
                            'Jenis Kelamin','Kategori Waktu','Travel time','Dispatch time','Chute time']
        available_features = [col for col in default_features if col in df.columns]
        selected_features = st.multiselect("Pilih fitur untuk training model", available_features,
            default=available_features[:5] if len(available_features) > 5 else available_features, key='feature_select')
        target = st.selectbox("Pilih target variable", ['Response time','Scene Time','Travel time'], index=0, key='target_select')
        if target not in df.columns:
            st.error(f"Target column '{target}' not found!")
        elif len(selected_features) == 0:
            st.warning("Please select at least one feature!")
        else:
            df_ml = df[selected_features + [target]].dropna()
            if len(df_ml) == 0:
                st.error("No valid data after removing missing values!")
            else:
                X = df_ml[selected_features]; y = df_ml[target]
                test_size   = st.slider("Test set size (%)", 10, 40, 20, key='test_size') / 100
                n_estimators = st.slider("Number of trees", 50, 300, 100, 50, key='n_estimators')
                if st.button("🚀 Train Model", key='train_btn'):
                    with st.spinner("Training model..."):
                        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
                        model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
                        model.fit(X_train, y_train)
                        st.session_state.model = model; st.session_state.features = selected_features
                        y_pred = model.predict(X_test)
                        col1, col2, col3 = st.columns(3)
                        with col1: st.metric("R² Score", f"{r2_score(y_test,y_pred):.3f}")
                        with col2: st.metric("MAE", f"{mean_absolute_error(y_test,y_pred):.2f} menit")
                        with col3: st.metric("Sample Size", len(df_ml))
                        st.subheader("📊 Feature Importance")
                        imp_df = pd.DataFrame({'Feature':selected_features,'Importance (%)':model.feature_importances_*100}).sort_values('Importance (%)',ascending=True)
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.barh(imp_df['Feature'], imp_df['Importance (%)'], color='teal')
                        ax.set_xlabel('Importance (%)'); ax.set_title('Feature Importance - Random Forest')
                        for i, v in enumerate(imp_df['Importance (%)']): ax.text(v+0.5, i, f'{v:.1f}%', va='center')
                        st.pyplot(fig)
                        joblib.dump({'model':model,'features':selected_features}, 'model_prediksi_respon_time.pkl')
                        with open('model_prediksi_respon_time.pkl','rb') as f:
                            st.download_button("💾 Download Model", data=f,
                                file_name="model_prediksi_respon_time.pkl",
                                mime="application/octet-stream", key='download_btn')

# ==================== MODULE 5: MODEL EVALUATION ====================
elif menu == "5. Evaluasi Model":
    st.header("📈 Evaluasi Model Prediksi")
    if st.session_state.df is not None and st.session_state.model is not None:
        df = st.session_state.df; model = st.session_state.model; features = st.session_state.features
        target = 'Response time'
        if target in df.columns and all(f in df.columns for f in features):
            df_eval = df[features+[target]].dropna()
            X = df_eval[features]; y = df_eval[target]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            y_pred = model.predict(X_test)
            st.subheader("📊 Model Performance Metrics")
            r2 = r2_score(y_test, y_pred); mae = mean_absolute_error(y_test, y_pred)
            mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("R² Score", f"{r2:.3f}", delta="Good" if r2>0.7 else "Fair" if r2>0.5 else "Poor")
            with col2: st.metric("MAE", f"{mae:.2f} menit")
            with col3: st.metric("MAPE", f"{mape:.1f}%")
            st.subheader("📈 Actual vs Predicted Values")
            fig, axes = plt.subplots(1, 2, figsize=(14, 6))
            axes[0].scatter(y_test, y_pred, alpha=0.5, color='blue')
            axes[0].plot([y_test.min(),y_test.max()],[y_test.min(),y_test.max()],'r--',lw=2,label='Perfect Prediction')
            axes[0].set_xlabel('Actual'); axes[0].set_ylabel('Predicted'); axes[0].set_title('Actual vs Predicted'); axes[0].legend(); axes[0].grid(True,alpha=0.3)
            residuals = y_test - y_pred
            axes[1].scatter(y_pred, residuals, alpha=0.5, color='green')
            axes[1].axhline(y=0, color='r', linestyle='--', linewidth=2)
            axes[1].set_xlabel('Predicted'); axes[1].set_ylabel('Residuals'); axes[1].set_title('Residual Plot'); axes[1].grid(True,alpha=0.3)
            st.pyplot(fig)
            st.subheader("📊 Distribution of Errors")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.histplot(residuals, kde=True, ax=ax, color='purple', bins=30)
            ax.set_xlabel('Error (menit)'); ax.set_title('Error Distribution'); ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
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
            model = st.session_state.model; features = st.session_state.features
            st.info(f"Model menggunakan fitur: {', '.join(features)}")
            col1, col2 = st.columns(2); input_values = {}
            with col1:
                if 'Jarak tempuh ke TKP (km)' in features: input_values['Jarak tempuh ke TKP (km)'] = st.number_input("Jarak ke TKP (km)", 0.0, 50.0, 5.0, 0.5, key='jarak_tkp')
                if 'Usia (tahun)' in features:             input_values['Usia (tahun)']              = st.number_input("Usia Pasien (tahun)", 0, 120, 40, key='usia_pasien')
                if 'Travel time' in features:              input_values['Travel time']               = st.number_input("Travel Time (menit)", 0.0, 60.0, 10.0, 0.5, key='travel_time')
            with col2:
                if 'Dispatch time' in features: input_values['Dispatch time'] = st.number_input("Dispatch Time (menit)", 0.0, 30.0, 2.0, 0.5, key='dispatch_time')
                if 'Chute time' in features:    input_values['Chute time']    = st.number_input("Chute Time (menit)", 0.0, 30.0, 1.0, 0.5, key='chute_time')
                if 'Trauma / Non-Trauma' in features:
                    trauma = st.selectbox("Jenis Kasus", ["Non-Trauma","Trauma"], key='trauma_select_tab1')
                    input_values['Trauma / Non-Trauma'] = 1 if trauma=="Trauma" else 0
                if 'Jenis Kelamin' in features:
                    jk = st.selectbox("Jenis Kelamin", ["Laki-laki","Perempuan"], key='jenis_kelamin_pred')
                    input_values['Jenis Kelamin'] = 1 if jk=="Laki-laki" else 0
                if 'Kategori Waktu' in features:
                    kw = st.selectbox("Kategori Waktu", ["Pagi","Siang","Sore","Malam"], key='kat_waktu_pred')
                    input_values['Kategori Waktu'] = {"Pagi":0,"Siang":1,"Sore":2,"Malam":3}[kw]
            defaults = {'Jarak tempuh ke TKP (km)':5.0,'Usia (tahun)':40,'Travel time':10.0,
                        'Dispatch time':2.0,'Chute time':1.0,'Trauma / Non-Trauma':0,'Jenis Kelamin':0,'Kategori Waktu':1}
            for feat in features:
                if feat not in input_values: input_values[feat] = defaults.get(feat, 0)
            if st.button("🔮 Prediksi Response Time", type="primary", key='predict_btn'):
                try:
                    pred = model.predict(pd.DataFrame([input_values])[features])[0]
                    st.success(f"### ⏱️ Prediksi Response Time: **{pred:.1f} menit**")
                    if pred <= 15:   st.info("✅ **Target Internasional Tercapai!** (< 15 menit)")
                    elif pred <= 25: st.warning("⚠️ **Target Nasional Tercapai** (15-25 menit)")
                    else:            st.error("❌ **Di Luar Target** (> 25 menit)")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please train a model first in the Machine Learning module!")

    with tab2:
        st.subheader("🗺️ Sistem Rekomendasi Dispatch Cerdas")
        if 'tkp_lat' not in st.session_state: st.session_state.tkp_lat = -7.9797
        if 'tkp_lon' not in st.session_state: st.session_state.tkp_lon = 112.6304

        col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
        with col_cfg1: basemap = st.selectbox("🗺️ Pilih Basemap", ["OpenStreetMap","Citra Satelit","Dark Theme"], key='basemap_select')
        with col_cfg2: usia    = st.number_input("👤 Usia Pasien", 0, 120, 40, key='usia_dispatch')
        with col_cfg3: kasus   = st.selectbox("🏥 Jenis Kasus", ["Non-Trauma","Trauma"], key='kasus_select_tab2')

        col_lat, col_lon = st.columns(2)
        with col_lat: tkp_lat = st.number_input("📍 Latitude TKP",  value=st.session_state.tkp_lat, format="%.6f", step=0.0001, key='tkp_lat_input')
        with col_lon: tkp_lon = st.number_input("📍 Longitude TKP", value=st.session_state.tkp_lon, format="%.6f", step=0.0001, key='tkp_lon_input')
        st.session_state.tkp_lat = tkp_lat; st.session_state.tkp_lon = tkp_lon

        POSKO = {
            "PMI Kota Malang":         {"lat":-7.9731,"lon":112.6186,"icon":"🏥","color":"red",   "alamat":"Jl. Brigjen Slamet Riadi No.4, Malang"},
            "RSUD dr. Saiful Anwar":   {"lat":-7.9630,"lon":112.6347,"icon":"🏨","color":"blue",  "alamat":"Jl. Jaksa Agung Suprapto No.2, Malang"},
            "FK Universitas Brawijaya":{"lat":-7.9523,"lon":112.6137,"icon":"🎓","color":"green", "alamat":"Jl. Veteran, Malang"},
        }
        BASEMAP_TILES = {
            "OpenStreetMap": {"tiles":"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png","attr":"© OpenStreetMap contributors"},
            "Citra Satelit": {"tiles":"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}","attr":"© Esri"},
            "Dark Theme":    {"tiles":"https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png","attr":"© CartoDB"},
        }
        selected_tile = BASEMAP_TILES[basemap]

        def haversine(lat1,lon1,lat2,lon2):
            R=6371; dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)
            a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
            return R*2*math.asin(math.sqrt(a))

        def get_osrm_route(lat1,lon1,lat2,lon2):
            try:
                url=f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
                resp=requests.get(url,timeout=10)
                if resp.status_code==200:
                    data=resp.json()
                    if data.get("routes"):
                        r=data["routes"][0]
                        return [[c[1],c[0]] for c in r["geometry"]["coordinates"]], r["distance"]/1000, r["duration"]/60
            except: pass
            return None, None, None

        def get_status(w):
            if w<=15: return "🟢 Target Internasional (Aman)"
            elif w<=25: return "🟡 Target Nasional (Waspada)"
            else: return "🔴 Terlambat (>25 menit)"

        m = folium.Map(location=[-7.9797,112.6304], zoom_start=13, tiles=selected_tile["tiles"], attr=selected_tile["attr"])
        folium.Marker([tkp_lat,tkp_lon], popup=f"<b>📍 TKP</b><br>Lat:{tkp_lat:.5f}<br>Lon:{tkp_lon:.5f}",
            tooltip="📍 TKP", icon=folium.Icon(color="orange",icon="exclamation-sign",prefix="glyphicon")).add_to(m)
        for nama, info in POSKO.items():
            jarak = haversine(tkp_lat,tkp_lon,info["lat"],info["lon"])
            folium.Marker([info["lat"],info["lon"]],
                popup=folium.Popup(f"<b>{info['icon']} {nama}</b><br>{info['alamat']}<br>Jarak:{jarak:.2f}km",max_width=250),
                tooltip=f"{info['icon']} {nama}", icon=folium.Icon(color=info["color"],icon="plus-sign",prefix="glyphicon")).add_to(m)
        m.add_child(folium.LatLngPopup())
        st.info("💡 Klik pada peta untuk mendapatkan koordinat TKP")
        map_data = st_folium(m, width="100%", height=450, key="dispatch_map")
        if map_data and map_data.get("last_clicked"):
            clicked = map_data["last_clicked"]
            st.session_state.tkp_lat = round(clicked["lat"],6)
            st.session_state.tkp_lon = round(clicked["lng"],6)
            st.success(f"✅ Koordinat TKP: Lat {st.session_state.tkp_lat}, Lon {st.session_state.tkp_lon}")
            st.rerun()

        st.markdown("---")
        if st.session_state.dispatch_result is not None:
            s = st.session_state.dispatch_result
            if s["tkp_lat"]!=tkp_lat or s["tkp_lon"]!=tkp_lon or s["kasus"]!=kasus:
                st.session_state.dispatch_result = None

        if st.button("🏆 Cari Unit Tercepat & Tampilkan Rute", type="primary", key='cari_unit_btn'):
            pen = 10.0 if kasus=="Trauma" else 0.0
            with st.spinner("🔍 Mengambil rute..."):
                hasil_rute = []
                for nama, info in POSKO.items():
                    coords, dist_km, dur_min = get_osrm_route(info["lat"],info["lon"],tkp_lat,tkp_lon)
                    if dist_km is None: dist_km = haversine(tkp_lat,tkp_lon,info["lat"],info["lon"])*1.3
                    est = 15.3 + 0.93*dist_km + 0.10*usia - pen
                    hasil_rute.append({"nama":nama,"info":info,"coords":coords,"dist_km":dist_km,"est_waktu":est})
                hasil_rute.sort(key=lambda x: x["est_waktu"])
                st.session_state.dispatch_result = {"hasil_rute":hasil_rute,"tkp_lat":tkp_lat,"tkp_lon":tkp_lon,"kasus":kasus,"selected_tile":selected_tile}

        if st.session_state.dispatch_result is not None:
            res = st.session_state.dispatch_result
            hasil_rute = res["hasil_rute"]; _tkp_lat=res["tkp_lat"]; _tkp_lon=res["tkp_lon"]
            _tile=res["selected_tile"]; tercepat=hasil_rute[0]
            ROUTE_COLORS = ["#FF4136","#0074D9","#2ECC40","#FF851B"]
            m2 = folium.Map(location=[_tkp_lat,_tkp_lon], zoom_start=13, tiles=_tile["tiles"], attr=_tile["attr"])
            folium.Marker([_tkp_lat,_tkp_lon], popup=f"<b>📍 TKP</b>", tooltip="📍 TKP",
                icon=folium.Icon(color="orange",icon="exclamation-sign",prefix="glyphicon")).add_to(m2)
            for i, hasil in enumerate(hasil_rute):
                info=hasil["info"]; chex=ROUTE_COLORS[i%len(ROUTE_COLORS)]
                label="★ TERCEPAT" if i==0 else f"#{i+1}"
                folium.Marker([info["lat"],info["lon"]],
                    popup=folium.Popup(f"<b>{info['icon']} {hasil['nama']}</b><br>{info['alamat']}<br>Jarak:{hasil['dist_km']:.2f}km<br>Est:{hasil['est_waktu']:.1f}mnt<br>{label}",max_width=280),
                    tooltip=f"{info['icon']} {hasil['nama']} — {hasil['est_waktu']:.1f}mnt ({label})",
                    icon=folium.Icon(color=info["color"],icon="plus-sign",prefix="glyphicon")).add_to(m2)
                if hasil["coords"]:
                    folium.PolyLine(hasil["coords"], color=chex, weight=6 if i==0 else 3,
                        opacity=1.0 if i==0 else 0.5, dash_array=None if i==0 else "8 6").add_to(m2)
                    if len(hasil["coords"])>2:
                        mid=hasil["coords"][len(hasil["coords"])//2]
                        folium.Marker(mid, icon=folium.DivIcon(
                            html=f'<div style="background:{chex};color:white;padding:2px 6px;border-radius:8px;font-size:11px;font-weight:bold;white-space:nowrap">{label} {hasil["est_waktu"]:.1f}mnt</div>',
                            icon_size=(120,24), icon_anchor=(60,12))).add_to(m2)
                else:
                    folium.PolyLine([[info["lat"],info["lon"]],[_tkp_lat,_tkp_lon]], color=chex, weight=3, opacity=0.5, dash_array="10 5").add_to(m2)
            m2.fit_bounds([[_tkp_lat,_tkp_lon]]+[[h["info"]["lat"],h["info"]["lon"]] for h in hasil_rute])
            st.markdown("### 🗺️ Peta Network Analysis")
            st_folium(m2, width="100%", height=500, key="route_map")
            st.markdown("---")
            st.markdown(f"""
### 🎯 REKOMENDASI UTAMA
## {tercepat['info']['icon']} {tercepat['nama']}
📍 {tercepat['info']['alamat']}

| Parameter | Nilai |
|---|---|
| ⏱️ Est. Response Time | **{tercepat['est_waktu']:.1f} menit** |
| 🛣️ Jarak Jalan | **{tercepat['dist_km']:.2f} km** |
| 📍 Koordinat TKP | **{_tkp_lat:.5f}, {_tkp_lon:.5f}** |
| 🏥 Jenis Kasus | **{res['kasus']}** |

**Status:** {get_status(tercepat['est_waktu'])}""")
            if tercepat['est_waktu'] > 15: st.warning("⚠️ Unit di luar jangkauan ideal!")
            else: st.success("✅ Unit dalam jangkauan ideal. Segera dispatch!")
            st.markdown("---")
            st.markdown("### 📊 Perbandingan Semua Posko")
            cols_r = st.columns(len(hasil_rute))
            for i, h in enumerate(hasil_rute):
                with cols_r[i]:
                    st.metric(f"{h['info']['icon']} {h['nama']}", f"{h['est_waktu']:.1f} mnt",
                        delta=f"{h['dist_km']:.2f} km | {'🥇 Tercepat' if i==0 else f'#{i+1}'}")

# ==================== APP FOOTER ====================
st.markdown("---")
st.markdown("""
<style>
.app-footer {
    background-image: url('https://cdn-assets-eu.frontify.com/s3/frontify-enterprise-files-eu/eyJvYXV0aCI6eyJjbGllbnRfaWQiOiJmcm9udGlmeS1maW5kZXIifSwicGF0aCI6ImloaC1oZWFsdGhjYXJlLWJlcmhhZFwvYWNjb3VudHNcL2MzXC80MDAwNjI0XC9wcm9qZWN0c1wvMjA5XC9hc3NldHNcLzEzXC8zODYyN1wvOWMxZTZiNzIyOTExYjNhM2IzYzkwNjI0YjYwNTlkNGItMTY1ODMwMjcwOS5qcGcifQ:ihh-healthcare-berhad:zOZW-7xDeRWRElxFHAOmqabzJivPI5ELSJAwHPd3mJU?format=webp');
    background-size:cover;background-position:center;background-repeat:no-repeat;
    position:relative;border-radius:16px;padding:2rem 2.5rem;margin-top:1rem;color:white;overflow:hidden;
}
.app-footer::before {
    content:'';position:absolute;top:0;left:0;right:0;bottom:0;
    background:linear-gradient(135deg,rgba(10,10,40,0.82) 0%,rgba(15,30,80,0.78) 50%,rgba(5,15,50,0.85) 100%);
    border-radius:16px;z-index:0;
}
.app-footer>*{position:relative;z-index:1}
.app-footer .footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:2rem;margin-bottom:1.5rem}
.app-footer h3{color:#FFD700;font-size:1.1rem;margin-bottom:.6rem}
.app-footer h4{color:#FFD700;font-size:.9rem;margin-bottom:.5rem}
.app-footer p,.app-footer li{color:rgba(255,255,255,.85);font-size:.82rem;line-height:1.7;margin:.15rem 0}
.app-footer ul{padding-left:1.1rem;margin:0}
.app-footer .badge-row{display:flex;flex-wrap:wrap;gap:6px;margin-top:.6rem}
.app-footer .badge{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:20px;padding:3px 12px;font-size:.75rem;color:white}
.app-footer .footer-divider{border:none;border-top:1px solid rgba(255,255,255,.15);margin:1rem 0}
.app-footer .footer-bottom{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem}
.app-footer .footer-bottom p{font-size:.78rem;color:rgba(255,255,255,.6);margin:0}
.app-footer .credit-name{color:#FFD700;font-weight:bold}
</style>
<div class="app-footer">
  <div class="footer-grid">
    <div>
      <h3>🚑 Analitik Data Sains & Decision Support Systems (DSS) Aksesibilitas PSC 119</h3>
      <p>Platform analitik data sains & sistem pengambilan keputusan berbasis <strong>Machine Learning</strong>
      untuk memantau, menganalisis, dan memprediksi <em>response time</em> ambulans PSC 119 Kota Malang.</p>
      <div class="badge-row">
        <span class="badge">🐍 Python 3.x</span><span class="badge">📡 Streamlit</span>
        <span class="badge">🌍 GIS</span><span class="badge">🧠 Random Forest</span>
        <span class="badge">📊 Scikit-learn</span><span class="badge">📈 Seaborn</span>
        <span class="badge">🔢 Pandas</span>
      </div>
    </div>
    <div>
      <h4>🎯 Fitur Utama</h4>
      <ul>
        <li>📁 Data Cleaning otomatis</li><li>📊 EDA &amp; Visualisasi Interaktif</li>
        <li>🔗 Analisis Korelasi Spearman</li><li>🤖 Prediksi ML Real-time</li>
        <li>📈 Evaluasi Model Komprehensif</li><li>🚨 Sistem Dispatch Cerdas</li>
      </ul>
    </div>
    <div>
      <h4>👨‍💻 Tim Pengembang</h4>
      <p><span class="credit-name">dr. Aurick Yudha Nagara</span><br>Sp.EM., KPEC.<br><em>Concept &amp; Design</em></p>
      <br>
      <p><span class="credit-name">Adipandang Yudono, PhD</span><br><em>GIS Engineering, Spatial Data Science, &amp; WebGIS Developer</em></p>
      <br>
      <h4>🏥 Institusi</h4>
      <p>PSC 119 — Dinas Kesehatan Kota Malang</p>
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
