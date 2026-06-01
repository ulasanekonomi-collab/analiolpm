import numpy as np
import pandas as pd

def process_pure_transaction_matrix(file_path):
    """
    Engine V15: Menggunakan positional indexing (iloc) secara murni.
    Tidak akan pernah terjadi KeyError karena mengabaikan nama label kolom.
    """
    try:
        # Membaca CSV dan mengabaikan header asli agar tidak ada konflik nama kolom
        # Kita buat header baru secara manual
        df = pd.read_csv(file_path, sep=';', header=None, skiprows=1)
    except:
        df = pd.read_csv(file_path, sep=',', header=None, skiprows=1)
    
    # 1. Ambil Nama Sektor (Sektor/Deskripsi selalu di kolom indeks 1)
    # Gunakan iloc untuk posisi, bukan nama
    sektor_names = df.iloc[:, 1].astype(str).str.strip().tolist()
    
    # 2. Ambil Matriks Transaksi (Data angka dimulai dari kolom indeks 2 sampai 18)
    # Kita ambil 17 baris pertama
    Z_raw = df.iloc[0:17, 2:19]
    
    # 3. Fungsi pembersih angka yang lebih aman
    def clean_cell(val):
        try:
            # Ganti spasi, koma jadi titik, lalu float
            return float(str(val).replace(' ', '').replace(',', '.'))
        except:
            return 0.0

    Z_numeric = Z_raw.applymap(clean_cell)
    Z_val = Z_numeric.values.astype(float)
    
    # 4. Kalkulasi
    df_result = pd.DataFrame(Z_val, index=sektor_names[0:17], columns=[str(i) for i in range(1, 18)])
    df_result['TOTAL OUTPUT'] = Z_val.sum(axis=1)
    df_result.loc['TOTAL INPUT'] = list(Z_val.sum(axis=0)) + [Z_val.sum()]
    
    return df_result, Z_val, sektor_names[0:17]
