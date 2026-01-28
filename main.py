import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Konfiguracja strony
st.set_page_config(page_title="CRM Dekarski", layout="wide", initial_sidebar_state="expanded")

# CSS: Cienka zielona ramka (2px) i czyste karty
st.markdown("""
    <style>
    /* Styl głównego kontenera karty - tylko zewnętrzna ramka 2px */
    .client-card {
        border: 2px solid #00e676;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: #1d2129;
    }
    
    /* Naprawa przycisku, żeby pasował do stylu */
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
        border: 1px solid #00e676;
    }

    /* Ukrycie domyślnych dekoratorów Streamlit, które psuły widok */
    div[data-testid="stVerticalBlock"] > div:has(div.client-card) {
        background-color: transparent !important;
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
    search = st.text_input("🔍 Szukaj klienta...", placeholder="Wpisz nazwisko lub adres...").lower()
    if search:
        # Filtrowanie po nazwisku (col 0) lub esencji/adresie (col 3)
        df = df[df.apply(lambda row: search in str(row.iloc[0]).lower() or search in str(row.iloc[3]).lower(), axis=1)]

    st.write("") 

    for index, row in df.iterrows():
        nazwisko = row.iloc[0]
        data_k = row.iloc[1] if len(row) > 1 else "---"
        # Przycinamy esencję, jeśli jest za długa, żeby karta była zgrabna
        esencja = str(row.iloc[3]) if len(row) > 3 else "Brak opisu"
        
        # Czysta karta z ramką 2px
        st.markdown(f"""
            <div class="client-card">
                <h2 style="margin:0; color:#00e676;">{nazwisko}</h2>
                <div style="margin: 10px 0; color:#e0e0e0;">
                    <span>📅 <b>Kontakt:</b> {data_k}</span><br>
                    <span style="font-size: 0.9em; opacity: 0.8;">📍 {esencja}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Przycisk "Szczegóły" pod kartą
        if st.button(f"Otwórz kartę: {nazwisko}", key=f"btn_{index}"):
            st.session_state['selected_client'] = row
            st.switch_page("pages/details.py")
else:
    st.info("Pobieranie danych z bazy...")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Odśwież Bazę"):
    st.rerun()
