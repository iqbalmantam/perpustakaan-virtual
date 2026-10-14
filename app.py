import datetime
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman & Sembunyikan Elemen Bawaan Streamlit
st.set_page_config(
    page_title="Perpustakaan Virtual Gemini: Konsol AI",
    page_icon="🏛️",
    layout="wide",
)

# Custom CSS Bergaya Konsol Hologram & Ruang Perpustakaan Futuristik
st.markdown("""
    <style>
    /* Sembunyikan Header, Footer, dan Menu Bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tema Utama: Latar Belakang Gelap Luar Angkasa / Konsol Digital */
    .stApp {
        background-color: #050814;
        color: #c9d1d9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Judul Utama Bergaya Hologram Neon */
    .hero-title {
        text-align: center;
        color: #00f3ff;
        font-size: 2.2rem;
        font-weight: 800;
        text-shadow: 0 0 15px rgba(0, 243, 255, 0.6);
        margin-bottom: 5px;
    }
    .hero-subtitle {
        text-align: center;
        color: #8b949e;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* Kotak Panel Konsol / Form Input */
    .console-box {
        background: rgba(13, 17, 23, 0.85);
        border: 1px solid rgba(0, 243, 255, 0.3);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.15);
        margin-bottom: 30px;
    }

    /* Kartu Pengetahuan Bergaya Panel Hologram */
    .skill-card {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.9) 0%, rgba(13, 17, 23, 0.95) 100%);
        padding: 22px;
        border-radius: 12px;
        border: 1px solid rgba(88, 166, 255, 0.3);
        margin-bottom: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    .skill-card:hover {
        border-color: #00f3ff;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.25);
    }

    /* Styling Metrik Kosmik */
    .stMetric {
        background: rgba(22, 27, 34, 0.8);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(88, 166, 255, 0.2);
        box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.05);
    }
    
    /* Tombol Konsol */
    .stButton>button {
        background: linear-gradient(90deg, #007acc 0%, #00f3ff 100%);
        color: #050814;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
        transition: 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.8);
    }
    </style>
""", unsafe_allow_html=True)

# Header Visual Ala Konsol Gemini
st.markdown('<p class="hero-title">🏛️ KONSOL PERPUSTAKAAN VIRTUAL GEMINI</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Peta Pengetahuan, Logika Pemrograman, dan Evolusi Keterampilan Terintegrasi</p>', unsafe_allow_html=True)

# Fungsi Koneksi Google Sheets
@st.cache_resource
def init_connection():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        sheet = client.open("Database_Skill_Gemini").sheet1
        return sheet
    except Exception as e:
        return None

sheet = init_connection()

# Memuat Data dari Google Sheets
df = pd.DataFrame()
if sheet:
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
    except Exception as e:
        pass

# Fallback Data Jika Kosong
if df.empty or "Skill" not in df.columns:
    df = pd.DataFrame([
        {
            "Kategori": "Logika & Pemrograman",
            "Skill": "Python & Streamlit App Development",
            "Level": 95,
            "Tanggal": "2026-07-15",
            "Deskripsi": "Pengembangan aplikasi web operasional dan kalkulator otomatis."
        }
    ])

# ==================== KONSOL INPUT (TANPA SIDEBAR / FRAME KIRI) ====================
st.markdown('<div class="console-box">', unsafe_allow_html=True)
st.markdown("### ➕ Terminal Input: Catat Perkembangan Skill Baru")

with st.form("add_skill_form_hologram", clear_on_submit=True):
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    
    with col_f1:
        new_kategori = st.selectbox(
            "Sayap / Ruang Perpustakaan",
            ["Logika & Pemrograman", "Inovasi & Teknologi", "Kreativitas & Seni", "Bahasa & Komunikasi", "Pengetahuan Umum & Sains"]
        )
        new_skill = st.text_input("Nama Skill / Pengetahuan")
        
    with col_f2:
        new_level = st.slider("Tingkat Penguasaan (%)", 10, 100, 85)
        new_desc = st.text_area("Catatan / Poin Pembelajaran", height=68)
        
    with col_f3:
        st.markdown("<br><br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("Simpan ke Cloud", use_container_width=True)

    if submit_btn and new_skill:
        new_row = [new_kategori, new_skill, int(new_level), str(datetime.date.today()), new_desc]
        if sheet:
            try:
                sheet.append_row(new_row)
                st.success(f"Skill '{new_skill}' berhasil disinkronkan ke Google Sheets!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan ke Google Sheets: {e}")
        else:
            st.error("Koneksi Google Sheets belum terdeteksi. Periksa kembali pengaturan Secrets.")

st.markdown('</div>', unsafe_allow_html=True)

# Statistik Ringkas Konsol
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Kategori Aktif", len(df["Kategori"].unique()) if not df.empty else 0)
with col2:
    st.metric("Total Skill Tercatat", len(df) if not df.empty else 0)
with col3:
    avg_level = int(df["Level"].mean()) if not df.empty and "Level" in df.columns else 0
    st.metric("Rata-rata Penguasaan", f"{avg_level}%")

st.markdown("---")
st.subheader("📚 Sayap Panel Pengetahuan & Arsip Skill")

# Filter Kategori
categories = ["Semua Ruang"] + list(df["Kategori"].unique()) if "Kategori" in df.columns else ["Semua Ruang"]
selected_category = st.selectbox("Pilih Ruang Kategori", categories)

if selected_category == "Semua Ruang":
    filtered_df = df
else:
    filtered_df = df[df["Kategori"] == selected_category]

# Render Kartu Pengetahuan Bergaya Hologram Panel
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        st.markdown(f"""
        <div class="skill-card">
            <h3 style="margin-top: 0; color: #00f3ff;">📖 {row.get('Skill', 'Skill')} 
                <span style="float: right; font-size: 16px; color: #58a6ff; background: rgba(0,243,255,0.1); padding: 2px 10px; border-radius: 6px; border: 1px solid rgba(0,243,255,0.3);">
                    {row.get('Level', 0)}% Penguasaan
                </span>
            </h3>
            <p style="color: #8b949e; font-size: 0.9rem; margin-bottom: 8px;">
                <b>Kategori:</b> <span style="color: #c9d1d9;">{row.get('Kategori', '-')}</span> &nbsp;|&nbsp; 
                <b>Dicatat Pada:</b> <span style="color: #c9d1d9;">{row.get('Tanggal', '-')}</span>
            </p>
            <p style="color: #e6edf3; margin-bottom: 0;">{row.get('Deskripsi', '-')}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Belum ada data skill di kategori ini.")
