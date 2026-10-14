import streamlit as st
import streamlit.components.v1 as components

# Konfigurasi Halaman & Full Screen Layout
st.set_page_config(
    page_title="Perpustakaan 3D Virtual Gemini",
    page_icon="🏛️",
    layout="wide",
)

# Custom CSS untuk Menghilangkan Sidebar, Header, dan Footer Bawaan Streamlit
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
    /* Memperluas area tampilan agar memenuhi layar */
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# HTML & Three.js untuk Merender Ruangan Fisik 3D Interaktif
threejs_code = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; overflow: hidden; background-color: #03070d; font-family: 'Segoe UI', sans-serif; }
        #canvas-container { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; }
        .holo-overlay {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            color: #00f3ff;
            text-shadow: 0 0 15px rgba(0,243,255,0.8);
            pointer-events: none;
            z-index: 10;
        }
        .holo-overlay h1 { margin: 0; font-size: 1.8rem; letter-spacing: 2px; }
        .holo-overlay p { margin: 5px 0 0; color: #8ab4f8; font-size: 0.95rem; }
    </style>
</head>
<body>
    <div class="holo-overlay">
        <h1>🏛️ RUANG PERPUSTAKAAN 3D VIRTUAL GEMINI</h1>
        <p>Evolusi Peta Pengetahuan & Keterampilan • Interaktif 3D Space</p>
    </div>
    <div id="canvas-container"></div>

    <!-- Pustaka Three.js CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // Inisialisasi Scene, Kamera, dan Renderer 3D
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x03070d, 0.03);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 4, 14);

        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        // Pencahayaan Ruangan Neon
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
        scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0x00f3ff, 2.5, 50);
        pointLight.position.set(0, 10, 0);
        scene.add(pointLight);

        // Kubah Raksasa (Dome Kaca Ruangan)
        const domeGeo = new THREE.SphereGeometry(30, 32, 16);
        const domeMat = new THREE.MeshBasicMaterial({ color: 0x1f2937, wireframe: true, transparent: true, opacity: 0.12 });
        const dome = new THREE.Mesh(domeGeo, domeMat);
        scene.add(dome);

        // Lantai Sirkuit Bercahaya
        const gridHelper = new THREE.GridHelper(50, 50, 0x00f3ff, 0x111927);
        gridHelper.position.y = -1;
        scene.add(gridHelper);

        // Pohon Pengetahuan Digital di Tengah Ruangan
        const trunkGeo = new THREE.CylinderGeometry(0.3, 0.9, 7, 8);
        const trunkMat = new THREE.MeshBasicMaterial({ color: 0x00f3ff, wireframe: true });
        const centralTree = new THREE.Mesh(trunkGeo, trunkMat);
        centralTree.position.set(0, 3.5, 0);
        scene.add(centralTree);

        // Panel-Panel Hologram Mengambang (Merepresentasikan Kategori Skill)
        const panels = [];
        const panelData = [
            { title: "Logika & Pemrograman", level: "95%", color: 0x00f3ff, pos: [-6, 3, -4] },
            { title: "Inovasi & Teknologi", level: "90%", color: 0x00ff88, pos: [6, 3, -4] },
            { title: "Kreativitas & Seni", level: "92%", color: 0x9900ff, pos: [-6, 1, 1] },
            { title: "Bahasa & Komunikasi", level: "88%", color: 0xffaa00, pos: [6, 1, 1] }
        ];

        panelData.forEach((data, index) => {
            const panelGeo = new THREE.BoxGeometry(3.6, 1.8, 0.1);
            const panelMat = new THREE.MeshStandardMaterial({ 
                color: data.color, 
                transparent: true, 
                opacity: 0.8,
                emissive: data.color,
                emissiveIntensity: 0.3
            });
            const panel = new THREE.Mesh(panelGeo, panelMat);
            panel.position.set(...data.pos);
            scene.add(panel);
            panels.push(panel);
        });

        // Interaksi Gerakan Kamera Berdasarkan Mouse
        let mouseX = 0, mouseY = 0;
        document.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX - window.innerWidth / 2) * 0.0004;
            mouseY = (e.clientY - window.innerHeight / 2) * 0.0004;
        });

        // Animasi Loop (Pergerakan Objek 3D secara Real-time)
        function animate() {
            requestAnimationFrame(animate);

            // Putar pohon inti digital
            centralTree.rotation.y += 0.008;

            // Efek mengambang pada panel hologram
            panels.forEach((p, idx) => {
                p.position.y += Math.sin(Date.now() * 0.002 + idx) * 0.002;
            });

            // Gerakan halus kamera mengikuti kursor
            camera.position.x += (mouseX * 6 - camera.position.x) * 0.05;
            camera.position.y += (-mouseY * 6 + 4 - camera.position.y) * 0.05;
            camera.lookAt(0, 2, 0);

            renderer.render(scene, camera);
        }
        animate();

        // Penyesuaian Ukuran Layar Otomatis
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

# Merender Komponen 3D ke dalam Streamlit
components.html(threejs_code, height=720, scrolling=False)
