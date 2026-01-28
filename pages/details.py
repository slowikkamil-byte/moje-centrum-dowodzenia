import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# 1. Funkcja autoryzacji do Google Drive (do podglądu zdjęć)
def get_gdrive_service():
    try:
        info = json.loads(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(info)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        return None

# 2. Pobieranie zdjęć z folderu formularza
def get_photos(client_name):
    try:
        service = get_gdrive_service()
        if not service: return []
        
        f_id = st.secrets["drive_folder_id"]
        # Szukamy plików, które mają w nazwie nazwisko klienta
        query = f"'{f_id}' in parents and name contains '{client_name}'"
        res = service.files().list(q=query, fields="files(id, name, thumbnailLink, webViewLink)").execute()
        return res.get('files', [])
    except Exception as e:
        return []

# --- LOGIKA SESJI ---
if 'selected_client' not in st.session_state:
    st.warning("⚠️ Nie wybrano klienta. Wróć do strony głównej.")
    if st.button("⬅️ Powrót"):
        st.switch_page("main.py")
    st.stop()

# Dane klienta z sesji
client = st.session_state['selected_client']
# Zakładam Twoją strukturę kolumn (możesz skorygować indeksy jeśli trzeba)
client_name = str(client.iloc[0])  # Kolumna A: Nazwisko/Firma
client_phone = str(client.iloc[6]) # Kolumna G: Telefon
client_address = str(client.iloc[3]) # Kolumna D: Adres
client_status = str(client.iloc[10]) # Kolumna K: Status

# --- UI APLIKACJI ---

# Nagłówek
st.title(f"👤 {client_name}")
st.subheader(f"📍 {client_address}")

# Szybkie akcje
col_tel, col_maps = st.columns(2)
with col_tel:
    st.link_button(f"📞 Zadzwoń: {client_phone}", f"tel:{client_phone}", use_container_width=True)
with col_maps:
    st.link_button("🗺️ Nawiguj", f"https://www.google.com/maps/search/?api=1&query={client_address}", use_container_width=True)

st.divider()

# SEKCJA 1: SZCZEGÓŁOWE DANE Z ARKUSZA
with st.expander("📄 Pełne dane z bazy", expanded=False):
    st.write(client)

st.divider()

# SEKCJA 2: WYCENA I NOTATKI
st.subheader("📝 Notatki i Wycena")
# Tutaj użytkownik wpisuje to, co ustalił na dachu
note = st.text_area("Wpisz ustalenia, wymiary, kwotę:", placeholder="Np. Dach 150m2, dachówka ceramiczna, cena: 5000zł...")

if st.button("💾 ZAPISZ NOTATKĘ", use_container_width=True):
    # To zapisuje notatkę tymczasowo, dopóki nie dodamy funkcji zapisu do Arkusza (Sheet)
    st.session_state[f"note_{client_name}"] = note
    st.success("Notatka zapamiętana w sesji!")

st.divider()

# SEKCJA 3: MULTIMEDIA (PODGLĄD + DODAWANIE)
st.subheader("📸 Zdjęcia i Multimedia")

# Podgląd już istniejących zdjęć
with st.spinner("Ładowanie zdjęć z dysku..."):
    photos = get_photos(client_name)
    if photos:
        cols = st.columns(2)
        for idx, p in enumerate(photos):
            with cols[idx % 2]:
                # Wyświetlamy miniaturkę i dodajemy link do pełnego zdjęcia
                st.image(p['thumbnailLink'].replace('=s220', '=s500'), use_container_width=True)
                st.link_button("👁️ Zobacz pełne", p['webViewLink'])
    else:
        st.info("Nie znaleziono jeszcze zdjęć przypisanych do tego nazwiska.")

# Przycisk dodawania nowych zdjęć (Formularz Google)
st.write("---")
st.markdown("#### Dodaj nowe zdjęcia/nagrania")
st.info("Zdjęcia dodawaj przez poniższy formularz. Pamiętaj, aby w formularzu wpisać nazwisko klienta!")

# TWOJE ZADANIE: Wklej poniżej swój link do Formularza Google
form_url = "TWOJ_LINK_DO_FORMULARZA_GOOGLE"
st.link_button("🚀 OTWÓRZ APARAT / FORMULARZ", form_url, use_container_width=True)

st.divider()

# Powrót
if st.button("⬅️ POWRÓT DO LISTY", use_container_width=True):
    st.switch_page("main.py")
