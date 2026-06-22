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

# Fungsi cerdas untuk membaca file style.css yang terpisah tadi
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Panggil file CSS luar
try:
    load_css("style.css")
except FileNotFoundError:
    st.warning("Catatan: File 'style.css' belum ditemukan di folder yang sama.")

# Judul Utama & Deskripsi
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

# Kotak Aktivasi Kamera
run_app = st.checkbox("✨ AKTIFKAN WEBCAM KAMU DI SINI ✨")
st.markdown("<br>", unsafe_allow_html=True)

# Wadah Penampil Video Streaming
FRAME_WINDOW = st.image([])

# =====================================================================
# 3. BAGIAN LOGIKA AI (OpenCV)
# =====================================================================
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

CONSECUTIVE_FRAMES = 10 

if 'counter' not in st.session_state:
    st.session_state.counter = 0

if run_app:
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Gagal mengakses webcam. Pastikan kamera tidak sedang dipakai aplikasi lain ya.")
            break
        
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        wajah_deteksi = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        status_teks = "Mata Terbuka (Kondisi Normal)"
        warna_teks_kamera = (147, 105, 255) # Pink Tua hangat untuk info teks
        alert_style = "normal"       
        
        for (x, y, w, h) in wajah_deteksi:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (180, 105, 255), 3) # Kotak Wajah Pink
            
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
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 255, 255), 2) # Kotak Mata Putih
        
        # Pembaruan Dashboard Real-Time
        # 📌 PEMBARUAN DASHBOARD REAL-TIME & ALARM SUARA
        if alert_style == "danger":
            status_placeholder.markdown("<div style='background-color:#FFF5F5; padding:15px; border-left:5px solid #FF0000; border-radius:10px; box-shadow: 1px 2px 5px rgba(0,0,0,0.05);'><b style='color:#991B1B;'>STATUS:</b> <span style='color:#DC2626;'>⚠️ MATA LELAH / MENGANTUK</span></div>", unsafe_allow_html=True)
            frame_placeholder.metric(label="🚨 Durasi Pejam", value=f"{st.session_state.counter} Frame", delta="ISTIRAHAT YUK!", delta_color="inverse")
            
            # --- TAMBAHAN KODE UNTUK ALARM SUARA ---
            import winsound
            # winsound.Beep(frekuensi_suara, durasi_milidetik)
            # 2000 artinya suara agak melengking cerah, 150 artinya bunyi pendek (tidak bikin kaget)
            winsound.Beep(2000, 150) 
            # --------------------------------------
        else:
            status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px; box-shadow: 1px 2px 5px rgba(0,0,0,0.05);'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>💖 MATA SEGAR & CANTIK</span></div>", unsafe_allow_html=True)
            frame_placeholder.metric(label="⏱️ Durasi Kedipan", value=f"{st.session_state.counter} Frame", delta="Aman Kak cantik dan ganteng")

        cv2.putText(frame, status_teks, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, warna_teks_kamera, 2)
        
        frame_tampil = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(frame_tampil)
        
    cap.release()
else:
    st.markdown("""
        <div style='background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 1px dashed #FFB6C1; color: #6B7280;'>
            <b>🌸 Petunjuk Aplikasi:</b><br>
            Yuk, centang tombol di atas untuk menyalakan webcam-mu! Pastikan wajahmu terlihat cerah di depan kamera agar sistem AI bisa memantau matamu dengan baik ya, Kak.
        </div>
    """, unsafe_allow_html=True)