import pandas as pd
import numpy as np

def clean_and_load(file_obj):
    """
    Fungsi internal untuk membaca CSV dan membersihkan data.
    """
    try:
        df = pd.read_csv(file_obj, sep=';', header=None, skiprows=1)
    except:
        df = pd.read_csv(file_obj, sep=',', header=None, skiprows=1)
    
    # Fungsi pembersih sel
    def clean_cell(x):
        try:
            return float(str(x).replace(' ', '').replace(',', '.'))
        except:
            return 0.0
            
    # Mengambil data angka (indeks kolom 2 sampai akhir)
    df_numeric = df.iloc[:, 2:].map(clean_cell)
    return df, df_numeric

def assemble_modular_io(file_z, file_p, file_y):
    """
    Fungsi utama untuk merakit data. 
    Memanggil clean_and_load secara internal.
    """
    df_z, Z_df = clean_and_load(file_z)
    df_p, P_df = clean_and_load(file_p)
    df_y, Y_df = clean_and_load(file_y)
    
    # Ekstraksi Nama Sektor (dari kolom indeks 1)
    sektor_names = df_z.iloc[:, 1].astype(str).str.strip().tolist()
    
    # Konversi ke NumPy Array
    Z = Z_df.values
    P = P_df.values
    Y = Y_df.values
    
    # Penyesuaian Dimensi (Transpose jika perlu)
    if P.shape[1] != Z.shape[1] and P.shape[0] == Z.shape[1]: P = P.T
    if Y.shape[0] != Z.shape[0]: Y = Y.T
    
    # Kalkulasi Total Output (X)
    X = Z.sum(axis=1) + Y.sum(axis=1)
    
    return Z, P, Y, X, sektor_names
