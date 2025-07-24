import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

def list_files_to_excel(folder_id, output_file='drive_links_only.xlsx'):
    try:
        service = get_drive_service()
        file_data = []
        page_token = None
        total = 0

        while True:
            response = service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageSize=1000,
                pageToken=page_token
            ).execute()

            for file in response.get('files', []):
                file_data.append({
                    'nama_file': file['name'],
                    'link_view': f"https://drive.google.com/file/d/{file['id']}/view"
                })
                total += 1
                if total % 1000 == 0:
                    print(f"🔄 {total} file tercatat...")

            page_token = response.get('nextPageToken', None)
            if not page_token:
                break

        df = pd.DataFrame(file_data)
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✅ Total {total} file berhasil disimpan ke: {output_file}")

    except HttpError as error:
        print(f"❌ Terjadi kesalahan: {error}")

# Ganti dengan folder ID kamu
folder_id = '17TN5QcoC55F7Ue7Y6oOX2Ph6v3Nd5TqW'
list_files_to_excel(folder_id)
