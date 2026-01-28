import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import json

# 1. Funkcja łącząca z Google Drive (korzysta z Twoich Secrets)
def get_gdrive_service():
    try:
        # Odczytujemy JSON z Twoich Secrets
        info = json.loads(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(info)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Błąd autoryzacji Google: {e}")
        return None

# 2. Funkcja wysyłająca plik do konkretnego folderu
def upload_to_gdrive(file, client_name):
    try:
        service = get_gdrive_service()
        if not service: return None
        
        folder_id = st.secrets["drive_folder_id"]
        
        file_metadata = {
            'name': f"{client_name}_{file.name}",
            'parents': [folder_id]
        }
        
        buffer = io.BytesIO(file.getvalue())
        media = MediaIoBaseUpload(buffer, mimetype=file.type, resumable=True)
        
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return uploaded_file.get('id')
    except Exception as e:
        st.error(f"Błąd wysyłki pliku {file.name}: {e}")
        return None

# --- UI APLIKACJI ---

# Sprawdzamy czy użytkownik wszedł tu legalnie (wybrał klienta na Start)
if 'selected_client' not in st.session_state:
    st.warning("⚠️ Nie wybrano klienta. Wróć do strony głównej.")
    if st.button("⬅️ Powrót"):
        st.switch_page("main.py")
    st.stop()

client = st.session_state['selected_client']
client_name = str(client.iloc[0])

# Layout strony
st.title(f"👤 {client_name}")
st.caption(f"📍 {client.iloc[3]} | 📞 {client.iloc[6]}")
st.divider()

# SEKCJA WYCENY
st.subheader("📝 Twoja wycena")
note = st.text_area("Dodatkowe uwagi / notatka z dachu:", placeholder="Opisz co trzeba zrobić...")

# SEKCJA MULTIMEDIÓW
st.markdown("### 📸 Multimedia")
st.caption("Możesz zrobić zdjęcie wyceny na papierze lub nagrać głos (dyktafon).")
uploaded_files = st.file_uploader(
    "Wybierz pliki", 
    type=['jpg', 'png', 'jpeg', 'mp3', 'wav', 'm4a'], 
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# Podgląd plików przed wysyłką
if uploaded_files:
    for f in uploaded_files:
        if f.type.startswith('image'):
            st.image(f, width=200)
        else:
            st.audio(f)

st.divider()

# PRZYCISKI AKCJI
col1, col2 = st.columns(2)

with col1:
    if st.button("💾 ZAPISZ I WYŚLIJ", use_container_width=True):
        if not uploaded_files and not note:
            st.warning("Nic nie dodałeś!")
        else:
            with st.spinner("Wysyłam na Google Drive..."):
                success_count = 0
                if uploaded_files:
                    for f in uploaded_files:
                        file_id = upload_to_gdrive(f, client_name)
                        if file_id:
                            success_count += 1
                
                # Tutaj możesz dodać zapisywanie 'note' do Arkusza Google
                
                st.success(f"✅ Zapisano pomyślnie! Wysłano plików: {success_count}")
                st.balloons()

with col2:
    if st.button("❌ ANULUJ", use_container_width=True):
        st.switch_page("main.py")

# Opcjonalne: pełny podgląd danych z Arkusza
with st.expander("📄 Zobacz wszystkie dane klienta"):
    st.write(client)
