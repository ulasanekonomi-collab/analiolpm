import streamlit as st
from modeliolpm_engine import process_pure_transaction_matrix

st.set_page_config(page_title="Model IOLPM - Data Modular", layout="wide")
st.title("📊 MODEL IOLPM: Layer Konstruksi Data")

# Panel Sidebar untuk Input Modular
st.sidebar.header("📁 Input Data Modular")
st.sidebar.write("Tahap 1: Validasi Matriks Transaksi Antara (Z)")
file_z = st.sidebar.file_uploader("Unggah Matriks Transaksi (Z)", type=["csv"])

if file_z:
    try:
        # Memanggil fungsi yang sesuai dengan engine V15
        df_result, Z_val, sektor_names = process_pure_transaction_matrix(file_z)
        
        st.success("✅ Data berhasil dimuat dan diproses!")
        
        # Ringkasan Audit
        st.write("### Audit Struktur Data")
        st.metric("Dimensi Matriks Z", f"{Z_val.shape[0]}x{Z_val.shape[1]}")
        
        # Menampilkan Tabel Hasil
        st.write("### Matriks Transaksi Antara (Z)")
        st.dataframe(df_result.style.format("{:,.2f}"))
        
        # Visualisasi Total Output
        st.write("### Bar Chart Total Output per Sektor")
        st.bar_chart(df_result['TOTAL OUTPUT'][:-1]) # Mengabaikan baris Total Input
        
    except Exception as e:
        st.error(f"Terjadi kesalahan saat merakit data: {e}")
else:
    st.info("Silakan unggah berkas CSV Matriks Transaksi untuk memulai.")
