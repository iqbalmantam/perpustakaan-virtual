import datetime
import pandas as pd
import streamlit as st

# Opsional: Jika menggunakan gspread untuk Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman
st.set_page_config(
    page_title="Perpustakaan Pengetahuan & Skill Gemini",
    page_icon="🏛️",
    layout="wide",
)

# Styling Tema Perpustakaan Digital Futuristik
st.markdown(
    """
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .skill-card { background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    </style>
""",
    unsafe_allow_html=True,
)

st.title(
    "🏛️ Perpustakaan Virtual Gemini: Peta Pengetahuan & Evolusi Keterampilan"
)
st.markdown(
    "Ruang interaktif berbasis cloud untuk merangkum, memantau, dan mengembangkan setiap ilmu dan skill yang dipelajari bersama AI."
)


# Fungsi untuk menghubungkan ke Google Sheets via Streamlit Secrets
@st.cache_resource
def init_connection():
    try:
        # Mengambil kredensial dari st.secrets (disetel di panel Streamlit Cloud)
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_info(
            creds_dict, scopes=scopes
        )
        client = gspread.authorize(credentials)
        # Nama file Google Sheets Anda di Drive
        sheet = client.open("Database_Skill_Gemini").sheet1
        return sheet
    except Exception as e:
        return None


sheet = init_connection()

# Memuat data dari Google Sheets (jika gagal, gunakan fallback data sesi)
if sheet:
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if df.empty or "Skill" not in df.columns:
            # Fallback data awal jika sheet masih kosong
            df = pd.DataFrame(
                [
                    {
                        "Kategori": "Logika & Pemrograman",
                        "Skill": "Python & Streamlit App Development",
                        "Level": 95,
                        "Tanggal": "2026-07-15",
                        "Deskripsi": (
                            "Pengembangan aplikasi web operasional dan"
                            " manajemen database."
                        ),
                    }
                ]
            )
    except Exception:
        df = pd.DataFrame(
            [
                {
                    "Kategori": "Logika & Pemrograman",
                    "Skill": "Python & Streamlit App Development",
                    "Level": 95,
                    "Tanggal": "2026-07-15",
                    "Deskripsi": "Koneksi Google Sheets belum dikonfigurasi.",
                }
            ]
        )
else:
    # Mode cadangan session state jika secrets belum diatur
    if "skills_data" not in st.session_state:
        st.session_state.skills_data = [
            {
                "Kategori": "Logika & Pemrograman",
                "Skill": "Python & Streamlit App Development",
                "Level": 95,
                "Tanggal": "2026-07-15",
                "Deskripsi": (
                    "Pengembangan aplikasi web operasional dan kalkulator"
                    " otomatis."
                ),
            }
        ]
    df = pd.DataFrame(st.session_state.skills_data)

# Sidebar: Tambah Perkembangan Skill Baru
st.sidebar.header("➕ Catat Perkembangan Skill Baru")
with st.sidebar.form("add_skill_form"):
    new_kategori = st.selectbox(
        "Sayap / Ruang Perpustakaan",
        [
            "Logika & Pemrograman",
            "Inovasi & Teknologi",
            "Kreativitas & Seni",
            "Bahasa & Komunikasi",
            "Pengetahuan Umum & Sains",
        ],
    )
    new_skill = st.text_input("Nama Skill / Pengetahuan")
    new_level = st.slider("Tingkat Penguasaan (%)", 10, 100, 85)
    new_desc = st.text_area("Catatan / Poin Pembelajaran")
    submit_btn = st.form_submit_button("Simpan ke Google Sheets")

    if submit_btn and new_skill:
        new_row = [
            new_kategori,
            new_skill,
            int(new_level),
            str(datetime.date.today()),
            new_desc,
        ]
        if sheet:
            try:
                sheet.append_row(new_row)
                st.success(
                    f"Skill '{new_skill}' berhasil disimpan ke Google Sheets!"
                )
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan ke Google Sheets: {e}")
        else:
            # Simpan ke session jika sheet tidak aktif
            st.session_state.skills_data.append(
                {
                    "Kategori": new_kategori,
                    "Skill": new_skill,
                    "Level": new_level,
                    "Tanggal": str(datetime.date.today()),
                    "Deskripsi": new_desc,
                }
            )
            st.success(
                f"Skill '{new_skill}' berhasil ditambahkan secara lokal!"
            )
            st.rerun()

# Statistik Ringkas Perpustakaan
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Kategori Aktif", len(df["Kategori"].unique()))
with col2:
    st.metric("Total Skill Tercatat", len(df))
with col3:
    avg_level = int(df["Level"].mean()) if not df.empty else 0
    st.metric("Rata-rata Penguasaan", f"{avg_level}%")

st.markdown("---")
st.subheader("📚 Jelajahi Sayap Perpustakaan")

# Filter Berdasarkan Kategori
selected_category = st.selectbox(
    "Pilih Ruang Kategori", ["Semua Ruang"] + list(df["Kategori"].unique())
)

if selected_category == "Semua Ruang":
    filtered_df = df
else:
    filtered_df = df[df["Kategori"] == selected_category]

# Render Kartu Pengetahuan
for index, row in filtered_df.iterrows():
    st.markdown(
        f"""
    <div class="skill-card">
        <h3>📖 {row['Skill']} <span style="float: right; font-size: 16px; color: #58a6ff;">{row['Level']}% Penguasaan</span></h3>
        <p style="color: #8b949e; margin-bottom: 8px;"><b>Kategori:</b> {row['Kategori']} &nbsp;|&nbsp; <b>Dicatat Pada:</b> {row['Tanggal']}</p>
        <p>{row['Deskripsi']}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
