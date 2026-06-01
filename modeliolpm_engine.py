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
    Merakit matriks Z (Transaksi), P (Input Primer), dan Y (Permintaan Akhir).
    """
    df_z, Z_df = clean_and_load(file_z)
    df_p, P_df = clean_and_load(file_p)
    df_y, Y_df = clean_and_load(file_y)
    
    # Validasi dimensi dasar
    if Z_df.shape[0] != P_df.shape[1] or Z_df.shape[0] != Y_df.shape[0]:
        raise ValueError(f"Ketidakcocokan dimensi! Z:{Z_df.shape}, P:{P_df.shape}, Y:{Y_df.shape}")
    
    # Konversi ke NumPy Array
    Z = Z_df.values
    P = P_df.values
    Y = Y_df.values
    
    # Menghitung Total Output (X)
    # X = (Sum baris Z) + (Sum baris Y)
    X = Z.sum(axis=1) + Y.sum(axis=1)
    
    return Z, P, Y, X
