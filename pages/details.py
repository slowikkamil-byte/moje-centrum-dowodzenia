import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# 1. Funkcja połączenia
def get_gdrive_service():
    info = json.loads(st.secrets["gcp_service_account"])
    creds = service_account.Credentials.from_service_account_info(info)
    return build('drive', 'v3', credentials=creds)

# 2. Pobieranie zdjęć (szukamy plików zawierających nazwisko klienta w nazwie)
def get_photos(client_name):
    try:
        service = get_gdrive_service()
        f_id = st.secrets["drive_folder_id"]
        query = f"'{f_id}' in parents and name contains '{client_name}'"
        res = service.files().list(q=query, fields="files(id, name, thumbnailLink)").execute()
        return res.get('files', [])
    except:
        return []

# --- UI ---
if 'selected_client' not in st.session_state:
    st.switch_page("main.py")

client = st.session_state['selected_client']
client_name = str(client.iloc[0]) # Zakładam, że nazwisko jest w 1. kolumnie

st.title(f"👤 {client_name}")
st.divider()

# SEKCJA ZDJĘĆ
st.subheader("🖼️ Zdjęcia tego klienta")
photos = get_photos(client_name)
if photos:
    cols = st.columns(3)
    for i, p in enumerate(photos):
        with cols[i % 3]:
            st.image(p['thumbnailLink'].replace('=s220', '=s500'), use_container_width=True)
else:
    st.info("Nie znaleziono jeszcze zdjęć dla tego klienta.")

# PRZYCISK FORMULARZA
st.link_button("➕ DODAJ ZDJĘCIA (FORMULARZ)", "TWOJ_LINK_DO_FORMULARZA", use_container_width=True)

st.divider()

# SEKCJA NOTATKI
st.subheader("📝 Notatka do arkusza")
note = st.text_area("Wpisz uwagi (trafi do kolumny M):")
if st.button("💾 ZAPISZ NOTATKĘ"):
    # Tutaj w przyszłości dodamy funkcję update_sheet(client_name, note)
    st.success("Notatka gotowa do wysłania!")

if st.button("⬅️ POWRÓT"):
    st.switch_page("main.py")
