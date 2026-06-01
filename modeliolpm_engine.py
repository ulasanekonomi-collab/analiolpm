import numpy as np
import pandas as pd

def process_pure_transaction_matrix(file_path):
    """
    Engine V14: Pembacaan matriks dinamis (flexible size) dan anti-typo.
    """
    # 1. Membaca data dengan deteksi delimiter otomatis
    try:
        df = pd.read_csv(file_path, sep=';')
    except:
        df = pd.read_csv(file_path, sep=',')
    
    # 2. Menentukan jumlah sektor secara otomatis (N)
    # Kita asumsikan jumlah sektor adalah jumlah baris yang terbaca
    n_sectors = len(df)
    
    # 3. Mengambil Label Baris (Deskripsi) secara posisional (kolom ke-2, indeks 1)
    # Ini menghindari KeyError akibat typo 'Deksripsi' vs 'Deskripsi'
    sektor_names = df.iloc[:, 1].astype(str).str.strip().tolist()
    
    # 4. Mengambil Matriks Angka secara dinamis (kolom ke-3 hingga ke-(N+2))
    # Kita ambil data angka dari kolom ke-3 (indeks 2) sampai sejumlah n_sectors
    Z_raw = df.iloc[:, 2:2+n_sectors]
    
    # Bersihkan data (hapus spasi, ganti koma dengan titik)
    def clean_cell(val):
        if pd.isna(val): return 0.0
        s = str(val).strip().replace(' ', '').replace(',', '.')
        try:
            return float(s)
        except:
            return 0.0
            
    Z_numeric = Z_raw.applymap(clean_cell)
    Z_val = Z_numeric.values.astype(float)
    
    # 5. Kalkulasi Agregat
    df_result = pd.DataFrame(Z_val, index=sektor_names, columns=sektor_names)
    df_result['TOTAL OUTPUT'] = Z_val.sum(axis=1)
    df_result.loc['TOTAL INPUT'] = list(Z_val.sum(axis=0)) + [Z_val.sum()]
    
    return df_result, Z_val, sektor_names
