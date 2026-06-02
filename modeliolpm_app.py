import streamlit as st
import pandas as pd
import altair as alt
import io
from modeliolpm_engine import (
    assemble_modular_io, 
    calculate_structural_coefficients, 
    calculate_leontief_inverse, 
    calculate_linkages,
    calculate_output_change  # <--- 
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

        # --- D. FITUR SIMULASI PERUBAHAN OUTPUT (Delta X = L * Delta Y) ---
        st.sidebar.markdown("---")
        st.sidebar.header("🚀 Skenario Simulasi ($\Delta Y$)")
        sim_sectors = st.sidebar.multiselect("Pilih Sektor yang Alami Perubahan:", sektor_names)
        
        delta_Y_dict = {}
        n_sektor = len(sektor_names)
        
        if sim_sectors:
            st.sidebar.write("Masukkan Nilai Perubahan ($\Delta Y$):")
            for s in sim_sectors:
                # User memasukkan nilai absolut perubahan permintaan akhir
                val = st.sidebar.number_input(f"Tambahan Nilai untuk {s}:", value=0.0, step=10.0)
                delta_Y_dict[sektor_names.index(s)] = val
        
        if st.sidebar.button("Jalankan Simulasi"):
            if not delta_Y_dict:
                st.warning("Silakan pilih sektor dan tentukan nilai $\Delta Y$ terlebih dahulu!")
            else:
                # Panggil fungsi murni dari engine
                delta_X, delta_Y = calculate_output_change(L, delta_Y_dict, n_sektor)
                
                # Masukkan hasil ke dalam Pandas Series & DataFrame dengan indeks sektor
                dy_series = pd.Series(delta_Y, index=sektor_names)
                dx_series = pd.Series(delta_X, index=sektor_names)
                
                df_sim_result = pd.DataFrame({
                    "Perubahan Permintaan ($\Delta Y$)": dy_series,
                    "Dampak Output ($\Delta X$)": dx_series
                })
                
                # --- TAMPILKAN HASIL SIMULASI ---
                st.write("### 📈 Hasil Simulasi Perubahan Output ($\Delta X = L \\times \Delta Y$)")
                st.write("Tabel di bawah ini menunjukkan seberapa besar output di setiap sektor harus berubah/bertambah untuk merespon perubahan permintaan akhir:")
                
                st.dataframe(df_sim_result.style.format("{:,.2f}").background_gradient(cmap="Blues", subset=["Dampak Output ($$)"]))
                
                # Tombol Download Hasil Simulasi dalam Excel
                excel_sim = convert_df_to_excel(df_sim_result)
                st.download_button(
                    label="📥 Download Hasil Simulasi (Excel)",
                    data=excel_sim,
                    file_name="hasil_simulasi_output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Visualisasi 10 Sektor dengan Dampak Output Terbesar
                st.write("#### 📊 Top 10 Sektor dengan Dampak Perubahan Output Terbesar")
                st.bar_chart(df_sim_result["Dampak Output ($\Delta X$)"].sort_values(ascending=False).head(10))

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Silakan unggah ketiga file CSV di sidebar untuk memulai analisis.")
