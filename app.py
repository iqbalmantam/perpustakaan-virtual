import datetime
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman & Sembunyikan Elemen Bawaan Streamlit
st.set_page_config(
    page_title="Konsol Hologram Perpustakaan Gemini",
    page_icon="🏛️",
    layout="wide",
)

# Custom CSS: Desain Persis Seperti Panel Hologram Konsol di Gambar
st.markdown("""
    <style>
    /* Sembunyikan Header, Footer, dan Menu Bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Latar Belakang Konsol Ruang Digital Gelap Futuristik */
    .stApp {
        background: radial-gradient(circle at 50% 30%, #08111e 0%, #03070d 100%);
        color: #c9d1d9;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Utama Bergaya Hologram Ruang Kendali */
    .holo-header {
        background: rgba(13, 25, 43, 0.75);
        border: 1px solid rgba(0, 243, 255, 0.4);
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 0 30px rgba(0, 243, 255, 0.25);
        backdrop-filter: blur(12px);
        margin-bottom: 25px;
    }
    .holo-title {
        color: #00f3ff;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-shadow: 0 0 15px rgba(0, 243, 255, 0.8);
        margin: 0;
    }
    .holo-subtitle {
        color: #8ab4f8;
        font-size: 1.05rem;
        margin-top: 8px;
    }

    /* Panel Konsol Input Hologram */
    .console-panel {
        background: rgba(10, 18, 30, 0.85);
        border: 1px solid rgba(0, 243, 255, 0.3);
        padding: 25px;
        border-radius: 14px;
        box-shadow: inset 0 0 20px rgba(0, 243, 255, 0.08), 0 8px 32px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        margin-bottom: 30px;
    }

    /* Kartu Pengetahuan Hologram per Sayap */
    .skill-holo-card {
        background: linear-gradient(135deg, rgba(15, 28, 45, 0.9) 0%, rgba(8, 15, 25, 0.95) 100%);
        padding: 22px;
        border-radius: 12px;
        border-left: 5px solid #00f3ff;
        border-top: 1px solid rgba(0, 243, 255, 0.2);
        border-right: 1px solid rgba(0, 243, 255, 0.2);
        border-bottom: 1px solid rgba(0, 243, 255, 0.2);
        margin-bottom: 18px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
        transition: all 0.3s ease;
    }
    .skill-holo-card:hover {
        border-left-color: #ff007f;
        box-shadow: 0 0 25px rgba(0, 243, 255, 0.4);
        transform: translateY(-2px);
    }

    /* Kotak Metrik Konsol */
    .stMetric {
        background: rgba(13, 25, 43, 0.8);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(0, 243, 255, 0.25);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.1);
    }

    /* Tombol Interaktif Konsol */
    .stButton>button {
        background: linear-gradient(90deg, #007acc 0%, #00f3ff 100%);
        color: #03070d;
        font-weight: 800;
        border: none;
        border-radius: 8px;
        padding: 11px 20px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.5);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.95;
        box-shadow: 0 0 25px rgba(0, 243, 255, 0.9);
    }
    </style>
""", unsafe_allow_html=True)

# Header Utama Hologram
st.markdown("""
    <div class="holo-header">
        <p class="holo-title">🏛️ PERPUSTAKAAN VIRTUAL GEMINI: KONSOL KENDALI</p>
        <p class="holo-subtitle">Peta Pengetahuan, Logika Pemrograman, dan Evolusi Keterampilan Interaktif</p>
    </div>
""", unsafe_allow_html=True)

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

# Fallback Data Awal Jika Kosong
if df.empty or "Skill" not in df.columns:
    df = pd.DataFrame([
        {
            "Kategori": "Logika & Pemrograman",
            "Skill": "Python & Streamlit App Development",
            "Level": 95,
            "Tanggal": "2026-07-15",
            "Deskripsi": "Pengembangan konsol web operasional dan sinkronisasi cloud database."
        }
    ])

# ==================== KONSOL PANEL INPUT (TANPA SIDEBAR) ====================
st.markdown('<div class="console-panel">', unsafe_allow_html=True)
st.markdown("### ➕ Terminal Input: Daftarkan Skill & Pengetahuan Baru")

with st.form("add_skill_form_holo", clear_on_submit=True):
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
        submit_btn = st.form_submit_button("Sinkronkan ke Cloud", use_container_width=True)

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

# Statistik Konsol Hologram
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Kategori Aktif", len(df["Kategori"].unique()) if not df.empty else 0)
with col2:
    st.metric("Total Skill Tercatat", len(df) if not df.empty else 0)
with col3:
    avg_level = int(df["Level"].mean()) if not df.empty and "Level" in df.columns else 0
    st.metric("Rata-rata Penguasaan", f"{avg_level}%")

st.markdown("---")
st.subheader("📚 Arsip Sayap & Panel Pengetahuan Hologram")

# Filter Kategori Sayap Perpustakaan
categories = ["Semua Ruang"] + list(df["Kategori"].unique()) if "Kategori" in df.columns else ["Semua Ruang"]
selected_category = st.selectbox("Pilih Ruang Kategori Sayap", categories)

if selected_category == "Semua Ruang":
    filtered_df = df
else:
    filtered_df = df[df["Kategori"] == selected_category]

# Render Kartu Hologram
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        st.markdown(f"""
        <div class="skill-holo-card">
            <h3 style="margin-top: 0; color: #00f3ff; display: flex; justify-content: space-between; align-items: center;">
                <span>📖 {row.get('Skill', 'Skill')}</span>
                <span style="font-size: 0.9rem; color: #03070d; background: #00f3ff; padding: 3px 12px; border-radius: 20px; font-weight: 700;">
                    {row.get('Level', 0)}% Penguasaan
                </span>
            </h3>
            <p style="color: #8ab4f8; font-size: 0.9rem; margin-bottom: 8px;">
                <b>Kategori Sayap:</b> <span style="color: #c9d1d9;">{row.get('Kategori', '-')}</span> &nbsp;|&nbsp; 
                <b>Dicatat Pada:</b> <span style="color: #c9d1d9;">{row.get('Tanggal', '-')}</span>
            </p>
            <p style="color: #e6edf3; margin-bottom: 0; line-height: 1.5;">{row.get('Deskripsi', '-')}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Belum ada data skill di kategori sayap ini.")
