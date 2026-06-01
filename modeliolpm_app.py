import streamlit as st
import pandas as pd
import altair as alt
import io
from modeliolpm_engine import (
    assemble_modular_io, 
    calculate_structural_coefficients, 
    calculate_leontief_inverse, 
    calculate_linkages,
    simulate_demand_shock # Pastikan import ini ada
)

# Fungsi untuk konversi ke Excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=True, sheet_name='Hasil Analisis')
    return output.getvalue()

st.set_page_config(page_title="Model IOLPM", layout="wide")
st.title("📊 MODEL IOLPM: Konstruksi Data & Analisis")

# --- SIDEBAR ---
st.sidebar.header("📁 Unggah Data")
file_z = st.sidebar.file_uploader("1. Matriks Transaksi (Z)", type=["csv"])
file_p = st.sidebar.file_uploader("2. Input Primer (P)", type=["csv"])
file_y = st.sidebar.file_uploader("3. Permintaan Akhir (Y)", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.image("logounisba.png", width=150) # Pastikan file logo ada
st.sidebar.markdown("**Dikembangkan oleh:**")
st.sidebar.markdown("Yuhka Sundaya")
st.sidebar.markdown("*Ekonomi Pembangunan Unisba*")

if file_z and file_p and file_y:
    try:
        # 1. Load & Assemble Data
        Z, P, Y, X, sektor_names = assemble_modular_io(file_z, file_p, file_y)
        
        # 2. Perhitungan Statistik
        df_struct = calculate_structural_coefficients(Z, P, Y, X, sektor_names)
        A, L = calculate_leontief_inverse(Z, X)
        df_linkages = calculate_linkages(L, sektor_names)
        output_multiplier = L.sum(axis=0)
        df_mult = pd.DataFrame(output_multiplier, index=sektor_names, columns=["Multiplier"])
        
        # --- TAMPILAN DASHBOARD UTAMA ---
        st.success("✅ Data berhasil dianalisis!")
        
        # A. Tabel Linkages
        st.write("### 📊 Multiplier Output, Forward & Backward Linkage")
        st.dataframe(df_linkages.style.format("{:.3f}").background_gradient(cmap="Greens"))
        
        excel_linkages = convert_df_to_excel(df_linkages)
        st.download_button("📥 Download Linkages (Excel)", excel_linkages, "linkage.xlsx")
        
        # B. Struktur Ekonomi
        st.write("### 📈 Struktur Ekonomi")
        st.dataframe(df_struct.style.format("{:.2f} %"))
        
        # C. Grafik Multiplier
        st.write("### 🚀 Multiplier Output per Sektor")
        df_chart = df_mult.reset_index().rename(columns={'index': 'Sektor', 'Multiplier': 'Nilai'})
        base = alt.Chart(df_chart).encode(x=alt.X('Sektor', sort='-y', axis=alt.Axis(labelAngle=-45)))
        st.altair_chart(base.mark_rule(color='skyblue').encode(y='Nilai') + base.mark_circle(size=60, color='blue').encode(y='Nilai'), use_container_width=True)

        # --- D. FITUR SIMULASI (Di dalam IF agar aman) ---
        st.sidebar.markdown("---")
        st.sidebar.header("🚀 Simulasi Shock")
        sim_sectors = st.sidebar.multiselect("Pilih Sektor untuk Simulasi:", sektor_names)
        
        shock_dict = {}
        if sim_sectors:
            st.sidebar.write("Input % kenaikan:")
            for s in sim_sectors:
                pct = st.sidebar.number_input(f"{s} (%):", 0.0, 200.0, 10.0, 1.0)
                shock_dict[sektor_names.index(s)] = pct
        
        if st.sidebar.button("Jalankan Simulasi"):
            if not shock_dict:
                st.warning("Pilih sektor dulu!")
            else:
                X_shock, Y_shock = simulate_demand_shock(L, Y, shock_dict)
                # Pakai Series untuk menghindari ValueError
                X_awal = pd.Series(X, index=sektor_names)
                X_akhir = pd.Series(X_shock, index=sektor_names)
                df_sim = pd.DataFrame({"Output Awal": X_awal, "Output Baru": X_akhir, "Selisih": X_akhir - X_awal})
                
                st.write("### 📉 Hasil Simulasi")
                st.dataframe(df_sim.style.format("{:,.0f}"))
                st.bar_chart(df_sim["Selisih"].sort_values(ascending=False).head(10))

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Silakan unggah ketiga file CSV di sidebar untuk memulai analisis.")
