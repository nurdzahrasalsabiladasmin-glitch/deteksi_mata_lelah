import streamlit as st
import pandas as pd
from datetime import datetime
import os

def catat_ke_dataset(nama_subjek, kondisi_mata, durasi_frame):
    nama_file = "dataset_log_kelelahan.csv"
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Simpan data baru ke dalam list memori RAM dulu (Instan & Bebas Lag)
    log_baru = {
        "Waktu": waktu_sekarang,
        "Nama Subjek": nama_subjek,
        "Status Mata (AI)": kondisi_mata,
        "Consecutive Frames": durasi_frame
    }
    st.session_state.list_log.append(log_baru)
    
    # 2. Tulis langsung ke file CSV fisik untuk backup permanen
    df_baru = pd.DataFrame([log_baru])
    if os.path.exists(nama_file):
        df_baru.to_csv(nama_file, mode='a', header=False, index=False)
    else:
        df_baru.to_csv(nama_file, index=False)