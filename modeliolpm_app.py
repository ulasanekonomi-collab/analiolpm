import streamlit as st
import pandas as pd
import altair as alt
import io
from modeliolpm_engine import (
    assemble_modular_io, 
    calculate_structural_coefficients, 
    calculate_leontief_inverse, 
    calculate_linkages
)

# Fungsi untuk konversi ke Excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=True, sheet_name='Hasil Analisis')
    return output.getvalue()

st.set_page_config(page_title="Model IOLPM", layout="wide")
st.title("📊 ANALISIS MODEL INPUT-OUTPUT")

st.sidebar.header("📁 Unggah Data")
file_z = st.sidebar.file_uploader("1. Matriks Transaksi (Z)", type=["csv"])
file_p = st.sidebar.file_uploader("2. Input Primer (P)", type=["csv"])
file_y = st.sidebar.file_uploader("3. Permintaan Akhir (Y)", type=["csv"])
# Tambahkan ini di bagian bawah sidebar
st.sidebar.markdown("---")  # Garis pemisah
st.sidebar.markdown("Model Input-Output")
st.sidebar.markdown("Dikembangkan oleh Wassily Leontief (1941) untuk menganalisis keragaan ekonomi.")

if file_z and file_p and file_y:
    try:
        # 1. Load & Assemble Data (Menggunakan engine stabil)
        Z, P, Y, X, sektor_names = assemble_modular_io(file_z, file_p, file_y)
        
        # 2. Perhitungan Statistik
        df_struct = calculate_structural_coefficients(Z, P, Y, X, sektor_names)
        A, L = calculate_leontief_inverse(Z, X)
        df_linkages = calculate_linkages(L, sektor_names)
        
        # 3. Multiplier Output
        output_multiplier = L.sum(axis=0)
        df_mult = pd.DataFrame(output_multiplier, index=sektor_names, columns=["Multiplier"])
        
        # --- TAMPILAN DASHBOARD ---
        st.success("✅ Data berhasil dianalisis!")
        
        # A. Tabel Linkages
        st.write("### 📊 Multiplier Output, Forward & Backward Linkage")
        st.dataframe(df_linkages.style.format("{:.3f}").background_gradient(cmap="Greens"))
        
        excel_linkages = convert_df_to_excel(df_linkages)
        st.download_button(
            label="📥 Download (Excel)",
            data=excel_linkages,
            file_name="analisis_linkages.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # B. Struktur Ekonomi
        st.write("### 📈 Struktur Ekonomi")
        st.dataframe(df_struct.style.format("{:.2f} %"))
        
        excel_struct = convert_df_to_excel(df_struct)
        st.download_button(
            label="📥 Download Struktur Ekonomi (Excel)",
            data=excel_struct,
            file_name="struktur_ekonomi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # C. Grafik Multiplier (Lollipop Chart)
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

# --- Footer Sidebar ---
st.sidebar.markdown("---") 

# 1. Menampilkan Logo (Pastikan file unisba_logo.png ada di folder yang sama)
st.sidebar.image("logounisba.png", width=100)

# 2. Menampilkan teks dengan spasi rapat (menggunakan HTML)
st.sidebar.markdown("""
    <div style="line-height: 1.0;">
        <p style="margin-bottom: 5px;">Dikembangkan oleh:</p>
        <p style="margin-bottom: 5px;"><strong>Yuhka Sundaya</strong></p>
        <p>Ekonomi Pembangunan Unisba</p>
    </div>
""", unsafe_allow_html=True)

def simulate_demand_shock(L, Y, sector_index, percentage_increase):
    """
    Simulasi kenaikan permintaan akhir pada sektor tertentu.
    L: Invers Leontief
    Y: Vektor Permintaan Akhir (asli)
    sector_index: indeks sektor yang disimulasi
    percentage_increase: nilai persentase (misal 10 untuk 10%)
    """
    # 1. Buat salinan Y agar data asli tidak berubah
    Y_new = Y.copy()
    
    # 2. Terapkan Shock: Y_new = Y * (1 + percent/100)
    # Kita asumsikan shock hanya pada baris sektor_index
    Y_new[sector_index] = Y[sector_index] * (1 + (percentage_increase / 100))
    
    # 3. Hitung X baru: X_new = L * Y_new
    X_new = L.dot(Y_new)
    
    return X_new, Y_new
