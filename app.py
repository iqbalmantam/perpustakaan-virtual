import logging

import gspread
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from google.oauth2.service_account import Credentials

# Konfigurasi Halaman & Full Screen Layout
st.set_page_config(
    page_title="Perpustakaan 3D Virtual Gemini",
    page_icon="🏛️",
    layout="wide",
)

# Custom CSS untuk Menghilangkan Header, Footer, dan Padding Bawaan Streamlit
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        background-color: #03070d;
        overflow: hidden;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ===== Data Skill dari Google Sheets =====
SHEET_NAME = "Database_Skill_Gemini"
KOLOM = ["Kategori", "Skill", "Level", "Tanggal", "Deskripsi"]

# Data contoh jika Google Sheets belum terhubung / gagal dibaca
# Juga dipakai untuk mengisi otomatis Google Sheets jika masih kosong
FALLBACK = [
    {
        "Kategori": "Logika & Pemrograman",
        "Skill": "Python & Streamlit App Development",
        "Level": 95,
        "Tanggal": "2026-07-15",
        "Deskripsi": (
            "Pengembangan aplikasi web operasional warehouse, timesheet"
            " matrix, dan kalkulator manpower cost."
        ),
    },
    {
        "Kategori": "Inovasi & Teknologi",
        "Skill": "OSINT & Candidate Background Verification",
        "Level": 90,
        "Tanggal": "2026-08-10",
        "Deskripsi": (
            "Teknik ekstraksi metadata, analisis data publik, dan"
            " pembangunan web OSINT."
        ),
    },
    {
        "Kategori": "Kreativitas & Seni",
        "Skill": "Cinematic & Wuxia Prompt Engineering",
        "Level": 92,
        "Tanggal": "2026-06-20",
        "Deskripsi": (
            "Penyusunan prompt visual sinematik dengan estetika bela diri"
            " Wuxia dan aksi."
        ),
    },
    {
        "Kategori": "Logika & Pemrograman",
        "Skill": "Google Sheets & Cloud Database Integration",
        "Level": 88,
        "Tanggal": "2026-09-05",
        "Deskripsi": (
            "Sinkronisasi data real-time, manajemen database cloud, dan"
            " pelacakan rak warehouse."
        ),
    },
]


# cache_data + ttl: data di-refresh otomatis tiap 5 menit (cache_resource akan
# menyimpan data selamanya sampai aplikasi di-reboot).
@st.cache_data(ttl=300, show_spinner=False)
def get_sheets_data():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        # spreadsheets (baca+tulis) hanya diperlukan untuk isi otomatis saat sheet kosong
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        if data:
            return pd.DataFrame(data), "sheets"

        # Sheet kosong (hanya header): isi otomatis dengan rangkuman skill awal
        logging.warning("Google Sheets kosong, mengisi data awal.")
        try:
            sheet.append_rows([[item[k] for k in KOLOM] for item in FALLBACK])
            data = sheet.get_all_records()
            if data:
                return pd.DataFrame(data), "sheets"
        except Exception as e:  # mis. service account hanya punya akses Viewer
            logging.warning("Gagal mengisi data awal ke Google Sheets: %s", e)
    except Exception as e:  # alasan lengkap hanya ke log server, bukan ke pengunjung
        logging.warning("Gagal membaca Google Sheets: %s", e)
    return pd.DataFrame(FALLBACK), "fallback"


def bersihkan(df):
    """Pastikan kolom lengkap, Level numerik 0-100, dan teks bertipe string."""
    for k in KOLOM:
        if k not in df.columns:
            df[k] = ""
    df = df[KOLOM].copy()
    df["Level"] = (
        pd.to_numeric(df["Level"].astype(str).str.replace("%", "", regex=False), errors="coerce")
        .fillna(0)
        .clip(0, 100)
        .round()
        .astype(int)
    )
    for k in ["Kategori", "Skill", "Tanggal", "Deskripsi"]:
        df[k] = df[k].fillna("").astype(str)
    df = df[df["Skill"].str.strip() != ""]
    return df.head(48)  # batasi jumlah kartu agar tetap ringan


