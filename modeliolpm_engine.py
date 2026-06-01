import pandas as pd
import numpy as np

def clean_and_load(file_obj):
    """
    Membaca CSV, membersihkan spasi internal, dan mengonversi ke angka murni.
    """
    try:
        df = pd.read_csv(file_obj, sep=';')
    except:
        df = pd.read_csv(file_obj, sep=',')
    
    # Menghapus spasi pada nama kolom
    df.columns = df.columns.str.strip()
    
    # Fungsi pembersih sel
    def clean_cell(x):
        if pd.isna(x): return 0.0
        s = str(x).strip().replace(' ', '').replace(',', '.')
        try:
            return float(s)
        except:
            return 0.0
            
    # Mengambil data angka (mengasumsikan kolom 0: Kode, kolom 1: Deskripsi, kolom 2 dst: Angka)
    df_numeric = df.iloc[:, 2:].applymap(clean_cell)
    return df, df_numeric

def assemble_modular_io(file_z, file_p, file_y):
    """
    Merakit matriks Z, P, dan Y dengan logika Auto-Transpose yang fleksibel.
    """
    df_z, Z_df = clean_and_load(file_z)
    df_p, P_df = clean_and_load(file_p)
    df_y, Y_df = clean_and_load(file_y)
    
    # 1. Pastikan Matriks Z (Transaksi) adalah 17x17 (N x N)
    Z = Z_df.values
    
    # 2. Logika Auto-Transpose untuk Input Primer (P)
    # Jika P tidak punya 17 kolom, coba balikkan (Transpose)
    P = P_df.values
    if P.shape[1] != Z.shape[1] and P.shape[0] == Z.shape[1]:
        P = P.T
    
    # 3. Logika Auto-Transpose untuk Permintaan Akhir (Y)
    Y = Y_df.values
    if Y.shape[0] != Z.shape[0]:
        Y = Y.T

    # Validasi Akhir (hanya peringatan, tidak harus mematikan program)
    if Z.shape[0] != P.shape[1] or Z.shape[0] != Y.shape[0]:
        st.warning(f"Audit Dimensi: Z={Z.shape}, P={P.shape}, Y={Y.shape}. Pastikan data sesuai.")
    
    # Menghitung Total Output per sektor (X)
    X = Z.sum(axis=1) + Y.sum(axis=1)
    
    return Z, P, Y, X
