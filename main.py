import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Konfiguracja strony
st.set_page_config(page_title="CRM Dekarski", layout="wide", initial_sidebar_state="expanded")

# CSS: Cienka zielona ramka (2px), czyste karty i pełna szerokość przycisków mobilnych
st.markdown("""
    <style>
    .client-card {
        border: 2px solid #00e676;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #1d2129;
    }
    /* Styl dla wszystkich przycisków */
    .stButton button {
        background-color: transparent;
        border: 1px solid #00e676;
        color: #00e676;
        width: 100%; /* Pełna szerokość na mobilkach */
        border-radius: 8px;
        transition: 0.3s;
        height: 3em;
        margin-bottom: 10px;
    }
    .stButton button:hover {
        background-color: #00e676;
        color: #1d2129;
    }
    /* Usunięcie zbędnych marginesów w kolumnach na mobilkach */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 calc(33.333% - 1rem) !important;
        min-width: 100% !important;
    }
    @media (min-width: 768px) {
        [data-testid="column"] {
            min-width: 0 !important;
        }
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
    
    # 2. TWOJE ORYGINALNE 3 PRZYCISKI (Pełna szerokość na mobilnych)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📞 Do zadzwonienia", use_container_width=True):
            search = "do zadzwonienia"
    with col2:
        if st.button("📝 Do wyceny", use_container_width=True):
            search = "do wyceny"
    with col3:
        if st.button("📅 Umówione", use_container_width=True):
            search = "umówione"

    if search:
        # Filtrowanie po Nazwisku (0), Esencji (3) lub Statusie (10)
        df = df[df.apply(lambda row: search in str(row.iloc[0]).lower() or 
                                     search in str(row.iloc[3]).lower() or 
                                     search in str(row.iloc[10]).lower(), axis=1)]

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
        
        if st.button(f"Szczegóły: {nazwisko}", key=f"btn_{index}", use_container_width=True):
            st.session_state['selected_client'] = row
            st.switch_page("pages/details.py")
else:
    st.info("Pobieranie danych z bazy...")

st.sidebar.markdown("### Nawigacja")
if st.sidebar.button("🔄 Odśwież listę"):
    st.rerun()
