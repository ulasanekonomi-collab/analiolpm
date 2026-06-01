import streamlit as st
import pandas as pd
import altair as alt
# Pastikan semua fungsi diimpor dengan benar
from modeliolpm_engine import (
    assemble_modular_io, 
    calculate_structural_coefficients, 
    calculate_leontief_inverse, 
    calculate_linkages
)

st.set_page_config(page_title="Model IOLPM", layout="wide")
st.title("📊 MODEL IOLPM: Konstruksi Data & Analisis")

st.sidebar.header("📁 Unggah Data")
file_z = st.sidebar.file_uploader("1. Matriks Transaksi (Z)", type=["csv"])
file_p = st.sidebar.file_uploader("2. Input Primer (P)", type=["csv"])
file_y = st.sidebar.file_uploader("3. Permintaan Akhir (Y)", type=["csv"])

# --- AWAL GEMBOK: Semua analisis hanya jalan kalau file sudah ada ---
if file_z and file_p and file_y:
    try:
        # 1. Load & Assemble
        Z, P, Y, X, sektor_names = assemble_modular_io(file_z, file_p, file_y)
        
        # 2. Perhitungan
        df_struct = calculate_structural_coefficients(Z, P, Y, X, sektor_names)
        A, L = calculate_leontief_inverse(Z, X)
        df_linkages = calculate_linkages(L, sektor_names) # <-- Sekarang aman di sini
        
        # 3. Multiplier Output
        output_multiplier = L.sum(axis=0)
        df_mult = pd.DataFrame(output_multiplier, index=sektor_names, columns=["Multiplier"])
        
        # 4. Tampilan Dashboard
        st.success("✅ Data berhasil dianalisis!")
        
        # A. Struktur Ekonomi
        st.write("### 📊 Analisis Keterkaitan Sektoral (Linkage)")
        st.dataframe(df_linkages.style.format("{:.3f}").background_gradient(cmap="Greens"))
        
        # B. Multiplier Output
        st.write("### 🚀 Multiplier Output per Sektor")
        df_chart = df_mult.reset_index().rename(columns={'index': 'Sektor', 'Multiplier': 'Nilai'})
        
        base = alt.Chart(df_chart).encode(
            x=alt.X('Sektor', sort='-y', axis=alt.Axis(labelAngle=-45))
        )
        line = base.mark_rule(color='skyblue').encode(y='Nilai')
        circle = base.mark_circle(size=60, color='blue').encode(y='Nilai')
        st.altair_chart(line + circle, use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {e}")
else:
    st.info("Silakan unggah ketiga file CSV di sidebar untuk memulai analisis.")
# --- AKHIR GEMBOK ---

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
