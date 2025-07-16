import pandas as pd
import re
import os

# Pastikan file Excel ada di folder yang sama dengan skrip
file_name = "katalog syalmahat New 2025.xlsx"

# Cek apakah file ada
if not os.path.exists(file_name):
    print(f"❌ File '{file_name}' tidak ditemukan di folder saat ini: {os.getcwd()}")
    exit()

# Load Excel
df = pd.read_excel(file_name, sheet_name="Sheet1", skiprows=10)

# Bersihkan nama kolom
df.columns = df.columns.str.strip()

# Fungsi deteksi jenjang
def deteksi_jenjang(judul):
    if not isinstance(judul, str):
        return None
    judul = judul.lower()

    if re.search(r'\btematik\b|\bsubtema\b|\bkelas [1-6]\b|\bsd\b', judul):
        return 'SD'
    if re.search(r'\bsmp\b|\bkelas (vii|viii|ix|7|8|9)\b|\bipa terpadu\b|\bips terpadu\b', judul):
        return 'SMP'
    if re.search(r'\bsma\b|\bma\b|\bkelas (x|xi|xii|10|11|12)\b|\bmatematika\b|\bfisika\b|\bkimia\b|\bsosiologi\b|\bgeografi\b|\bbahasa indonesia\b|\bbahasa inggris\b|\bekonomi\b|\bpkn\b|\bpai\b|\binformatika\b', judul):
        return 'SMA'
    if re.search(r'\bsmk\b|\bproduktif\b|\bkejuruan\b|\bteknik\b|\bkomputer\b|\bmenggambar teknik\b', judul):
        return 'SMK'
    if re.search(r'\bpengantar\b|\bdasar\b|\bteori\b|\bfilsafat\b|\bhukum\b|\bpsikologi\b', judul):
        return 'Kuliah / Umum'
    
    return 'Tidak Teridentifikasi'

# Terapkan fungsi ke kolom judul
df["Peruntukan"] = df["JUDUL BUKU"].apply(deteksi_jenjang)

# Simpan ke file output
output_name = "hasil_deteksi_jenjang.xlsx"
df.to_excel(output_name, index=False)

print(f"✅ Selesai. Hasil disimpan ke: {output_name}")
