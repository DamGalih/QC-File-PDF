import pandas as pd
import requests
import os

# === Konfigurasi ===
excel_path = r'D:\\Aksaramaya\\Cover MCCP\\Download PDF.xlsx'
output_folder = r'D:\\Aksaramaya\\Cover MCCP\\PDF_Output'
timeout_seconds = 60

# === Persiapan ===
df = pd.read_excel(excel_path)
df.columns = df.columns.str.replace('\ufeff', '').str.strip()
os.makedirs(output_folder, exist_ok=True)
failed_downloads = []

# === Proses Download PDF ===
for index, row in df.iterrows():
    url = row['PDF'] if 'PDF' in row else row.get('URL')
    title = str(row['Nama']).strip()

    if pd.notna(url) and pd.notna(title):
        try:
            response = requests.get(url, stream=True, timeout=timeout_seconds)
            if response.status_code == 200:
                file_name = f"{title}.pdf"
                path_save = os.path.join(output_folder, file_name)

                with open(path_save, 'wb') as f:
                    f.write(response.content)

                if os.path.getsize(path_save) == 0:
                    print(f"⚠️ File kosong: {file_name}")
                    failed_downloads.append((title, url, 'File kosong'))
                    os.remove(path_save)
                    continue

                print(f"✅ Downloaded: {file_name} ({os.path.getsize(path_save)/1024:.1f} KB)")

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
