import pandas as pd
import numpy as np

def clean_and_load(file_obj):
    """
    Membaca CSV, membersihkan spasi internal, dan mengembalikan dataframe asli serta dataframe numerik.
    """
    try:
        # Mencoba pembatas semicolon, jika gagal gunakan koma
        df_raw = pd.read_csv(file_obj, sep=';')
    except:
        df_raw = pd.read_csv(file_obj, sep=',')
    
    # Membersihkan nama kolom
    df_raw.columns = df_raw.columns.str.strip()
    
    # Fungsi pembersih sel
    def clean_cell(x):
        if pd.isna(x): return 0.0
        s = str(x).strip().replace(' ', '').replace(',', '.')
        try:
            return float(s)
        except:
            return 0.0
            
    # Mengambil data angka (kolom ke-3 sampai terakhir)
    df_numeric = df_raw.iloc[:, 2:].map(clean_cell)
    
    return df_raw, df_numeric

def assemble_modular_io(file_z, file_p, file_y):
    """
    Merakit matriks Z, P, dan Y dengan memastikan semua variabel terdefinisi dengan benar.
    """
    # Memanggil fungsi pemuat untuk masing-masing file
    df_z, Z_df = clean_and_load(file_z)
    df_p, P_df = clean_and_load(file_p)
    df_y, Y_df = clean_and_load(file_y)
    
    # Menggunakan df_z, df_p, df_y yang spesifik untuk ekstraksi nama sektor
    sektor_names = df_z.iloc[:, 1].tolist()
    
    # Konversi ke NumPy Array
    Z = Z_df.values
    P = P_df.values
    Y = Y_df.values
    
    # Logika Transpose otomatis jika dimensi tidak sesuai dengan Z
    if P.shape[1] != Z.shape[1] and P.shape[0] == Z.shape[1]:
        P = P.T
    if Y.shape[0] != Z.shape[0]:
        Y = Y.T
    
    # Menghitung Total Output (X)
    X = Z.sum(axis=1) + Y.sum(axis=1)
    
    return Z, P, Y, X
