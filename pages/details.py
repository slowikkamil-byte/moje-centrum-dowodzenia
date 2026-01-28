import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import json

# 1. Autoryzacja
def get_gdrive_service():
    try:
        info = json.loads(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(info)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Błąd kluczy: {e}")
        return None

# 2. Funkcja wysyłki z ominięciem limitów konta usługi
def upload_to_gdrive(file, client_name):
    try:
        service = get_gdrive_service()
        if not service: return None
        
        folder_id = st.secrets["drive_folder_id"]
        
        file_metadata = {
            'name': f"{client_name}_{file.name}",
            'parents': [folder_id]
        }
        
        # Przygotowanie danych pliku
        buffer = io.BytesIO(file.getvalue())
        
        # resumable=False jest kluczowe dla darmowych kont, aby uniknąć błędu 403
        media = MediaIoBaseUpload(buffer, mimetype=file.type, resumable=False)
        
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True,
            ignoreDefaultVisibility=True
        ).execute()
        
        return uploaded_file.get('id')
    except Exception as e:
        st.error(f"Google nadal blokuje zapis: {e}")
        return None

# --- UI APLIKACJI ---

if 'selected_client' not in st.session_state:
    st.warning("⚠️ Nie wybrano klienta!")
    if st.button("⬅️ Powrót"): st.switch_page("main.py")
    st.stop()

client = st.session_state['selected_client']
client_name = str(client.iloc[0])

st.title(f"👤 {client_name}")
st.caption(f"📍 {client.iloc[3]} | 📞 {client.iloc[6]}")
st.divider()

# SEKCJA WYCENY
st.subheader("📝 Notatki")
note = st.text_area("Twoje uwagi (zapis lokalny w sesji):", placeholder="Wpisz notatkę...")

# SEKCJA MULTIMEDIÓW
st.markdown("### 📸 Zdjęcia i Nagrania")
uploaded_files = st.file_uploader(
    "Wgraj pliki", 
    type=['jpg', 'png', 'jpeg', 'mp3', 'wav', 'm4a'], 
    accept_multiple_files=True,
    label_visibility="collapsed"
)

if uploaded_files:
    cols = st.columns(3)
    for idx, f in enumerate(uploaded_files):
        with cols[idx % 3]:
            if f.type.startswith('image'):
                st.image(f, use_container_width=True)
            else:
                st.audio(f)

st.divider()

col_save, col_back = st.columns(2)

with col_save:
    if st.button("💾 ZAPISZ NA DYSKU", use_container_width=True):
        if not uploaded_files:
            st.warning("Dodaj plik, aby przetestować zapis.")
        else:
            with st.spinner("Przesyłam..."):
                success_count = 0
                for f in uploaded_files:
                    file_id = upload_to_gdrive(f, client_name)
                    if file_id:
                        success_count += 1
                
                if success_count > 0:
                    st.success(f"✅ Sukces! Pliki na dysku: {success_count}")
                    st.balloons()

with col_back:
    if st.button("⬅️ POWRÓT", use_container_width=True):
        st.switch_page("main.py")

with st.expander("📄 Dane klienta"):
    st.write(client)
