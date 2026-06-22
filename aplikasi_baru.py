import streamlit as st
import cv2
import av # Pustaka untuk mengolah frame video WebRTC
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# =====================================================================
# 1. KONFIGURASI HALAMAN & PEMANGGILAN CSS EKSTERNAL
# =====================================================================
st.set_page_config(
    page_title="Pendeteksi Mata Lelah Aesthetic", 
    layout="centered",
    page_icon="🌸"
)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_css("style.css")
except FileNotFoundError:
    st.warning("Catatan: File 'style.css' belum ditemukan di folder yang sama.")

st.markdown("<h1>🌸 AI Eye Fatigue Detector 🌸</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Pantau kesehatan mata indahmu secara real-time dengan asisten AI pribadi</p>", unsafe_allow_html=True)

# =====================================================================
# 2. LAYOUT METRIK INDIKATOR
# =====================================================================
col1, col2 = st.columns(2)

with col1:
    status_placeholder = st.empty()  

with col2:
    frame_placeholder = st.empty()   

st.markdown("<hr>", unsafe_allow_html=True)

run_app = st.checkbox("✨ AKTIFKAN WEBCAM KAMU DI SINI ✨")
st.markdown("<br>", unsafe_allow_html=True)

# Tampilan awal dashboard sebelum kamera aktif
status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px;'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>💖 SIAP MEMANTAU</span></div>", unsafe_allow_html=True)
frame_placeholder.metric(label="⏱️ Durasi Kedipan", value="0 Frame", delta="Menunggu Kamera")

# =====================================================================
# 3. BAGIAN LOGIKA AI DENGAN WEBRTC (Bagian yang Dirombak Total)
# =====================================================================
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Gunakan session_state untuk menyimpan hitungan frame secara global
if 'counter' not in st.session_state:
    st.session_state.counter = 0

CONSECUTIVE_FRAMES = 10 

if run_app:
    # Konfigurasi server STUN publik agar video lancar di internet
    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    # Kelas pengolah video WebRTC pengganti Loop While OpenCV
    class EyeFatigueProcessor:
        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            img = frame.to_ndarray(format="bgr24")
            img = cv2.flip(img, 1) # Efek cermin
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            wajah_deteksi = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            status_teks = "Mata Terbuka (Kondisi Normal)"
            warna_teks_kamera = (147, 105, 255) # Pink
            alert_style = "normal"
            
            for (x, y, w, h) in wajah_deteksi:
                cv2.rectangle(img, (x, y), (x+w, y+h), (180, 105, 255), 3) # Kotak Wajah Pink
                
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
                mata_deteksi = eye_cascade.detectMultiScale(roi_gray, 1.1, 4)
                
                if len(mata_deteksi) < 2:
                    st.session_state.counter += 1
                    if st.session_state.counter >= CONSECUTIVE_FRAMES:
                        status_teks = "PERINGATAN: MATA KAMU LELAH!"
                        warna_teks_kamera = (0, 0, 255) # Merah
                        alert_style = "danger"
                else:
                    st.session_state.counter = 0
                    
                for (ex, ey, ew, eh) in mata_deteksi:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 255, 255), 2) # Kotak Mata Putih
            
            # Perbarui komponen dashboard di halaman web
            if alert_style == "danger":
                status_placeholder.markdown("<div style='background-color:#FFF5F5; padding:15px; border-left:5px solid #FF0000; border-radius:10px;'><b style='color:#991B1B;'>STATUS:</b> <span style='color:#DC2626;'>⚠️ MATA LELAH / MENGANTUK</span></div>", unsafe_allow_html=True)
                frame_placeholder.metric(label="🚨 Durasi Pejam", value=f"{st.session_state.counter} Frame", delta="ISTIRAHAT YUK!", delta_color="inverse")
            else:
                status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px;'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>💖 MATA SEGAR & CANTIK</span></div>", unsafe_allow_html=True)
                frame_placeholder.metric(label="⏱️ Durasi Kedipan", value=f"{st.session_state.counter} Frame", delta="Aman Kak")
            
            cv2.putText(img, status_teks, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, warna_teks_kamera, 2)
            return av.VideoFrame.from_ndarray(img, format="bgr24")

    # Tampilkan perekam video bawaan browser ke halaman web
    webrtc_streamer(
        key="eye-fatigue",
        mode=WebRtcMode.VIDEORECVONLY,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=EyeFatigueProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

else:
    st.markdown("""
        <div style='background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 1px dashed #FFB6C1; color: #6B7280;'>
            <b>🌸 Petunjuk Aplikasi:</b><br>
            Yuk, centang tombol di atas untuk menyalakan webcam-mu! Pastikan wajahmu terlihat cerah di depan kamera agar sistem AI bisa memantau matamu dengan baik ya, Kak.
        </div>
    """, unsafe_allow_html=True)