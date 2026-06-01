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
        # Menangkap variabel sektor_names yang baru
        Z, P, Y, X, sektor_names = assemble_modular_io(file_z, file_p, file_y)
        
        # Membuat DataFrame untuk grafik agar sumbu X menggunakan nama sektor
        df_output = pd.DataFrame(X, index=sektor_names, columns=["Total Output"])
        
        st.success("✅ Data berhasil diproses dengan pelabelan sektor!")
        
        st.write("### Grafik Total Output per Sektor")
        # Sekarang grafik akan menampilkan nama sektor di sumbu X
        st.bar_chart(df_output)
        
        st.write("### Data Tabel Output")
        st.dataframe(df_output)
        
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Silakan unggah ketiga berkas CSV (Z, P, dan Y) pada panel di sebelah kiri.")
