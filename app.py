import streamlit as st
import cv2
import math
import base64

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
    pass 

st.markdown("<h1>🌸 Ai Deteksi Mata Kelelahan 🌸</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Pantau kesehatan mata indahmu secara real-time dengan asisten AI pribadi</p>", unsafe_allow_html=True)

# --- TOMBOL PILIHAN MODE APLIKASI ---
st.markdown("<br>", unsafe_allow_html=True)
mode_aplikasi = st.radio(
    "⚙️ **Pilih Mode Jalankan Aplikasi:**",
    ("💻 Mode Laptop Sendiri (Offline)", "🌐 Mode Website Server (Online)"),
    horizontal=True
)
st.markdown("<hr>", unsafe_allow_html=True)

# =====================================================================
# FUNCTION UNTUK MEMUTAR SUARA DI STREAMLIT (ONLINE & OFFLINE)
# =====================================================================
def putar_suara_alarm(file_audio):
    try:
        with open(file_audio, "rb") as f:
            data_audio = f.read()
        b64_audio = base64.b64encode(data_audio).decode()
        # Kode HTML5 untuk memutar audio otomatis secara tersembunyi
        html_audio = f"""
            <audio autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
        """
        st.markdown(html_audio, unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Jika file mp3 belum diunggah, aplikasi tidak akan error

# =====================================================================
# 2. LAYOUT METRIK INDIKATOR (POSISI DI ATAS TOMBOL)
# =====================================================================
col1, col2 = st.columns(2)
with col1:
    status_placeholder = st.empty()  
    status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px;'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>💖 MATA SEGAR & CANTIK</span></div>", unsafe_allow_html=True)

with col2:
    FRAME_WINDOW = st.empty() 

st.markdown("<br>", unsafe_allow_html=True)
run_app = st.checkbox("✨ AKTIFKAN WEBCAM KAMU DI SINI  ✨")
st.markdown("<br>", unsafe_allow_html=True)

# =====================================================================
# 3. SETTING CASCADE CLASSIFIER (OPENCV)
# =====================================================================
@st.cache_resource
def load_cascades():
    face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    return face, eye

face_cascade, eye_cascade = load_cascades()
CONSECUTIVE_FRAMES = 7

if 'counter' not in st.session_state:
    st.session_state.counter = 0

# =====================================================================
# A. JALUR PILIHAN: MODE LAPTOP (OFFLINE)
# =====================================================================
if mode_aplikasi == "💻 Mode Laptop Sendiri (Offline)":
    if run_app:
        cap = cv2.VideoCapture(0)
        while cap.isOpened() and run_app:
            ret, frame = cap.read()
            if not ret:
                st.error("Webcam lokal tidak terdeteksi.")
                break
            
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            wajah_deteksi = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            status_teks = "Mata Terbuka (Kondisi Normal)"
            warna_teks_kamera = (147, 105, 255)
            alert_style = "normal"
            
            for (x, y, w, h) in wajah_deteksi:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (180, 105, 255), 3)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                mata_deteksi = eye_cascade.detectMultiScale(roi_gray, 1.1, 4)
                
                if len(mata_deteksi) < 2:
                    st.session_state.counter += 1
                    if st.session_state.counter >= CONSECUTIVE_FRAMES:
                        status_teks = "PERINGATAN: MATA KAMU LELAH!"
                        warna_teks_kamera = (0, 0, 255)
                        alert_style = "danger"
                else:
                    st.session_state.counter = 0
                    
                for (ex, ey, ew, eh) in mata_deteksi:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 255, 255), 2)
            
            if alert_style == "danger":
                status_placeholder.markdown("<div style='background-color:#FFF5F5; padding:15px; border-left:5px solid #FF0000; border-radius:10px;'><b style='color:#991B1B;'>STATUS:</b> <span style='color:#DC2626;'>⚠️ MATA LELAH</span></div>", unsafe_allow_html=True)
                putar_suara_alarm("alarm.mp3") # <--- Bunyi alarm di mode offline
            else:
                status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px;'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>💖 MATA SEGAR & CANTIK</span></div>", unsafe_allow_html=True)
                
            cv2.putText(frame, status_teks, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, warna_teks_kamera, 2)
            frame_tampil = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame_tampil, use_container_width=True)
        cap.release()

