import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

# Ustawienia strony
st.set_page_config(page_title="CRM Dekarski", layout="wide")

# 1. Połączenie z Arkuszem
def get_data():
    try:
        info = json.loads(st.secrets["gcp_service_account"])
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)
        
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=st.secrets["spreadsheet_id"],
            range="Arkusz1!A:M"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return pd.DataFrame()
        
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return pd.DataFrame()

# --- UI ---
st.title("🏗️ Twoje Zlecenia")

# Pobieranie danych
df = get_data()

if not df.empty:
    # Wyszukiwarka
    search = st.text_input("🔍 Szukaj klienta (nazwisko, miasto, telefon)...").lower()
    
    if search:
        df = df[df.apply(lambda row: search in row.astype(str).str.lower().values, axis=1)]

    st.divider()

    # Wyświetlanie kafelków
    for index, row in df.iterrows():
        # Pobieramy dane z odpowiednich kolumn (dostosuj indeksy jeśli trzeba)
        nazwisko = row.iloc[0]
        data_wpisu = row.iloc[1] if len(row) > 1 else "Brak daty"
        esencja = row.iloc[3] if len(row) > 3 else "Brak opisu"
        status = row.iloc[10] if len(row) > 10 else "Nowy"

        # Kontener dla kafelka
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### {nazwisko}")
                # Mały tekst pod nazwiskiem: Data i Esencja
                st.markdown(f"📅 **Data kontaktu:** {data_wpisu} | 📝 **Opis:** {esencja}")
                st.caption(f"📍 {row.iloc[3]}") # Adres
            
            with col2:
                st.write("") # Odstęp
                if st.button(f"Szczegóły", key=f"btn_{index}", use_container_width=True):
                    st.session_state['selected_client'] = row
                    st.switch_page("pages/details.py")
            
            st.divider()
else:
    st.info("Brak danych w arkuszu lub błąd połączenia.")

# Odświeżanie
if st.button("🔄 Odśwież dane"):
    st.rerun()
