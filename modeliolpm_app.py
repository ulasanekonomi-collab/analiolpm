import streamlit as st
import pandas as pd
import altair as alt
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

st.write("### 🚀 Multiplier Output per Sektor")

# Mengubah data agar bisa diolah oleh Altair
df_chart = df_mult.reset_index().rename(columns={'index': 'Sektor', 'Multiplier': 'Nilai'})

# Membuat "Lollipop Chart" (Garis Vertikal)
# Garis tipis (stem)
base = alt.Chart(df_chart).encode(
    x=alt.X('Sektor', sort='-y', axis=alt.Axis(labelAngle=-45)) # Label miring agar terbaca
)

line = base.mark_rule(color='skyblue').encode(
    y='Nilai'
)

# Titik (lollipop head)
circle = base.mark_circle(size=60, color='blue').encode(
    y='Nilai'
)

chart = line + circle

st.altair_chart(chart, use_container_width=True)
