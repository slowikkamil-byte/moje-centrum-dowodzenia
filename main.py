import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Konfiguracja strony
st.set_page_config(page_title="CRM Dekarski", layout="wide")

# CSS dla Dark Mode i kontrastowych kafelków
st.markdown("""
    <style>
    .stButton button {
        background-color: #1d2129;
        border: 1px solid #00e676;
        color: white;
    }
    .stButton button:hover {
        background-color: #00e676;
        color: black;
    }
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: #1d2129;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #00e676;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_data():
    try:
        # POBIERANIE BEZ json.loads (Streamlit sam parsuje TOML z Secrets)
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
        st.error(f"Błąd połączenia z Arkuszem: {e}")
        return pd.DataFrame()

st.title("🏗️ Twoje Zlecenia")

df = get_data()

if not df.empty:
    search = st.text_input("🔍 Szukaj klienta...").lower()
    if search:
        df = df[df.apply(lambda row: search in row.astype(str).str.lower().values, axis=1)]

    for index, row in df.iterrows():
        # Mapowanie kolumn: A-Nazwisko, B-Data kontaktu, D-Esencja
        nazwisko = row.iloc[0]
        data_k = row.iloc[1] if len(row) > 1 else "Brak daty"
        esencja = row.iloc[3] if len(row) > 3 else "Brak opisu"
        
        with st.container():
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"### {nazwisko}")
                st.markdown(f"📅 **Kontakt:** {data_k} | 💡 **Opis:** {esencja}")
            with c2:
                st.write("")
                if st.button("Szczegóły", key=f"btn_{index}", use_container_width=True):
                    st.session_state['selected_client'] = row
                    st.switch_page("pages/details.py")
else:
    st.info("Baza jest pusta lub trwa ładowanie...")
