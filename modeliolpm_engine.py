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
    
    # Bersihkan nama kolom
    df.columns = df.columns.str.strip()
    
    # Fungsi pembersih sel
    def clean_and_load(file_obj):
        """
        Versi Anti-Error: Mengubah data menjadi numerik dengan paksa.
        """
        try:
            df = pd.read_csv(file_obj, sep=';')
        except:
            df = pd.read_csv(file_obj, sep=',')
    
        # Bersihkan nama kolom dari spasi
        df.columns = df.columns.str.strip()
    
        # --- BAGIAN PERBAIKAN DI SINI ---
        # Kita ambil kolom data (mulai kolom ke-3 / indeks 2)
        # pd.to_numeric dengan errors='coerce' akan mengubah teks menjadi NaN
        # fillna(0) mengubah NaN menjadi 0 agar kalkulasi aman
        df_numeric = df.iloc[:, 2:].apply(pd.to_numeric, errors='coerce').fillna(0.0)
    
        return df, df_numeric
            
    # Mengambil data angka (mengasumsikan kolom 0: Kode, kolom 1: Deskripsi, sisanya angka)
    df_numeric = df.iloc[:, 2:].applymap(clean_cell)
    return df, df_numeric

def assemble_modular_io(file_z, file_p, file_y):
    """
    Merakit matriks Z, P, dan Y menjadi struktur tabel IO yang utuh.
    """
    df_z, Z_df = clean_and_load(file_z)
    df_p, P_df = clean_and_load(file_p)
    df_y, Y_df = clean_and_load(file_y)
    
    # Nama sektor diambil dari kolom deskripsi (indeks 1)
    sektor_names = df_z.iloc[:, 1].tolist()
    
    # Konversi ke NumPy Array
    Z = Z_df.values
    P = P_df.values
    Y = Y_df.values
    
    # Menghitung Total Output per sektor (X)
    # Total Output = Row Sum of Z + Row Sum of Y
    X = Z.sum(axis=1) + Y.sum(axis=1)
    
    return Z, P, Y, X, sektor_names
