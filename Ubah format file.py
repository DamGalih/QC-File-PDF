import os
from PIL import Image, UnidentifiedImageError

# --- Konfigurasi ---
input_folder = r'D:\Cover MCCP\Cover'        # Folder asal gambar
output_folder = r'D:\Cover MCCP\Cover Ubah' # Folder simpan hasil konversi
output_format = 'JPEG'                      # Format tujuan: 'PNG', 'WEBP', 'JPEG', dll
output_ext = 'jpg'                          # Ekstensi file tujuan

os.makedirs(output_folder, exist_ok=True)

# --- Proses konversi ---
for file_name in os.listdir(input_folder):
    file_path = os.path.join(input_folder, file_name)

    try:
        with Image.open(file_path) as img:
            img = img.convert("RGB")  # konversi warna (hindari mode CMYK/alpha error)
            base_name = os.path.splitext(file_name)[0]
            new_file = os.path.join(output_folder, f"{base_name}.{output_ext}")
            img.save(new_file, format=output_format, quality=85, optimize=True)
            print(f"✅ Berhasil ubah: {file_name} → {output_format}")
    except UnidentifiedImageError:
        print(f"⚠️ Bukan gambar atau rusak: {file_name}")
    except Exception as e:
        print(f"❌ Error {file_name}: {e}")
