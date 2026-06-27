import streamlit as st
import cv2
import math
import base64
import pandas as pd
import os

# --- IMPORT FUNGSI DARI FILE SEBELAH ---
from database import catat_ke_dataset  

# =====================================================================
# 1. KONFIGURASI HALAMAN WEB STREAMLIT
# =====================================================================
st.set_page_config(
    page_title="AI Deteksi Mata Kelelahan",
    page_icon="👁️",
    layout="wide"
)

# =====================================================================
# 2. INISIALISASI SESSION STATE (PENGAMAN DATA RAM)
# =====================================================================
if 'counter' not in st.session_state:
    st.session_state.counter = 0

if 'list_log' not in st.session_state:
    st.session_state.list_log = []

# =====================================================================
# 3. FUNGSI UNTUK MEMUTAR SUARA ALARM (AUDIO BASE64)
# =====================================================================
def putar_suara_alarm(file_audio):
    if os.path.exists(file_audio):
        with open(file_audio, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

# =====================================================================
# 4. FUNGSI MEMUAT MODEL DETEKSI (PENGAMAN EROR 'face_cascade')
# =====================================================================
@st.cache_resource
def load_cascades():
    face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    return face, eye

face_cascade, eye_cascade = load_cascades()

# =====================================================================
# 5. TAMPILKAN SIDEBAR & PILIHAN MODE APLIKASI
# =====================================================================
st.sidebar.header("👤 Profil Pengguna")
nama_user = st.sidebar.text_input("Masukkan Nama Kamu:", "User_Aesthetic")

st.markdown("<h2 style='text-align: center;'>👁️ AI Sistem Pendeteksi Mata Lelah Real-Time</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

mode_aplikasi = st.radio(
    "⚙️ **Pilih Mode Jalankan Aplikasi:**",
    ("💻 Mode Laptop Sendiri (Offline)", "🌐 Mode Website Server (Online)"),
    horizontal=True
)
st.markdown("<hr>", unsafe_allow_html=True)

CONSECUTIVE_FRAMES = 7

# =====================================================================
# 6. JALUR PILIHAN: MODE LAPTOP (OFFLINE)
# =====================================================================
if mode_aplikasi == "💻 Mode Laptop Sendiri (Offline)":
    
    # Tombol pemicu webcam utama
    run_app = st.checkbox("✨ AKTIFKAN WEBCAM KAMU DI SINI ✨", value=False)
    
    # Wadah untuk menampilkan video & status di halaman web
    FRAME_WINDOW = st.image([])
    status_placeholder = st.empty()
    
    if run_app:
        # Membuka webcam default laptop
        cap = cv2.VideoCapture(0)  
        tabel_placeholder = st.empty() 
        
        while cap.isOpened() and run_app:
            ret, frame = cap.read()
            if not ret:
                st.error("Webcam lokal tidak terdeteksi. Pastikan tidak sedang dipakai aplikasi lain.")
                break
            
            # Membalik gambar agar seperti cermin & mengubah ke skala abu-abu
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Deteksi wajah menggunakan model yang sudah di-load di atas
            wajah_deteksi = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            status_teks = "Mata Terbuka (Kondisi Normal)"
            warna_teks_kamera = (147, 105, 255)
            alert_style = "normal"
            
            # Memproses setiap wajah yang ditemukan
            for (x, y, w, h) in wajah_deteksi:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (180, 105, 255), 3)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                
                # Deteksi mata di area wajah
                mata_deteksi = eye_cascade.detectMultiScale(roi_gray, 1.1, 4)
                
                # Logika hitung frame memejam
                if len(mata_deteksi) < 2:
                    st.session_state.counter += 1
                    if st.session_state.counter >= CONSECUTIVE_FRAMES:
                        status_teks = "PERINGATAN: MATA KAMU LELAH!"
                        warna_teks_kamera = (0, 0, 255)
                        alert_style = "danger"
                        
                        if st.session_state.counter == CONSECUTIVE_FRAMES:
                            catat_ke_dataset(nama_user, "⚠️ MATA LELAH", st.session_state.counter)
                else:
                    if st.session_state.counter >= CONSECUTIVE_FRAMES:
                        catat_ke_dataset(nama_user, "💖 MATA SEGAR", 0)
                    st.session_state.counter = 0
                    
                for (ex, ey, ew, eh) in mata_deteksi:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 255, 255), 2)
            
            # --- UPDATE TAMPILAN INTERFACE DI WEB ---
            if alert_style == "danger":
                status_placeholder.markdown("<div style='background-color:#FFF5F5; padding:15px; border-left:5px solid #FF0000; border-radius:10px;'><b style='color:#991B1B;'>STATUS:</b> <span style='color:#DC2626;'>⚠️ MATA LELAH</span></div>", unsafe_allow_html=True)
                putar_suara_alarm("alarm.mp3") 
            else:
                status_placeholder.markdown("<div style='background-color:#FFF0F5; padding:15px; border-left:5px solid #FF69B4; border-radius:10px;'><b style='color:#C71585;'>STATUS:</b> <span style='color:#FF1493;'>💖 MATA SEGAR & CANTIK</span></div>", unsafe_allow_html=True)
            
            # Menampilkan video ke frame Streamlit
            cv2.putText(frame, status_teks, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, warna_teks_kamera, 2)
            frame_tampil = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame_tampil, use_container_width=True)
            
            # Update tabel live di bawah video
            if st.session_state.list_log:
                df_temp = pd.DataFrame(st.session_state.list_log)
                tabel_placeholder.dataframe(df_temp.tail(5), use_container_width=True)
                
        # Menutup hardware webcam dengan bersih saat tombol di-uncheck
        cap.release()

# =====================================================================
# 7. BLOCK DOWNLOAD DATA SHEET (DI LUAR LOOP KAMERA)
# =====================================================================
st.markdown("---")
st.markdown("### 📥 Download Seluruh Data Sheet")
nama_file = "dataset_log_kelelahan.csv"

if os.path.exists(nama_file):
    df_log = pd.read_csv(nama_file)
    csv_data = df_log.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download File CSV untuk Laporan",
        data=csv_data,
        file_name="data_sheet_mata_lelah.csv",
        mime="text/csv"
    )
else:
    st.info("Belum ada file data sheet yang tersimpan di sistem. Jalankan kamera untuk menguji.")