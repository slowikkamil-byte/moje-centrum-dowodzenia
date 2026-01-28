import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Konfiguracja strony
st.set_page_config(page_title="CRM Dekarski", layout="wide", initial_sidebar_state="expanded")

# CSS: Cienka zielona ramka (2px), czyste karty i styl przycisków
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
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #00e676;
        color: #1d2129;
    }
    /* Styl dla przycisków akcji pod wyszukiwarką */
    .action-button button {
        border: 1px solid #e0e0e0 !important;
        color: #e0e0e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

st.title("🏗️ Twoje Zlecenia")

df = get_data()

if not df.empty:
    # 1. WYSZUKIWARKA
    search = st.text_input("🔍 Szukaj klienta...", placeholder="Wpisz nazwisko lub adres...").lower()
    
    # 2. TRZY PRZYCISKI AKCJI (Filtry / Szybkie akcje)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🆕 Nowe zlecenia", key="filter_new"):
            search = "nowy" # Przykładowe działanie - filtracja
    with col_b:
        if st.button("📅 Dzisiejsze spotkania", key="filter_today"):
            # Tutaj można dodać logikę filtrowania po dacie
            st.info("Funkcja filtrowania daty w przygotowaniu")
    with col_c:
        if st.button("✅ Zakończone", key="filter_done"):
            search = "zakończone"

    if search:
        df = df[df.apply(lambda row: search in str(row.iloc[0]).lower() or search in str(row.iloc[3]).lower() or search in str(row.iloc[10]).lower(), axis=1)]

    st.write("") 

    # 3. LISTA KLIENTÓW W RAMKACH 2PX
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
        
        if st.button(f"Otwórz kartę: {nazwisko}", key=f"btn_{index}"):
            st.session_state['selected_client'] = row
            st.switch_page("pages/details.py")
else:
    st.info("Pobieranie danych z bazy...")

# Sidebar
st.sidebar.markdown("### Ustawienia")
if st.sidebar.button("🔄 Odśwież Bazę"):
    st.rerun()
