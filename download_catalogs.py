import pandas as pd
import requests
import os
from PIL import Image, UnidentifiedImageError

# Baca file Excel
file_path = r'D:\\Aksaramaya\\Cover MCCP\\Tinggalan.xlsx'
df = pd.read_excel(file_path)
df.columns = df.columns.str.replace('\ufeff', '').str.strip()

# Buat folder output
download_folder = r'D:\\Aksaramaya\\Cover MCCP\\Cover Lembata'
os.makedirs(download_folder, exist_ok=True)

# Menyimpan data kegagalan
failed_downloads = []

# Target megapixel
target_mp = 2.0
target_total_pixels = int(target_mp * 1_000_000)

# Loop proses download dan kompres
for index, row in df.iterrows():
    url = row['Cover']
    title = str(row['Id']).strip()

    if pd.notna(url) and pd.notna(title):
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                # Ambil ekstensi dari URL
                file_extension = url.split('.')[-1].split('?')[0].lower()
                if len(file_extension) > 5 or '/' in file_extension:
                    file_extension = 'jpg'  # fallback jika tidak valid

                file_name = f"{title}.{file_extension}"
                file_path_save = os.path.join(download_folder, file_name)

                # Simpan file hasil unduhan
                with open(file_path_save, 'wb') as f:
                    f.write(response.content)

                # Cek file kosong
                if os.path.getsize(file_path_save) == 0:
                    print(f"⚠️ File kosong: {file_name}")
                    failed_downloads.append((title, url, 'File Kosong'))
                    os.remove(file_path_save)
                    continue

                # Validasi dan resize jika perlu
                try:
                    with Image.open(file_path_save) as img:
                        img.load()
                        orig_format = img.format or file_extension.upper()
                        orig_pixels = img.width * img.height

                        # Resize jika melebihi target pixel
                        if orig_pixels > target_total_pixels:
                            scale_factor = (target_total_pixels / orig_pixels) ** 0.5
                            new_width = int(img.width * scale_factor)
                            new_height = int(img.height * scale_factor)
                            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                            print(f"🔧 Resized to {new_width}x{new_height} ({(new_width * new_height)/1_000_000:.2f} MP)")

                        # Simpan ulang hasil resize dan kompresi
                        save_params = {'format': orig_format}
                        if orig_format.upper() in ['JPEG', 'JPG', 'WEBP']:
                            save_params.update({'quality': 60, 'optimize': True})
                        elif orig_format.upper() == 'PNG':
                            save_params.update({'optimize': True, 'compress_level': 9})

                        img.save(file_path_save, **save_params)
                        print(f"✅ Valid & compressed: {file_name}")

                except (UnidentifiedImageError, OSError) as e:
                    print(f"❌ File rusak atau bukan gambar: {file_name}")
                    failed_downloads.append((title, url, 'File corrupt atau bukan gambar'))
                    os.remove(file_path_save)
            else:
                print(f"⚠️ Gagal download {url} (Status: {response.status_code})")
                failed_downloads.append((title, url, f'Status code: {response.status_code}'))
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
            failed_downloads.append((title, url, str(e)))
    else:
        print(f"⚠️ Data tidak lengkap pada baris {index} (URL atau UUID kosong)")
        failed_downloads.append((title, url, 'URL atau UUID kosong'))

# Simpan log kegagalan jika ada
if failed_downloads:
    log_file = os.path.join(download_folder, 'failed_downloads.csv')
    pd.DataFrame(failed_downloads, columns=['UUID', 'URL', 'Keterangan']).to_csv(log_file, index=False)
    print(f"\n📄 Log kegagalan disimpan di: {log_file}")
