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
    # P biasanya memiliki dimensi (indikator x sektor), 
    # kita sum di axis 0 untuk mendapatkan total input primer per sektor
    primary_input_share = (P.sum(axis=0) / X_safe) * 100
    
    # Gabungkan ke dalam DataFrame
    df_structure = pd.DataFrame({
        "Output: Bahan Baku (%)": intermediate_output_share,
        "Output: Permintaan Akhir (%)": final_demand_share,
        "Input: Bahan Baku (%)": intermediate_input_share,
        "Input: Input Primer (%)": primary_input_share
    }, index=sektor_names)
    
    return df_structure

def calculate_leontief_inverse(Z, X):
    """
    Menghitung Matriks Koefisien Teknis (A) dan Invers Leontief (L).
    """
    # Menghindari pembagian dengan nol
    X_safe = np.where(X == 0, 1.0, X)
    
    # 1. Hitung Koefisien Teknis (A = Z / X)
    # Z adalah [Sektor x Sektor], X adalah [Sektor]
    A = Z / X_safe
    
    # 2. Matriks Identitas
    I = np.identity(Z.shape[0])
    
    # 3. Hitung (I - A)
    IA = I - A
    
    # 4. Hitung Invers Leontief L = (I - A)^-1
    try:
        L = np.linalg.inv(IA)
    except np.linalg.LinAlgError:
        # Jika matriks tidak bisa di-invers
        L = np.zeros_like(I)
        
    return A, L

def calculate_linkages(L, sektor_names):
    """
    Menghitung Output Multiplier, Backward Linkage (BL), dan Forward Linkage (FL).
    BL: Power of Dispersion
    FL: Sensitivity of Dispersion
    """
    n = L.shape[0] # Jumlah sektor
    
    # 1. Output Multiplier = Sum Kolom L
    col_sums = L.sum(axis=0)
    
    # 2. Rata-rata total matriks L
    avg_total_sum = L.sum() / n
    
    # 3. Backward Linkage (BL) = (Sum Kolom L) / (Rata-rata L)
    BL = col_sums / (L.sum() / n)
    
    # 4. Forward Linkage (FL) = (Sum Baris L) / (Rata-rata L)
    FL = L.sum(axis=1) / (L.sum() / n)
    
    # Gabungkan ke DataFrame
    df_linkages = pd.DataFrame({
        "Output Multiplier": col_sums,
        "Backward Linkage": BL,
        "Forward Linkage": FL
    }, index=sektor_names)
    
    return df_linkages

def assemble_modular_io_from_df(Z_df, P_df, Y_df):
    """
    Fungsi baru: Merakit matriks dari DataFrame yang sudah dipilih/dipetakan oleh User.
    Input: DataFrame yang sudah difilter di app.py
    Output: Z, P, Y, X (dalam format numpy array siap hitung)
    """
    # 1. Konversi DataFrame ke NumPy Array
    Z = Z_df.values.astype(float)
    P = P_df.values.astype(float)
    Y = Y_df.values.astype(float)
    
    # 2. Kalkulasi Total Output (X)
    # X = (Sum baris Z) + (Sum baris Y)
    X = Z.sum(axis=1) + Y.sum(axis=1)
    
    # 3. Kembalikan hasil agar bisa lanjut ke analisis Leontief
    return Z, P, Y, X

def simulate_demand_shock(L, Y, shock_dict):
    """
    Simulasi kenaikan permintaan akhir pada beberapa sektor sekaligus.
    """
    Y_new = Y.copy()
    
    # Terapkan shock
    for idx, pct in shock_dict.items():
        Y_new[idx] = Y[idx] * (1 + (pct / 100))
    
    # Hitung X baru dengan .flatten() agar hasilnya menjadi 1 dimensi (N,)
    X_new = L.dot(Y_new).flatten() 
    
    return X_new, Y_new
