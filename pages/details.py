import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_gdrive_service():
    try:
        # POBIERANIE BEZ json.loads
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(info)
        return build('drive', 'v3', credentials=creds)
    except:
        return None

def get_photos(client_name):
    service = get_gdrive_service()
    if not service: return []
    try:
        f_id = st.secrets["drive_folder_id"]
        query = f"'{f_id}' in parents and name contains '{client_name}'"
        res = service.files().list(q=query, fields="files(id, name, thumbnailLink, webViewLink)").execute()
        return res.get('files', [])
    except:
        return []

if 'selected_client' not in st.session_state:
    st.switch_page("main.py")

client = st.session_state['selected_client']
client_name = str(client.iloc[0])
client_phone = str(client.iloc[6]) if len(client) > 6 else ""
client_address = str(client.iloc[3]) if len(client) > 3 else ""

st.title(f"👤 {client_name}")
st.caption(f"📍 {client_address}")

col1, col2 = st.columns(2)
with col1:
    st.link_button(f"📞 Zadzwoń: {client_phone}", f"tel:{client_phone}", use_container_width=True)
with col2:
    st.link_button("🗺️ Mapy Google", f"https://www.google.com/maps/search/?api=1&query={client_address}", use_container_width=True)

st.divider()

# Sekcja Zdjęć
st.subheader("🖼️ Zdjęcia")
photos = get_photos(client_name)
if photos:
    cols = st.columns(2)
    for i, p in enumerate(photos):
        with cols[i % 2]:
            st.image(p['thumbnailLink'].replace('=s220', '=s500'), use_container_width=True)
            st.link_button("Otwórz zdjęcie", p['webViewLink'])
else:
    st.info("Brak zdjęć. Dodaj je przez formularz.")

# Przycisk Formularza (Wklej swój link!)
st.link_button("🚀 DODAJ ZDJĘCIA (FORMULARZ)", "TUTAJ_WKLEJ_TWOJ_LINK", use_container_width=True)

st.divider()
with st.expander("📄 Pełne dane z Arkusza"):
    st.write(client)

if st.button("⬅️ POWRÓT"):
    st.switch_page("main.py")
