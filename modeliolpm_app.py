import streamlit as st
from modeliolpm_engine import assemble_modular_io

st.set_page_config(page_title="Model IOLPM - Data Modular", layout="wide")
st.title("📊 MODEL IOLPM: Layer Konstruksi Data Modular")

# Panel Sidebar untuk Input Modular
st.sidebar.header("📁 Unggah Komponen Data")
file_z = st.sidebar.file_uploader("1. Matriks Transaksi (Z)", type=["csv"])
file_p = st.sidebar.file_uploader("2. Input Primer (P)", type=["csv"])
file_y = st.sidebar.file_uploader("3. Permintaan Akhir (Y)", type=["csv"])

if file_z and file_p and file_y:
    try:
        Z, P, Y, X = assemble_modular_io(file_z, file_p, file_y)
        
        st.success("✅ **Struktur Data Berhasil Disinkronisasi!**")
        
        # Ringkasan Audit untuk memastikan tidak ada kesalahan dimensi
        col1, col2, col3 = st.columns(3)
        col1.metric("Dimensi Transaksi (Z)", f"{Z.shape[0]}x{Z.shape[1]}")
        col2.metric("Dimensi Input Primer (P)", f"{P.shape[0]}x{P.shape[1]}")
        col3.metric("Dimensi Permintaan Akhir (Y)", f"{Y.shape[0]}x{Y.shape[1]}")
        
        # Visualisasi sederhana untuk verifikasi awal
        st.write("### Grafik Total Output per Sektor (X)")
        st.bar_chart(X)
        
    except Exception as e:
        st.error(f"🚨 **Kesalahan perakitan data:** {e}")
else:
    st.info("Silakan unggah ketiga berkas CSV (Z, P, dan Y) pada panel di sebelah kiri.")