df, sumber_data = get_sheets_data()
df = bersihkan(df.copy())

# "</" di-escape supaya isi sel Sheets tidak bisa menutup tag <script> di HTML
skills_json = df.to_json(orient="records", force_ascii=False).replace("</", "<\\/")

# PENTING: r""" (raw string) dipakai supaya "\n" di dalam JavaScript tidak
# berubah menjadi baris baru oleh Python. Placeholder __SOURCE__ dan
# __SKILLS_JSON__ diisi lewat .replace() di bagian paling bawah file.
threejs_code = r"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #03070d; font-family: 'Segoe UI', sans-serif; }
        #canvas-container { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; }
        .holo-overlay {
            position: absolute; top: 14px; left: 50%; transform: translateX(-50%);
            text-align: center; color: #00f3ff; text-shadow: 0 0 15px rgba(0,243,255,0.8);
            pointer-events: none; z-index: 10;
        }
        .holo-overlay h1 { margin: 0; font-size: 1.5rem; letter-spacing: 2px; }
        .holo-overlay p { margin: 4px 0 0; color: #8ab4f8; font-size: 0.85rem; }
        .hint {
            position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
            color: #6b8cae; font-size: 0.8rem; pointer-events: none; z-index: 10;
        }
        #info-box {
            position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%);
            background: rgba(13, 25, 43, 0.85); border: 1px solid rgba(0, 243, 255, 0.5);
            padding: 12px 24px; border-radius: 12px; color: #c9d1d9; text-align: center;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.3); backdrop-filter: blur(10px);
            pointer-events: none; max-width: 600px; z-index: 10;
        }
        #info-box h3 { margin: 0 0 4px 0; color: #00f3ff; font-size: 1.1rem; }
        #info-box p { margin: 0; font-size: 0.9rem; color: #8ab4f8; }
    </style>
