import streamlit as st
import cv2
import math
import mediapipe as mp
import time

# =====================================================================
# 1. CLASS PENGOLAH WAJAH (DIPINDAHKAN KE SINI AGAR TIDAK ERROR IMPORT)
# =====================================================================
class PengolahWajah:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1, 
            refine_landmarks=True
        )

    def hitung_jarak(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    def hitung_ear(self, landmarks, top_bottom_idx, left_right_idx):
        p_top = landmarks[top_bottom_idx[0]]
        p_bottom = landmarks[top_bottom_idx[1]]
        p_left = landmarks[left_right_idx[0]]
        p_right = landmarks[left_right_idx[1]]
        
        vertikal = self.hitung_jarak(p_top, p_bottom)
        horizontal = self.hitung_jarak(p_left, p_right)
        return vertikal / horizontal

    def deteksi_landmarks(self, rgb_frame):
        return self.face_mesh.process(rgb_frame)

# =====================================================================
# 2. KONFIGURASI NILAI AMBANG BATAS (THRESHOLD) BROWSER
# =====================================================================
EAR_THRESHOLD = 0.23        # Batas mata dikatakan merem/lelah
CONSECUTIVE_FRAMES = 10     # Harus merem selama 10 frame berturut-turut

# Indeks koordinat titik mata untuk Mediapipe Face Mesh
LEFT_EYE_TOP_BOTTOM = [159, 145]
LEFT_EYE_LEFT_RIGHT = [33, 133]
RIGHT_EYE_TOP_BOTTOM = [386, 374]
RIGHT_EYE_LEFT_RIGHT = [362, 263]

# =====================================================================
# 3. INTERFACE APLIKASI WEB STREAMLIT
# =====================================================================
st.set_page_config(page_title="Pendeteksi Mata Lelah", layout="centered")
st.title("👁️ Web Aplikasi Pendeteksi Mata Lelah")
st.write("Aplikasi berbasis web untuk memantau tingkat kelelahan mata Anda secara real-time.")

run_app = st.checkbox("Aktifkan Kamera Webcam")
FRAME_WINDOW = st.image([])

# Memanggil class yang berada di file yang sama
pengolah = PengolahWajah()

if 'counter' not in st.session_state:
    st.session_state.counter = 0

# =====================================================================
# 4. PROSES LOGIKA KAMERA LIVE STREAMING
# =====================================================================
if run_app:
    cap = cv2.VideoCapture(0)
    
    while run_app:
        ret, frame = cap.read()
        if not ret:
            st.error("Gagal mengakses webcam. Pastikan kamera tidak sedang dipakai aplikasi lain.")
            break
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        hasil = pengolah.deteksi_landmarks(rgb_frame)
        
        status_teks = "Mata Terbuka (Kondisi Normal)"
        warna_box = (0, 255, 0)  # Hijau (RGB)
        
        if hasil.multi_face_landmarks:
            for face_landmarks in hasil.multi_face_landmarks:
                # Hitung EAR menggunakan indeks koordinat lokal
                ear_kiri = pengolah.hitung_ear(face_landmarks.landmark, LEFT_EYE_TOP_BOTTOM, LEFT_EYE_LEFT_RIGHT)
                ear_kanan = pengolah.hitung_ear(face_landmarks.landmark, RIGHT_EYE_TOP_BOTTOM, RIGHT_EYE_LEFT_RIGHT)
                ear_rata = (ear_kiri + ear_kanan) / 2.0
                
                if ear_rata < EAR_THRESHOLD:
                    st.session_state.counter += 1
                    if st.session_state.counter >= CONSECUTIVE_FRAMES:
                        status_teks = "PERINGATAN: MATA ANDA LELAH!"
                        warna_box = (255, 0, 0)  # Merah (RGB)
                else:
                    st.session_state.counter = 0
                
                # Menggambar teks parameter ke layar web
                cv2.putText(rgb_frame, f"EAR: {ear_rata:.2f}", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(rgb_frame, status_teks, (20, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, warna_box, 2)
        
        FRAME_WINDOW.image(rgb_frame)
        time.sleep(0.01)
        
    cap.release()
else:
    st.info("Silakan centang kotak 'Aktifkan Kamera Webcam' di atas untuk memulai aplikasi.")