import pandas as pd
import numpy as np

def load_csv_data(file_obj):
    """
    Fungsi utilitas untuk memuat file CSV dengan logika anti-error.
    """
    try:
        # Mencoba pembatas semicolon, jika gagal gunakan koma
        df = pd.read_csv(file_obj, sep=';', header=None, skiprows=1)
    except:
        df = pd.read_csv(file_obj, sep=',', header=None, skiprows=1)
    
    # Membersihkan sel dari karakter non-numerik
    def clean_cell(x):
        try:
            return float(str(x).replace(' ', '').replace(',', '.'))
        except:
            return 0.0

    # Mengambil data angka (indeks 2 sampai akhir)
    df_numeric = df.iloc[:, 2:].map(clean_cell)
    
    return df, df_numeric

def assemble_modular_io(file_z, file_p, file_y):
    """
    Fungsi utama untuk merakit data modular.
    Menggantikan fungsi process_pure_transaction_matrix yang lama.
    """
    # 1. Load data
    df_z, Z_df = load_csv_data(file_z)
    df_p, P_df = load_csv_data(file_p)
    df_y, Y_df = load_csv_data(file_y)
    
    # 2. Ekstraksi data angka ke NumPy
    Z = Z_df.values
    P = P_df.values
    Y = Y_df.values
    
    # 3. Validasi dan Penyesuaian Dimensi (Auto-Transpose)
    # Memastikan Input Primer dan Permintaan Akhir sesuai dengan dimensi Transaksi (Z)
    if P.shape[1] != Z.shape[1] and P.shape[0] == Z.shape[1]:
        P = P.T
    if Y.shape[0] != Z.shape[0]:
        Y = Y.T
    
    # 4. Kalkulasi Total Output (X)
    # X = (Sum baris Z) + (Sum baris Y)
    X = Z.sum(axis=1) + Y.sum(axis=1)
    
    # 5. Mengembalikan hasil untuk digunakan di app.py
    return Z, P, Y, X
