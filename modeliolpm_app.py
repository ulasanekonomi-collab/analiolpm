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
        # 1. Panggil fungsi perakitan utama
        Z, P, Y, X, sektor_names = assemble_modular_io(file_z, file_p, file_y)
        
        # 2. Analisis Struktur Ekonomi
        df_struct = calculate_structural_coefficients(Z, P, Y, X, sektor_names)
        
        # 3. Analisis Leontief
        A, L = calculate_leontief_inverse(Z, X)
        
        # 4. Hitung Multiplier (Di sini kita buat df_mult)
        output_multiplier = L.sum(axis=0)
        df_mult = pd.DataFrame(output_multiplier, index=sektor_names, columns=["Multiplier"])
        
        # --- TAMPILAN DASHBOARD ---
        st.success("✅ Data berhasil dianalisis!")
        
        # A. Struktur Ekonomi
        st.write("### 📈 Analisis Struktur Ekonomi Sektoral")
        st.dataframe(df_struct.style.format("{:.2f} %"))
        
        st.write("### Komposisi Biaya Input per Sektor (%)")
        st.bar_chart(df_struct[["Input: Bahan Baku (%)", "Input: Input Primer (%)"]])
        
        # B. Multiplier Output
        st.write("### 🚀 Multiplier Output per Sektor")
        
        # Mengubah data untuk Altair
        df_chart = df_mult.reset_index().rename(columns={'index': 'Sektor', 'Multiplier': 'Nilai'})
        
        base = alt.Chart(df_chart).encode(
            x=alt.X('Sektor', sort='-y', axis=alt.Axis(labelAngle=-45))
        )
        line = base.mark_rule(color='skyblue').encode(y='Nilai')
        circle = base.mark_circle(size=60, color='blue').encode(y='Nilai')
        
        chart = line + circle
        st.altair_chart(chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Terjadi kesalahan : {e}")
else:
    st.info("Silakan unggah ketiga file CSV di sidebar untuk memulai analisis.")

    # Pastikan import sudah mencakup fungsi baru ini
    from modeliolpm_engine import (
        assemble_modular_io, 
        calculate_structural_coefficients, 
        calculate_leontief_inverse, 
        calculate_linkages # <--- Jangan lupa tambah ini
    )

    # ... (setelah kode perhitungan L) ...

    # 3. Analisis Linkages
    df_linkages = calculate_linkages(L, sektor_names)

    st.write("### 📊 Analisis Keterkaitan Sektoral (Linkage)")
    st.write("Nilai > 1 menunjukkan sektor tersebut memiliki keterkaitan di atas rata-rata.")

    # Menampilkan tabel gabungan
    st.dataframe(df_linkages.style.format("{:.3f}").background_gradient(cmap="Greens"))
