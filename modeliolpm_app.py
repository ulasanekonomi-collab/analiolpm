import streamlit as st
import pandas as pd
from modeliolpm_engine import assemble_modular_io, calculate_structural_coefficients, calculate_leontief_inverse

st.set_page_config(page_title="Model IOLPM", layout="wide")
st.title("📊 MODEL IOLPM: Konstruksi Data")

st.sidebar.header("📁 Unggah Data")
file_z = st.sidebar.file_uploader("1. Matriks Transaksi (Z)", type=["csv"])
file_p = st.sidebar.file_uploader("2. Input Primer (P)", type=["csv"])
file_y = st.sidebar.file_uploader("3. Permintaan Akhir (Y)", type=["csv"])

if file_z and file_p and file_y:
    try:
        Z, P, Y, X, sektor_names = assemble_modular_io(file_z, file_p, file_y)
        
        # Memanggil fungsi yang tadi sudah diperbaiki
        df_struct = calculate_structural_coefficients(Z, P, Y, X, sektor_names)
        
        st.success("✅ Struktur ekonomi berhasil dianalisis!")
        st.dataframe(df_struct.style.format("{:.2f} %"))
        
        # ... (visualisasi chart) ...

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

# ... (setelah kode pemrosesan Z, P, Y, X) ...

# Memanggil fungsi analisis struktur
df_struct = calculate_structural_coefficients(Z, P, Y, X, sektor_names)

st.write("### 📈 Analisis Struktur Ekonomi Sektoral")
st.write("Tabel di bawah menunjukkan komposisi distribusi output dan struktur biaya input:")
st.dataframe(df_struct.style.format("{:.2f} %"))

# Visualisasi Stacked Bar Chart untuk Input
st.write("### Komposisi Biaya Input per Sektor (Bahan Baku vs Input Primer)")
st.bar_chart(df_struct[["Input: Bahan Baku (%)", "Input: Input Primer (%)"]])

# Visualisasi Stacked Bar Chart untuk Output
# st.write("### Distribusi Output per Sektor (Bahan Baku vs Permintaan Akhir)")
# st.bar_chart(df_struct[["Output: Bahan Baku (%)", "Output: Permintaan Akhir (%)"]])

# ... (setelah pemrosesan Z, P, Y, X) ...

# Panggil fungsi Leontief
A, L = calculate_leontief_inverse(Z, X)

st.write("### 🧮 Analisis Multiplier Output")
st.write("Matriks di bawah menunjukkan dampak total (langsung + tidak langsung) dari kenaikan permintaan 1 unit.")

# Kita buat DataFrame agar rapi
df_L = pd.DataFrame(L, index=sektor_names, columns=sektor_names)

# Tampilkan dengan format heatmap sederhana (highlight nilai tinggi)
st.dataframe(df_L.style.background_gradient(cmap="Blues", axis=None).format("{:.4f}"))

# Opsional: Hitung Output Multiplier (Sum kolom L)
output_multiplier = L.sum(axis=0)
st.write("### 🚀 Multiplier Output per Sektor")
df_mult = pd.DataFrame(output_multiplier, index=sektor_names, columns=["Multiplier"])
st.bar_chart(df_mult)
