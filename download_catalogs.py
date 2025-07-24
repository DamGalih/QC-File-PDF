import pandas as pd
import requests
import os
from PIL import Image, UnidentifiedImageError
from io import BytesIO

# === Konfigurasi ===
excel_path = r'D:\\Aksaramaya\\Cover MCCP\\Download cover.xlsx'
output_folder = r'D:\\Aksaramaya\\Cover MCCP\\Bestari_SISA'
max_size_bytes = 2_000_000  # 1.5 MB

# === Persiapan ===
df = pd.read_excel(excel_path)
df.columns = df.columns.str.replace('\ufeff', '').str.strip()
os.makedirs(output_folder, exist_ok=True)
failed_downloads = []

# === Proses Download & Kompresi ===
for index, row in df.iterrows():
    url = row['Cover']
    title = str(row['Id']).strip()

    if pd.notna(url) and pd.notna(title):
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                file_name = f"{title}.jpg"
                path_save = os.path.join(output_folder, file_name)

                # Simpan unduhan awal
                with open(path_save, 'wb') as f:
                    f.write(response.content)

                if os.path.getsize(path_save) == 0:
                    print(f"⚠️ File kosong: {file_name}")
                    failed_downloads.append((title, url, 'File kosong'))
                    os.remove(path_save)
                    continue

                try:
                    with Image.open(path_save) as img:
                        img.load()

                        # Konversi ke RGB (hindari mode RGBA, P, CMYK)
                        if img.mode not in ('RGB', 'L'):
                            img = img.convert('RGB')

                        temp_buffer = BytesIO()
                        quality = 120

                        # Kompresi bertahap
                        while True:
                            temp_buffer.seek(0)
                            temp_buffer.truncate(0)
                            img.save(temp_buffer, format='JPEG', quality=quality, optimize=True)
                            size = temp_buffer.getbuffer().nbytes
                            if size <= max_size_bytes or quality <= 30:
                                break
                            quality -= 5

                        # Resize kalau masih terlalu besar
                        while size > max_size_bytes:
                            new_w = int(img.width * 0.9)
                            new_h = int(img.height * 0.9)
                            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                            temp_buffer.seek(0)
                            temp_buffer.truncate(0)
                            img.save(temp_buffer, format='JPEG', quality=quality, optimize=True)
                            size = temp_buffer.getbuffer().nbytes

                        with open(path_save, 'wb') as out_file:
                            out_file.write(temp_buffer.getvalue())
                        print(f"✅ Saved JPG <2MB: {file_name} ({size/1024:.1f} KB, q={quality})")

                except (UnidentifiedImageError, OSError):
                    print(f"❌ File rusak/bukan gambar: {file_name}")
                    failed_downloads.append((title, url, 'File rusak/bukan gambar'))
                    os.remove(path_save)

            else:
                print(f"⚠️ Gagal download {url} (Status: {response.status_code})")
                failed_downloads.append((title, url, f'Status: {response.status_code}'))

        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
            failed_downloads.append((title, url, str(e)))
    else:
        print(f"⚠️ Baris {index} tidak lengkap (UUID/URL kosong)")
        failed_downloads.append((title, url, 'UUID/URL kosong'))

# === Simpan log gagal ===
if failed_downloads:
    log_path = os.path.join(output_folder, 'failed_downloads.csv')
    pd.DataFrame(failed_downloads, columns=['UUID', 'URL', 'Keterangan']).to_csv(log_path, index=False)
    print(f"\n📄 Log kegagalan disimpan: {log_path}")
