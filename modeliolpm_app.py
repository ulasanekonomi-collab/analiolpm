import streamlit as st
import pandas as pd
from modeliolpm_engine import assemble_modular_io

st.set_page_config(page_title="Model IOLPM", layout="wide")
st.title("📊 MODEL IOLPM: Konstruksi Data")

st.sidebar.header("📁 Unggah Data")
file_z = st.sidebar.file_uploader("1. Matriks Transaksi (Z)", type=["csv"])
file_p = st.sidebar.file_uploader("2. Input Primer (P)", type=["csv"])
file_y = st.sidebar.file_uploader("3. Permintaan Akhir (Y)", type=["csv"])

if file_z and file_p and file_y:
    try:
        # Panggil fungsi perakitan
        Z, P, Y, X, sektor_names = assemble_modular_io(file_z, file_p, file_y)
        
        st.success("✅ Data berhasil diproses!")
        
        # Tampilkan Grafik
        df_output = pd.DataFrame(X, index=sektor_names, columns=["Total Output"])
        st.bar_chart(df_output)
        
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