# =====================================================================
# B. JALUR PILIHAN: MODE WEBSITE (ONLINE - WEBRTC)
# =====================================================================
else:
    try:
        import av
        from streamlit_webrtc import webrtc_streamer, WebRtcMode
        
        @st.cache_resource
        def dapatkan_processor():
            class EyeFatigueProcessor:
                def __init__(self):
                    self.local_counter = 0
                    try:
                        with open("alarm.mp3", "rb") as f:
                            self.audio_bytes = f.read()
                        self.b64_audio = base64.b64encode(self.audio_bytes).decode()
                    except FileNotFoundError:
                        self.b64_audio = None

                def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
                    img = frame.to_ndarray(format="bgr24")
                    img = cv2.flip(img, 1)
                    
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    wajah_deteksi = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    status_teks = "Mata Terbuka (Kondisi Normal)"
                    warna_teks_kamera = (255, 105, 180) 
                    
                    for (x, y, w, h) in wajah_deteksi:
                        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 105, 180), 3)
                        roi_gray = gray[y:y+h, x:x+w]
                        roi_color = img[y:y+h, x:x+w]
                        mata_deteksi = eye_cascade.detectMultiScale(roi_gray, 1.1, 4)
                        
                        if len(mata_deteksi) < 2:
                            self.local_counter += 1
                            if self.local_counter >= 7:
                                status_teks = "PERINGATAN: MATA KAMU LELAH!"
                                warna_teks_kamera = (0, 0, 255) 
                        else:
                            self.local_counter = 0
                            
                        for (ex, ey, ew, eh) in mata_deteksi:
                            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 255, 255), 2)
                    
                    cv2.putText(img, status_teks, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, warna_teks_kamera, 2)
                    return av.VideoFrame.from_ndarray(img, format="bgr24")
            
            return EyeFatigueProcessor

        if run_app:
            status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px;'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>🌐 Mode Website Aktif</span></div>", unsafe_allow_html=True)
            
            processor_terpilih = dapatkan_processor()
            with FRAME_WINDOW:
                ctx = webrtc_streamer(
                    key="eye-fatigue-audio-v6", 
                    mode=WebRtcMode.SENDRECV,
                    video_processor_factory=processor_terpilih,
                    media_stream_constraints={"video": True, "audio": False},
                    async_processing=True,
                    desired_playing_state=True
                )
                
                # 🌟 KUNCI PERBAIKAN: Blok 'if ctx.video_processor' harus berada DI SINI 
                # (Masih di dalam blok 'if run_app' dan di dalam 'try')
                if ctx.video_processor:
                    if hasattr(ctx.video_processor, 'local_counter') and ctx.video_processor.local_counter >= 7:
                        status_placeholder.markdown("<div style='background-color:#FFF5F5; padding:15px; border-left:5px solid #FF0000; border-radius:10px;'><b style='color:#991B1B;'>STATUS:</b> <span style='color:#DC2626;'>⚠️ MATA LELAH</span></div>", unsafe_allow_html=True)
                        putar_suara_alarm("alarm.mp3") 
                    else:
                        status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px;'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>💖 MATA SEGAR & CANTIK</span></div>", unsafe_allow_html=True)
                        
    except ModuleNotFoundError:
        st.info("💡 Mode Online siap digunakan.")

# Jika tombol centang belum diaktifkan
if not run_app:
    FRAME_WINDOW.empty()
    st.markdown("""
    <div style='background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 1px dashed #FF69B4; color: #000000;'>
        <p style='text-align: center; color: #C71585;'><b>Silakan aktifkan tombol centang untuk memulai deteksi mata lelah kk cantik. ✨</b></p>
    </div>
    """, unsafe_allow_html=True)