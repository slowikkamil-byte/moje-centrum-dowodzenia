import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Konfiguracja strony
st.set_page_config(page_title="CRM Dekarski", layout="wide", initial_sidebar_state="expanded")

# CSS: Ramka 2px, Dark Mode i pełna szerokość przycisków na mobilkach
st.markdown("""
    <style>
    .client-card {
        border: 2px solid #00e676;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #1d2129;
    }
    .stButton button {
        background-color: transparent;
        border: 1px solid #00e676;
        color: #00e676;
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #00e676;
        color: #1d2129;
    }
    /* Równe rozłożenie i pełna szerokość w widoku mobilnym */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 auto !important;
        min-width: 100% !important;
        margin-bottom: 5px;
    }
    @media (min-width: 768px) {
        [data-testid="column"] {
            min-width: 0 !important;
            flex: 1 1 0% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Funkcja pobierania danych
def get_data():
    try:
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=st.secrets["spreadsheet_id"],
            range="Arkusz1!A:M"
        ).execute()
        values = result.get('values', [])
        if not values: return pd.DataFrame()
        return pd.DataFrame(values[1:], columns=values[0])
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")
        return pd.DataFrame()

# --- NAWIGACJA (TWOJE PRZYCISKI) ---
if 'view' not in st.session_state:
    st.session_state.view = "Klienci"

m1, m2, m3 = st.columns(3)
with m1:
    if st.button("🏗️ START", use_container_width=True): 
        st.session_state.view = "Start"
with m2:
    if st.button("👥 KLIENCI", use_container_width=True): 
        st.session_state.view = "Klienci"
with m3:
    if st.button("➕ DODAJ", use_container_width=True): 
        st.session_state.view = "Dodaj"

st.divider()

# --- LOGIKA WIDOKÓW ---
if st.session_state.view == "Klienci":
    st.title("🏗️ Lista Klientów")
    
    df = get_data()
    
    if not df.empty:
        search = st.text_input("🔍 Szukaj...", placeholder="Nazwisko, adres...").lower()
        
        if search:
            df = df[df.apply(lambda row: search in str(row.iloc[0]).lower() or search in str(row.iloc[3]).lower(), axis=1)]

        for index, row in df.iterrows():
            nazwisko = row.iloc[0]
            data_k = row.iloc[1] if len(row) > 1 else "---"
            esencja = str(row.iloc[3]) if len(row) > 3 else "Brak opisu"
            
            st.markdown(f"""
                <div class="client-card">
                    <h2 style="margin:0; color:#00e676;">{nazwisko}</h2>
                    <div style="margin: 10px 0; color:#e0e0e0;">
                        <span>📅 <b>Kontakt:</b> {data_k}</span><br>
                        <span style="font-size: 0.9em; opacity: 0.8;">📍 {esencja}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button(f"Szczegóły: {nazwisko}", key=f"btn_{index}", use_container_width=True):
                st.session_state['selected_client'] = row
                st.switch_page("pages/details.py")
    else:
        st.info("Pobieranie danych...")

elif st.session_state.view == "Start":
    st.title("🏠 Panel Główny")
    st.write("Witaj w systemie! Wybierz 'Klienci', aby zobaczyć listę.")

elif st.session_state.view == "Dodaj":
    st.title("➕ Dodaj nowe zlecenie")
    st.write("Tutaj w przyszłości dodamy formularz szybkiego dodawania klienta.")

# Sidebar
st.sidebar.button("🔄 Odśwież dane", on_click=lambda: st.rerun())
