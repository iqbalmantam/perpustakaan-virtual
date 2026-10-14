import streamlit as st
import streamlit.components.v1 as components

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

# PENTING: r""" (raw string) dipakai supaya "\n" di dalam JavaScript tidak
# berubah menjadi baris baru oleh Python.
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
    </style>
</head>
<body>
    <div class="holo-overlay">
        <h1>🏛️ RUANG PERPUSTAKAAN 3D VIRTUAL GEMINI</h1>
        <p>Peta Pengetahuan &amp; Evolusi Keterampilan • Interaktif 3D Space</p>
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

# Merender Komponen 3D ke dalam Streamlit
components.html(threejs_code, height=800, scrolling=False)