</head>
<body>
    <div class="holo-overlay">
        <h1>🏛️ RUANG PERPUSTAKAAN 3D VIRTUAL GEMINI</h1>
        <p id="subtitle">Peta Pengetahuan &amp; Evolusi Keterampilan • Interaktif 3D Space</p>
    </div>
    <div id="info-box">
        <h3 id="info-title"></h3>
        <p id="info-desc"></p>
    </div>
    <div class="hint">Seret mouse = putar • Scroll = zoom • Klik kanan + seret = geser</div>
    <div id="canvas-container"></div>

    <!-- Three.js + OrbitControls + Bloom (glow) -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/CopyShader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/shaders/LuminosityHighPassShader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/EffectComposer.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/RenderPass.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/ShaderPass.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/postprocessing/UnrealBloomPass.js"></script>
    <script>
        const R = 16; // radius ruangan

        // Data skill dari Python (Google Sheets atau data contoh)
        const SOURCE = "__SOURCE__";
        const rawData = __SKILLS_JSON__;

        // ===== Scene, Kamera, Renderer =====
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x03070d);
        scene.fog = new THREE.FogExp2(0x03070d, 0.012);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 4, 14);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        // ===== Kontrol Kamera =====
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(0, 3, 0);
        controls.enableDamping = true;
        controls.maxPolarAngle = Math.PI * 0.52;
        controls.maxDistance = 20;
        controls.minDistance = 3;

        // ===== Pencahayaan =====
        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const pointLight = new THREE.PointLight(0x00f3ff, 2.5, 50);
        pointLight.position.set(0, 10, 0);
        scene.add(pointLight);
        const warmLight = new THREE.PointLight(0xff9a3c, 1.2, 40);
        warmLight.position.set(0, 3, 10);
        scene.add(warmLight);

        // ===== Dinding Melingkar =====
        const wall = new THREE.Mesh(
            new THREE.CylinderGeometry(R, R, 8, 64, 1, true),
            new THREE.MeshStandardMaterial({ color: 0x0b1626, side: THREE.BackSide, metalness: 0.6, roughness: 0.4 })
        );
        wall.position.y = 3;
        scene.add(wall);

        // ===== Kubah Kaca =====
        const dome = new THREE.Mesh(
            new THREE.SphereGeometry(R, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2),
            new THREE.MeshBasicMaterial({ color: 0x4aa8ff, wireframe: true, transparent: true, opacity: 0.25 })
        );
        dome.position.y = 7;
        scene.add(dome);

        // ===== Lantai + Cincin Sirkuit =====
        const floor = new THREE.Mesh(
            new THREE.CircleGeometry(R, 64),
            new THREE.MeshStandardMaterial({ color: 0x050b14, metalness: 0.8, roughness: 0.3 })
        );
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = -1;
        scene.add(floor);

        for (let r = 3; r < R; r += 2.5) {
            const ring = new THREE.Mesh(
                new THREE.RingGeometry(r, r + 0.04, 96),
                new THREE.MeshBasicMaterial({ color: 0x00f3ff, transparent: true, opacity: 0.35, side: THREE.DoubleSide })
            );
            ring.rotation.x = -Math.PI / 2;
            ring.position.y = -0.98;
            scene.add(ring);
        }
        // Garis radial sirkuit
        for (let i = 0; i < 24; i++) {
            const a = (i / 24) * Math.PI * 2;
            const line = new THREE.Line(
                new THREE.BufferGeometry().setFromPoints([
                    new THREE.Vector3(Math.cos(a) * 3, -0.97, Math.sin(a) * 3),
                    new THREE.Vector3(Math.cos(a) * R, -0.97, Math.sin(a) * R)
                ]),
                new THREE.LineBasicMaterial({ color: 0x00a8c8, transparent: true, opacity: 0.2 })
            );
            scene.add(line);
        }

        // ===== Kota di Luar Kubah =====
        for (let i = 0; i < 120; i++) {
            const a = Math.random() * Math.PI * 2;
            const d = R + 6 + Math.random() * 20;
            const h = 4 + Math.random() * 18;
            const b = new THREE.Mesh(
                new THREE.BoxGeometry(1.5 + Math.random() * 2, h, 1.5 + Math.random() * 2),
                new THREE.MeshBasicMaterial({ color: 0x0e2238 })
            );
            b.position.set(Math.cos(a) * d, h / 2 - 1, Math.sin(a) * d);
            scene.add(b);
            // jendela menyala
            if (Math.random() > 0.4) {
                const win = new THREE.Mesh(
                    new THREE.PlaneGeometry(0.4, 0.4),
                    new THREE.MeshBasicMaterial({ color: 0xffd27a })
                );
                win.position.set(b.position.x, 1 + Math.random() * h * 0.8, b.position.z);
                win.lookAt(0, win.position.y, 0);
                scene.add(win);
            }
        }

        // ===== Panel Kategori (Teks Canvas) =====
        function makeLabel(text, color) {
            const c = document.createElement('canvas');
            c.width = 512; c.height = 256;
            const g = c.getContext('2d');
            g.fillStyle = 'rgba(5,15,30,0.92)';
            g.fillRect(0, 0, 512, 256);
            g.strokeStyle = color; g.lineWidth = 8;
            g.strokeRect(4, 4, 504, 248);
            g.fillStyle = color;
            g.font = 'bold 40px Segoe UI, Arial, sans-serif';
            g.textAlign = 'center'; g.textBaseline = 'middle';
            const lines = text.split('\n');
            lines.forEach((t, i) => g.fillText(t, 256, 128 + (i - (lines.length - 1) / 2) * 52));
            return new THREE.CanvasTexture(c);
        }

        const panels = [];
        const panelData = [
            { t: "LOGIKA &\nPEMROGRAMAN",     c: "#4aa8ff" },
            { t: "INOVASI &\nTEKNOLOGI",      c: "#00ff88" },
            { t: "KREATIVITAS\n& SENI",       c: "#b44dff" },
            { t: "BAHASA &\nKOMUNIKASI",      c: "#ffaa00" },
            { t: "PENGETAHUAN\nUMUM & SAINS", c: "#00e5ff" },
        ];
        panelData.forEach((d, i) => {
            const th = THREE.MathUtils.degToRad(-60 + (120 * i) / (panelData.length - 1));
            const p = new THREE.Mesh(
                new THREE.PlaneGeometry(4.6, 2.8),
                new THREE.MeshBasicMaterial({ map: makeLabel(d.t, d.c), side: THREE.DoubleSide })
            );
            p.position.set(Math.sin(th) * (R - 0.6), 3 + (i % 2) * 0.3, -Math.cos(th) * (R - 0.6));
            p.rotation.y = -th;
            p.userData.baseY = p.position.y;
            scene.add(p);
            panels.push(p);
        });

        // Judul besar di tengah atas
        const title = new THREE.Mesh(
            new THREE.PlaneGeometry(9, 2),
            new THREE.MeshBasicMaterial({ map: makeLabel("🏛 PERPUSTAKAAN VIRTUAL GEMINI", "#e6f7ff"), transparent: true })
        );
        title.position.set(0, 6, -(R - 0.8));
        scene.add(title);

        // ===== Kartu Skill dari Google Sheets =====
        function levelColor(lv) { return lv >= 90 ? "#00ff88" : (lv < 80 ? "#ffaa00" : "#00f3ff"); }

        function makeSkillCard(item) {
            const color = levelColor(item.Level);
            const c = document.createElement('canvas');
            c.width = 512; c.height = 256;
            const g = c.getContext('2d');
            g.fillStyle = 'rgba(5,15,30,0.92)';
            g.fillRect(0, 0, 512, 256);
            g.strokeStyle = color; g.lineWidth = 6;
            g.strokeRect(3, 3, 506, 250);
            g.fillStyle = color; g.textAlign = 'center'; g.textBaseline = 'middle';
            g.font = 'bold 34px Segoe UI, Arial, sans-serif';
            // pecah nama skill menjadi maksimal 3 baris
            const lines = []; let cur = '';
            String(item.Skill || '').split(' ').forEach(w => {
                const test = cur ? cur + ' ' + w : w;
                if (g.measureText(test).width > 440 && cur) { lines.push(cur); cur = w; } else { cur = test; }
            });
            if (cur) lines.push(cur);
            const shown = lines.slice(0, 3);
            shown.forEach((t, i) => g.fillText(t, 256, 72 + (i - (shown.length - 1) / 2) * 42));
            // bar level
            g.fillStyle = 'rgba(255,255,255,0.12)'; g.fillRect(56, 190, 400, 16);
            g.fillStyle = color; g.fillRect(56, 190, 400 * Math.min(100, item.Level) / 100, 16);
            g.font = 'bold 24px Segoe UI, Arial, sans-serif';
            g.fillText(Math.round(item.Level) + '%', 256, 228);
            return new THREE.CanvasTexture(c);
        }

        const skillCards = [];
        const perRing = 12;
        rawData.forEach((item, i) => {
            const ring = Math.floor(i / perRing);
            const inRing = Math.min(perRing, rawData.length - ring * perRing);
            const idx = i % perRing;
            const a = (idx / inRing) * Math.PI * 2 + ring * 0.3;
            const rad = 6.5 + ring * 2.6;
            const y = 2.2 + (idx % 3) * 0.9;
            const m = new THREE.Mesh(
                new THREE.PlaneGeometry(2.6, 1.3),
                new THREE.MeshBasicMaterial({ map: makeSkillCard(item), side: THREE.DoubleSide, transparent: true })
            );
            m.position.set(Math.sin(a) * rad, y, Math.cos(a) * rad);
            m.userData = { item: item, baseY: y, phase: i };
            scene.add(m);
            skillCards.push(m);
        });

        // ===== Info Box + Hover / Klik pada Kartu =====
        const infoTitle = document.getElementById('info-title');
        const infoDesc = document.getElementById('info-desc');
        function showInfo(item) {
            if (!item) {
                infoTitle.textContent = '📚 ' + rawData.length + ' skill dimuat';
                infoDesc.textContent = 'Arahkan kursor atau ketuk kartu skill untuk melihat detail';
                return;
            }
            infoTitle.textContent = '📖 ' + item.Skill + ' (' + Math.round(item.Level) + '%)';
            infoDesc.textContent = '[' + item.Kategori + '] ' + item.Deskripsi + (item.Tanggal ? '  •  ' + item.Tanggal : '');
        }
        showInfo(null);
        document.getElementById('subtitle').textContent = (SOURCE === 'sheets')
            ? 'Tersinkron dengan Google Sheets • ' + rawData.length + ' skill'
            : 'Mode data contoh (Google Sheets belum terhubung) • ' + rawData.length + ' skill';

        const raycaster = new THREE.Raycaster();
        const pointer = new THREE.Vector2(-2, -2);
        let hovered = null;
        function setPointer(e) {
            const r = renderer.domElement.getBoundingClientRect();
            pointer.x = ((e.clientX - r.left) / r.width) * 2 - 1;
            pointer.y = -((e.clientY - r.top) / r.height) * 2 + 1;
        }
        renderer.domElement.addEventListener('pointermove', setPointer);
        renderer.domElement.addEventListener('pointerdown', setPointer);
        renderer.domElement.addEventListener('pointerleave', () => pointer.set(-2, -2));

        // ===== Rak Buku Kiri & Kanan =====
        const bookCols = [0x8b4513, 0xa0522d, 0x2f4f4f, 0x6b2d5c, 0x1e3a5f, 0xb8860b];
        const bookGeo = new THREE.BoxGeometry(0.9, 0.7, 0.5);
        const bookMats = bookCols.map(c => new THREE.MeshStandardMaterial({ color: c }));
        for (let th = 1.25; th < 2.7; th += 0.05) {
            for (const s of [-1, 1]) {
                for (let row = 0; row < 7; row++) {
                    const bk = new THREE.Mesh(bookGeo, bookMats[Math.floor(Math.random() * bookMats.length)]);
                    bk.position.set(Math.sin(th) * s * (R - 0.4), -0.6 + row * 0.9, -Math.cos(th) * (R - 0.4));
                    bk.rotation.y = -th * s;
                    scene.add(bk);
                }
            }
        }

        // ===== Pohon Pengetahuan Bercabang =====
        const centralTree = new THREE.Group();
        function branch(start, dir, len, depth) {
            if (depth === 0) return;
            const end = start.clone().add(dir.clone().multiplyScalar(len));
            centralTree.add(new THREE.Line(
                new THREE.BufferGeometry().setFromPoints([start, end]),
                new THREE.LineBasicMaterial({ color: 0x5ad1ff, transparent: true, opacity: 0.3 + depth * 0.1 })
            ));
            if (depth === 1) {
                const node = new THREE.Mesh(
                    new THREE.SphereGeometry(0.06, 6, 6),
                    new THREE.MeshBasicMaterial({ color: 0xbff4ff })
                );
                node.position.copy(end);
                centralTree.add(node);
            }
            for (let i = 0; i < 3; i++) {
                const axis = new THREE.Vector3(Math.random() - 0.5, 0, Math.random() - 0.5).normalize();
                const nd = dir.clone().applyAxisAngle(axis, 0.2 + Math.random() * 0.7).normalize();
                branch(end, nd, len * 0.72, depth - 1);
            }
        }
        branch(new THREE.Vector3(0, -0.6, 0), new THREE.Vector3(0, 1, 0), 2.4, 6);
        scene.add(centralTree);

        const plat = new THREE.Mesh(
            new THREE.CylinderGeometry(2.8, 3.2, 0.4, 48),
            new THREE.MeshStandardMaterial({ color: 0x0a1a2a, emissive: 0x00c8ff, emissiveIntensity: 0.4 })
        );
        plat.position.y = -0.8;
        scene.add(plat);

        // ===== Meja Konsol + Orang =====
        function makeStation(x, z, rotY) {
            const g = new THREE.Group();
            const desk = new THREE.Mesh(
                new THREE.BoxGeometry(2, 0.9, 1),
                new THREE.MeshStandardMaterial({ color: 0x0f1c2e, emissive: 0x0a5a7a, emissiveIntensity: 0.5 })
            );
            desk.position.y = -0.55;
            const person = new THREE.Group();
            const body = new THREE.Mesh(
                new THREE.CylinderGeometry(0.22, 0.28, 1.2, 12),
                new THREE.MeshStandardMaterial({ color: Math.random() > 0.5 ? 0x223344 : 0xdddddd })
            );
            body.position.y = 0.2;
            const head = new THREE.Mesh(
                new THREE.SphereGeometry(0.2, 12, 12),
                new THREE.MeshStandardMaterial({ color: 0xd9a77f })
            );
            head.position.y = 1;
            person.add(body, head);
            person.position.set(0, 0, 1);
            g.add(desk, person);
            g.position.set(x, 0, z);
            g.rotation.y = rotY;
            scene.add(g);
        }
        [[-9, -3], [-5, 3], [5, 3], [9, -3], [-2, 7], [3, 8]].forEach(([x, z]) =>
            makeStation(x, z, Math.atan2(-x, -z))
        );

        // ===== Efek Glow (Bloom) =====
        const composer = new THREE.EffectComposer(renderer);
        composer.addPass(new THREE.RenderPass(scene, camera));
        const bloom = new THREE.UnrealBloomPass(
            new THREE.Vector2(window.innerWidth, window.innerHeight), 0.8, 0.6, 0.2
        );
        composer.addPass(bloom);

        // ===== Animasi =====
        function animate() {
            requestAnimationFrame(animate);
            const t = Date.now();

            centralTree.rotation.y += 0.008;
            panels.forEach((p, i) => {
                p.position.y = p.userData.baseY + Math.sin(t * 0.002 + i) * 0.12;
            });
            dome.rotation.y += 0.0005;

            // Kartu skill: melayang, selalu menghadap kamera, membesar saat di-hover
            raycaster.setFromCamera(pointer, camera);
            const hit = raycaster.intersectObjects(skillCards)[0];
            const nowHovered = hit ? hit.object : null;
            if (nowHovered !== hovered) {
                hovered = nowHovered;
                showInfo(hovered ? hovered.userData.item : null);
                renderer.domElement.style.cursor = hovered ? 'pointer' : 'grab';
            }
            skillCards.forEach(m => {
                m.position.y = m.userData.baseY + Math.sin(t * 0.002 + m.userData.phase) * 0.1;
                m.lookAt(camera.position.x, m.position.y, camera.position.z);
                const target = (m === hovered) ? 1.15 : 1;
                m.scale.setScalar(m.scale.x + (target - m.scale.x) * 0.2);
            });

            controls.update();
            composer.render();
        }
        animate();

        // ===== Resize =====
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
            composer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

# Isi placeholder (SOURCE lebih dulu, JSON terakhir agar isi sel tidak ikut terganti)
threejs_code = threejs_code.replace("__SOURCE__", sumber_data).replace(
    "__SKILLS_JSON__", skills_json
)

# Merender Komponen 3D ke dalam Streamlit
components.html(threejs_code, height=800, scrolling=False)
