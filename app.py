import datetime
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman & Sembunyikan Elemen Bawaan Streamlit (GitHub/Menu/Footer)
st.set_page_config(
    page_title="Perpustakaan Pengetahuan & Skill Gemini",
    page_icon="🏛️",
    layout="wide",
)

st.markdown("""
    <style>
    /* Sembunyikan Menu Utama, Header, dan Footer Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .skill-card { background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .form-box { background-color: #161b22; padding: 25px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏛️ Perpustakaan Virtual Gemini: Peta Pengetahuan & Evolusi Keterampilan")
st.markdown("Ruang interaktif berbasis cloud untuk merangkum, memantau, dan mengembangkan setiap ilmu dan skill yang dipelajari bersama AI.")
st.markdown("---")

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

# Load Data dari Google Sheets
df = pd.DataFrame()
if sheet:
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
    except Exception as e:
        st.warning(f"Catatan: Menggunakan data lokal sementara karena pembacaan Google Sheets gagal: {e}")

# Fallback Data Jika Kosong / Belum Ada Data di Sheets
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

# ==================== FORM UTAMA (TANPA FRAME KIRI / SIDEBAR) ====================
with st.container():
    st.markdown("### ➕ Catat Perkembangan Skill Baru")
    with st.form("add_skill_form_main", clear_on_submit=True):
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
            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("Simpan ke Google Sheets", use_container_width=True)

        if submit_btn and new_skill:
            new_row = [new_kategori, new_skill, int(new_level), str(datetime.date.today()), new_desc]
            if sheet:
                try:
                    # Pastikan header baris pertama Google Sheets Anda: Kategori | Skill | Level | Tanggal | Deskripsi
                    sheet.append_row(new_row)
                    st.success(f"Skill '{new_skill}' berhasil disimpan permanen ke Google Sheets!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan ke Google Sheets: {e}")
            else:
                st.error("Koneksi Google Sheets belum terdeteksi. Periksa kembali konfigurasi Secrets.")

st.markdown("---")

# Statistik Ringkas Perpustakaan
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Kategori Aktif", len(df["Kategori"].unique()) if not df.empty else 0)
with col2:
    st.metric("Total Skill Tercatat", len(df) if not df.empty else 0)
with col3:
    avg_level = int(df["Level"].mean()) if not df.empty and "Level" in df.columns else 0
    st.metric("Rata-rata Penguasaan", f"{avg_level}%")

st.markdown("---")
st.subheader("📚 Jelajahi Sayap Perpustakaan")

# Filter Berdasarkan Kategori
categories = ["Semua Ruang"] + list(df["Kategori"].unique()) if "Kategori" in df.columns else ["Semua Ruang"]
selected_category = st.selectbox("Pilih Ruang Kategori", categories)

if selected_category == "Semua Ruang":
    filtered_df = df
else:
    filtered_df = df[df["Kategori"] == selected_category]

# Render Kartu Pengetahuan
if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        st.markdown(f"""
        <div class="skill-card">
            <h3>📖 {row.get('Skill', 'Skill')} <span style="float: right; font-size: 16px; color: #58a6ff;">{row.get('Level', 0)}% Penguasaan</span></h3>
            <p style="color: #8b949e; margin-bottom: 8px;"><b>Kategori:</b> {row.get('Kategori', '-')} &nbsp;|&nbsp; <b>Dicatat Pada:</b> {row.get('Tanggal', '-')}</p>
            <p>{row.get('Deskripsi', '-')}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Belum ada data skill di kategori ini.")
