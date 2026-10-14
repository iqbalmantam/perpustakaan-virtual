import datetime
import pandas as pd
import streamlit as st

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
    "Ruang interaktif untuk merangkum, memantau, dan mengembangkan setiap ilmu, logika pemrograman, serta skill baru yang dipelajari bersama AI."
)

# Inisialisasi Database Sederhana di Session State
if "skills_data" not in st.session_state:
    st.session_state.skills_data = [
        {
            "Kategori": "Logika & Pemrograman",
            "Skill": "Python & Streamlit App Development",
            "Level": 95,
            "Tanggal": "2026-07-15",
            "Deskripsi": (
                "Pengembangan aplikasi web operasional, manajemen database,"
                " dan kalkulator otomatis."
            ),
        },
        {
            "Kategori": "Inovasi & Teknologi",
            "Skill": "OSINT & Background Verification Tools",
            "Level": 90,
            "Tanggal": "2026-08-10",
            "Deskripsi": (
                "Teknik ekstraksi metadata dan sistem verifikasi data kandidat."
            ),
        },
        {
            "Kategori": "Kreativitas & Seni",
            "Skill": "Cinematic & Wuxia Prompt Engineering",
            "Level": 92,
            "Tanggal": "2026-06-20",
            "Deskripsi": (
                "Penyusunan prompt visual sinematik dengan estetika bela diri dan"
                " Wuxia."
            ),
        },
        {
            "Kategori": "Logika & Pemrograman",
            "Skill": "Google Sheets & Cloud Database Integration",
            "Level": 88,
            "Tanggal": "2026-09-05",
            "Deskripsi": (
                "Sinkronisasi data real-time untuk form inspeksi dan laporan"
                " harian."
            ),
        },
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
    submit_btn = st.form_submit_button("Simpan ke Perpustakaan")

    if submit_btn and new_skill:
        new_entry = {
            "Kategori": new_kategori,
            "Skill": new_skill,
            "Level": new_level,
            "Tanggal": str(datetime.date.today()),
            "Deskripsi": new_desc,
        }
        st.session_state.skills_data.append(new_entry)
        st.success(f"Skill '{new_skill}' berhasil ditambahkan ke perpustakaan!")
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

# Render Kartu Pengetahuan (Visual Rak Buku Digital)
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

st.markdown("---")
st.info(
    "💡 **Tips Pengembangan:** Anda dapat terus menambahkan *skill* baru melalui panel di sebelah kiri setiap kali mempelajari topik atau kode baru bersama Gemini. Program ini juga bisa di-deploy gratis ke **Streamlit Community Cloud** agar dapat diakses dari perangkat mana saja!"
)
