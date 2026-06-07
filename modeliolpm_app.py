import streamlit as st
import pandas as pd
import altair as alt
import io
from modeliolpm_engine import (
    assemble_modular_io, 
    calculate_structural_coefficients, 
    calculate_leontief_inverse, 
    calculate_linkages,
    calculate_output_change,
    calculate_round_by_round,
    hitung_estimasi_waktu_io  # <--- Sudah ditambahkan ke dalam daftar import engine
)

# Fungsi untuk konversi ke Excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=True, sheet_name='Hasil Analisis')
    return output.getvalue()

st.set_page_config(page_title="Model IOL", layout="wide")
st.title("📊 MODEL INPUT-OUPUT")

# --- SIDEBAR ---
st.sidebar.header("📁 Unggah Data")
file_z = st.sidebar.file_uploader("1. Matriks Transaksi (Z)", type=["csv"])
file_p = st.sidebar.file_uploader("2. Input Primer (P)", type=["csv"])
file_y = st.sidebar.file_uploader("3. Permintaan Akhir (Y)", type=["csv"])

st.sidebar.markdown("---")
st.sidebar.image("logounisba.png", width=75) # Pastikan file logo ada
st.sidebar.markdown("**Dikembangkan oleh:**")
st.sidebar.markdown("Yuhka Sundaya")
st.sidebar.markdown("Ekonomi Pembangunan Unisba")

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
                    "Perubahan Permintaan": dy_series,
                    "Perubahan Output": dx_series
                })
                
                # --- TAMPILKAN HASIL SIMULASI ---
                st.write("### 📈 Hasil Simulasi Perubahan Output ($\Delta X = L' \\times \Delta Y$)")
                st.write("Tabel di bawah ini menunjukkan seberapa besar output di setiap sektor harus berubah/bertambah untuk merespon perubahan permintaan akhir:")
                
                st.dataframe(df_sim_result.style.format("{:,.2f}").background_gradient(cmap="Blues", subset=["Perubahan Output"]))
                
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
                st.bar_chart(df_sim_result["Perubahan Output"].sort_values(ascending=False).head(10))
                
                # --- E. TAMPILAN ROUND-BY-ROUND EFFECT ---
                st.write("---")
                st.write("### 🔁 Analisis Proses Konvergensi (Round-by-Round Effect)")
                st.write("Secara teoritis, nilai **Perubahan Output** akhir dicapai melalui proses stimulasi berantai antar-sektor dari satu putaran transaksi ke putaran berikutnya hingga efeknya habis:")
                
                df_rounds_result = calculate_round_by_round(A, delta_Y_dict, n_sektor)
                
                col_tabel, col_grafik = st.columns([1, 1])
                
                with col_tabel:
                    st.write("**Tabel Akumulasi Dampak per Putaran (Round):**")
                    st.dataframe(df_rounds_result.style.format({
                        "Tambahan Output": "{:,.2f}",
                        "Total Output Akumulasi": "{:,.2f}"
                    }))
                        
                with col_grafik:
                    st.write("**Grafik Peluruhan Efek (Menuju Konvergen):**")
                    st.line_chart(df_rounds_result.set_index("Round")["Tambahan Output"])
                    
                total_iterasi = df_rounds_result["Round"].max()
                st.info(f"💡 **Analisis Makro:** Efek kejutan stimulus ekonomi ini membutuhkan waktu sebanyak **{total_iterasi} putaran transaksi** di dalam pasar sampai dampaknya benar-benar terserap sepenuhnya dan mencapai titik keseimbangan baru.")
                
        # ==========================================================================================
        # ⏱️ ESTIMATOR JEDA WAKTU (MANDIRI & SEJAJAR DI LUAR BLOK TOMBOL SIMULASI LAIN)
        # ==========================================================================================
        st.write("---")
        st.title("⏱️ I-O Time-Lag Estimator")
        st.write("Visualisasi interaktif estimasi waktu penyerapan stimulus ekonomi berdasarkan struktur pasar nyata.")

        # Wadah Form Mandiri agar aman dari re-run behavior
        with st.form(key="form_time_lag_permanen"):
            st.subheader("⚙️ Atur Parameter Waktu Dinamis")
            
            tau_input = st.slider(
                "Jeda Adaptasi Industri (𝜏)", 0.5, 3.0, 1.0, 0.5, 
                help="Rata-rata waktu (bulan) yang dibutuhkan industri untuk merespons pesanan baru."
            )
            
            toleransi_input = st.slider(
                "Target Penyerapan Dampak (%)", 80, 99, 95, 1,
                help="Ambang batas persentase dampak ideal Leontief yang ingin diserap pasar."
            ) / 100.0
            
            submit_hitung = st.form_submit_button(label="🚀 Hitung Estimasi Waktu Efek")

        # Eksekusi logika matematika penjalaran waktu setelah form di-submit
        if submit_hitung:
            import numpy as np
            
            # Merakit vektor delta_Y murni dari data skenario
            delta_Y_vector = np.zeros(n_sektor)
            for idx, value in delta_Y_dict.items():
                delta_Y_vector[idx] = value

            # Memanggil fungsi hitung waktu dari engine.py
            estimasi_waktu, total_round = hitung_estimasi_waktu_io(
                matrix_A=A, 
                matrix_L=L, 
                delta_Y=delta_Y_vector, 
                tau=tau_input, 
                toleransi=toleransi_input
            )
            
            # Tampilkan Panel Hasil Utama
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>Estimasi Waktu Penyerapan Penuh</h3>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; color: #FF4B4B; font-size: 75px;'>{estimasi_waktu:.1f} Bulan</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray;'>Kebijakan investasi membutuhkan waktu sekitar <b>{estimasi_waktu:.1f} bulan</b> untuk mentransmisikan dampak multipliernya melalui {total_round} putaran penyesuaian pasar.</p>", unsafe_allow_html=True)
            st.markdown("---")
            
            # Lembar Justifikasi Ilmiah untuk laporan pengguna
            with st.expander("🔍 Lihat Justifikasi Ilmiah & Basis Rumus (Bahan Laporan)"):
                st.markdown(f"""
                ### Formula yang Digunakan:
                Angka di atas dihitung secara semi-dinamis menggunakan rumus penjalaran waktu:
                $$t = k \\times \\tau$$
                
                Dimana:
                * **$t$ (Estimasi Waktu):** **{estimasi_waktu:.1f} Bulan**
                * **$k$ (Putaran Rantai Pasok):** Ditentukan otomatis oleh komputer sebanyak **{total_round} putaran** hingga dampak kumulatif meluruh dan menyerap **{toleransi_input*100:.0f}%** dari target ideal Invers Leontief.
                * **$\\tau$ (Jeda Adaptasi):** Parameter input yang Anda tentukan sebesar **{tau_input} bulan** per siklus transaksi.
                
                ### Korelasi Teoritis dengan Literatur Akademis:
                * **Dekomposisi Putaran ($k$):** Mengikuti kritik *Kolokontes et al. (2019)*, efek pengganda ekonomi tidak terjadi instan, melainkan menjalar dari dampak langsung (*Direct Effect*) hingga berantai (*Indirect Effects*).
                * **Justifikasi Batas Konvergensi:** Studi komparatif Leontief-Ghosh oleh *Guerra & Sancho (2010)* membuktikan deret putaran pasti akan mengerem (konvergen) karena adanya kebocoran berupa komponen nilai tambah (*Value-Added*).
                * **Justifikasi Waktu Berjalan ($\\tau$):** Pemodelan struktural modern oleh *Pettena & Raberto (2025)* memvalidasi adanya jeda waktu operasional (*time lag*) di dunia nyata bagi korporasi untuk melakukan penyesuaian kapasitas produksi saat terjadi perubahan permintaan.
                """)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Silakan unggah ketiga file CSV di sidebar untuk memulai analisis.")
