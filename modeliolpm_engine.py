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

def calculate_structural_coefficients(Z, P, Y, X, sektor_names):
    """
    Menghitung persentase distribusi output dan struktur input.
    """
    # Pastikan X tidak nol untuk menghindari division by zero
    X_safe = np.where(X == 0, 1, X)
    
    # 1. Analisis Output (Row-wise)
    intermediate_output_share = (Z.sum(axis=1) / X_safe) * 100
    final_demand_share = (Y.sum(axis=1) / X_safe) * 100
    
    # 2. Analisis Input (Column-wise)
    intermediate_input_share = (Z.sum(axis=0) / X_safe) * 100
    primary_input_share = (P.sum(axis=0) / X_safe) * 100
    
    # Gabungkan ke dalam DataFrame untuk kemudahan tampilan
    df_structure = pd.DataFrame({
        "Output: Bahan Baku (%)": intermediate_output_share,
        "Output: Permintaan Akhir (%)": final_demand_share,
        "Input: Bahan Baku (%)": intermediate_input_share,
        "Input: Input Primer (%)": primary_input_share
    }, index=sektor_names)
    
    return df_structure
