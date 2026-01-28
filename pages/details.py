import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import json

# 1. Funkcja autoryzacji z Google Drive
def get_gdrive_service():
    try:
        # Pobieranie danych z Twoich Secrets w Streamlit Cloud
        info = json.loads(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(info)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Błąd połączenia z Google: {e}")
        return None

# 2. Funkcja wysyłki z poprawką na brak limitu miejsca (Quota)
def upload_to_gdrive(file, client_name):
    try:
        service = get_gdrive_service()
        if not service: return None
        
        folder_id = st.secrets["drive_folder_id"]
        
        # Przygotowanie metadanych pliku
        file_metadata = {
            'name': f"{client_name}_{file.name}",
            'parents': [folder_id]
        }
        
        # Konwersja pliku ze Streamlita na format akceptowany przez Google
        buffer = io.BytesIO(file.getvalue())
        media = MediaIoBaseUpload(buffer, mimetype=file.type, resumable=True)
        
        # KLUCZOWA POPRAWKA: supportsAllDrives=True pozwala na zapis w Twoim folderze
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True 
        ).execute()
        
        return uploaded_file.get('id')
    except Exception as e:
        st.error(f"Szczegółowy błąd wysyłki: {e}")
        return None

# --- INTERFEJS UŻYTKOWNIKA (UI) ---

# Zabezpieczenie przed wejściem bez wybranego klienta
if 'selected_client' not in st.session_state:
    st.warning("⚠️ Brak wybranego klienta. Wróć do listy.")
    if st.button("⬅️ Powrót"):
        st.switch_page("main.py")
    st.stop()

client = st.session_state['selected_client']
client_name = str(client.iloc[0])

# Wyświetlanie nagłówka z danymi klienta
st.title(f"👤 {client_name}")
st.caption(f"📍 {client.iloc[3]} | 📞 {client.iloc[6]}")
st.divider()

# Sekcja 1: Notatka tekstowa
st.subheader("📝 Notatki i Wycena")
note = st.text_area("Twoje uwagi z dachu:", placeholder="Np. wymiary, stan rynien, wycena...")

# Sekcja 2: Multimedia (Zdjęcia/Głos)
st.markdown("### 📸 Multimedia")
st.caption("Dodaj zdjęcia dokumentów, dachu lub nagraj notatkę głosową.")
uploaded_files = st.file_uploader(
    "Wybierz pliki", 
    type=['jpg', 'png', 'jpeg', 'mp3', 'wav', 'm4a'], 
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# Podgląd wybranych plików przed wysłaniem
if uploaded_files:
    cols = st.columns(3)
    for idx, f in enumerate(uploaded_files):
        with cols[idx % 3]:
            if f.type.startswith('image'):
                st.image(f, use_container_width=True)
            else:
                st.audio(f)

st.divider()

# Sekcja 3: Przyciski akcji
col_save, col_back = st.columns(2)

with col_save:
    if st.button("💾 ZAPISZ WSZYSTKO", use_container_width=True):
        if not uploaded_files and not note:
            st.warning("Dodaj notatkę lub chociaż jedno zdjęcie!")
        else:
            with st.spinner("Przesyłam dane do Twojego folderu Google Drive..."):
                success_count = 0
                if uploaded_files:
                    for f in uploaded_files:
                        file_id = upload_to_gdrive(f, client_name)
                        if file_id:
                            success_count += 1
                
                # Sukces
                if success_count > 0 or note:
                    st.success(f"✅ Gotowe! Wysłano plików: {success_count}")
                    if note:
                        st.info("Notatka została przygotowana do zapisu (wkrótce połączymy z Arkuszem).")
                    st.balloons()

with col_back:
    if st.button("⬅️ POWRÓT DO LISTY", use_container_width=True):
        st.switch_page("main.py")

# Opcjonalny wgląd w pełne dane klienta
with st.expander("📄 Zobacz pełną kartę klienta"):
    st.write(client)
