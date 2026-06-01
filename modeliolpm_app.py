import streamlit as st
import pandas as pd
import altair as alt
import io
from modeliolpm_engine import (
    assemble_modular_io_from_df, 
    calculate_structural_coefficients, 
    calculate_leontief_inverse, 
    calculate_linkages
)

# Fungsi bantuan untuk membaca CSV agar kita tahu list barisnya
def load_csv_preview(file_obj):
    # Menggunakan index_col=0 supaya kolom pertama otomatis jadi index (label baris)
    return pd.read_csv(file_obj, sep=None, engine='python', index_col=0)

# Fungsi untuk konversi ke Excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=True, sheet_name='Hasil')
    return output.getvalue()

st.set_page_config(page_title="Model IOLPM - Mapping", layout="wide")
st.title("📊 MODEL IOLPM: Pemetaan Data (Mapping)")

st.sidebar.header("📁 Unggah Data")
file_z = st.sidebar.file_uploader("1. Matriks Transaksi (Z)", type=["csv"])
file_p = st.sidebar.file_uploader("2. Input Primer (P)", type=["csv"])
file_y = st.sidebar.file_uploader("3. Permintaan Akhir (Y)", type=["csv"])

if file_z and file_p and file_y:
    # 1. Baca dulu filenya untuk lihat isinya
    df_z = load_csv_preview(file_z)
    df_p = load_csv_preview(file_p)
    df_y = load_csv_preview(file_y)

    st.write("### 🛠️ Mapping Variabel")
    st.info("Pilih baris yang sesuai dengan kategori di bawah:")
    
    col1, col2 = st.columns(2)
    # Mapping untuk Input Primer (P)
    with col1:
        st.subheader("Input Primer (P)")
        map_rt = st.selectbox("Pilih baris Pendapatan Rumah Tangga:", df_p.index)
        map_pajak = st.selectbox("Pilih baris Pajak:", df_p.index)
        map_surplus = st.selectbox("Pilih baris Surplus Usaha:", df_p.index)
        map_impor = st.selectbox("Pilih baris Impor:", df_p.index)
    
    with col2:
        st.subheader("Permintaan Akhir (Y)")
        # Contoh jika ingin user memilih kolom tertentu untuk Permintaan Akhir
        map_y = st.multiselect("Pilih kolom Permintaan Akhir:", df_y.columns, default=df_y.columns.tolist())

    if st.button("Proses Analisis"):
        try:
            # 2. Filter data berdasarkan pilihan user
            P_filtered = df_p.loc[[map_rt, map_pajak, map_surplus, map_impor]]
            Y_filtered = df_y[map_y]
            
            # 3. Panggil Engine (Data yang sudah difilter dikirim ke engine)
            Z, P, Y, X = assemble_modular_io_from_df(df_z, P_filtered, Y_filtered)
            
            # 4. Lanjut Analisis (Leontief, Linkage, dsb)
            A, L = calculate_leontief_inverse(Z, X)
            df_linkages = calculate_linkages(L, df_z.index) # Pakai label dari Z
            
            st.success("✅ Data berhasil dipetakan dan dianalisis!")
            
            # --- TAMPILAN DASHBOARD ---
            st.write("### 📊 Analisis Keterkaitan Sektoral (Linkage)")
            st.dataframe(df_linkages.style.format("{:.3f}").background_gradient(cmap="Greens"))
            
            # Tombol Download
            st.download_button("📥 Download Linkages (Excel)", convert_df_to_excel(df_linkages), "linkage.xlsx")
            
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses: {e}")

else:
    st.info("Silakan unggah ketiga file CSV di sidebar untuk memulai proses mapping.")
