import streamlit as st
import cv2

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
    pass # Mengabaikan jika CSS belum sefolder saat testing

st.markdown("<h1>🌸 Deteksi Mata Kelelahan 🌸</h1>", unsafe_allow_html=True)
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
# 2. LAYOUT METRIK INDIKATOR
# =====================================================================
col1, col2 = st.columns(2)
with col1:
    status_placeholder = st.empty()  
with col2:
    frame_placeholder = st.empty()   

run_app = st.checkbox("✨ AKTIFKAN WEBCAM KAMU DI SINI ✨")
st.markdown("<br>", unsafe_allow_html=True)

# =====================================================================
# 3. SETTING CASCADE CLASSIFIER (OPENCV)
# =====================================================================
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

CONSECUTIVE_FRAMES = 7
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# =====================================================================
# A. JALUR PILIHAN: MODE LAPTOP (OFFLINE)
# =====================================================================
if mode_aplikasi == "💻 Mode Laptop Sendiri (Offline)":
    FRAME_WINDOW = st.image([]) # Wadah gambar lokal
    
    if run_app:
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
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
                frame_placeholder.metric(label="🚨 Durasi Pejam", value=f"{st.session_state.counter} Frame", delta="ISTIRAHAT YUK!", delta_color="inverse")
                try:
                    import winsound
                    winsound.Beep(2000, 150)
                except:
                    pass
            else:
                status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px;'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>💖 MATA SEGAR & CANTIK</span></div>", unsafe_allow_html=True)
                frame_placeholder.metric(label="⏱️ Durasi Kedipan", value=f"{st.session_state.counter} Frame", delta="Aman Kak")
                
            cv2.putText(frame, status_teks, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, warna_teks_kamera, 2)
            frame_tampil = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame_tampil)
        cap.release()

# =====================================================================
# B. JALUR PILIHAN: MODE WEBSITE (ONLINE - WEBRTC)
# =====================================================================
else:
    try:
        import av
        from streamlit_webrtc import webrtc_streamer, WebRtcMode
        
        if run_app:
            class EyeFatigueProcessor:
                def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
                    img = frame.to_ndarray(format="bgr24")
                    img = cv2.flip(img, 1)
                    
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    wajah_deteksi = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    status_teks = "Mata Terbuka (Kondisi Normal)"
                    warna_teks_kamera = (147, 105, 255)
                    alert_style = "normal"
                    
                    for (x, y, w, h) in wajah_deteksi:
                        cv2.rectangle(img, (x, y), (x+w, y+h), (180, 105, 255), 3)
                        roi_gray = gray[y:y+h, x:x+w]
                        roi_color = img[y:y+h, x:x+w]
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
                        frame_placeholder.metric(label="🚨 Durasi Pejam", value=f"{st.session_state.counter} Frame", delta="ISTIRAHAT YUK!", delta_color="inverse")
                    else:
                        status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px;'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>💖 MATA SEGAR & CANTIK</span></div>", unsafe_allow_html=True)
                        frame_placeholder.metric(label="⏱️ Durasi Kedipan", value=f"{st.session_state.counter} Frame", delta="Aman Kak")
                    
                    cv2.putText(img, status_teks, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, warna_teks_kamera, 2)
                    return av.VideoFrame.from_ndarray(img, format="bgr24")

            webrtc_streamer(
                key="eye-fatigue-hybrid",
                mode=WebRtcMode.SENDRECV,
                video_processor_factory=EyeFatigueProcessor,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
            )
    except ModuleNotFoundError:
        st.info("💡 Mode Online siap digunakan. (Instal `pip install av streamlit-webrtc` jika ingin mencoba mode online di laptop).")

# Jika tombol centang belum diaktifkan
if not run_app:
    st.markdown("""
    <div style='background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 1px dashed #000000; color: #000000;'>
        <p style='text-align: center;'>Silakan aktifkan tombol centang untuk memulai deteksi mata lelah kk cantik dan ganteng.</p>
    </div>
    """, unsafe_allow_html=True) # <-- Perhatikan penutup """ dan tambahan unsafe_allow_html ini!