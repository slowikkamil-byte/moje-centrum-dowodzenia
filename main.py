import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- 1. KONFIGURACJA ---
st.set_page_config(page_title="CRM Dekarski", layout="wide", initial_sidebar_state="collapsed")

# --- CSS (Stylizacja kart 2px i przycisków mobilnych) ---
st.markdown("""
    <style>
    /* Ukrycie domyślnych elementów */
    .stDeployButton, header {display: none !important;}
    
    /* Karta klienta - Twoja zielona ramka 2px */
    .client-card {
        border: 2px solid #00e676;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 10px;
        background-color: #1d2129;
    }
    
    /* Przyciski nawigacyjne i akcji */
    .stButton button {
        background-color: transparent;
        border: 1px solid #00e676;
        color: #00e676;
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #00e676;
        color: #1d2129;
    }

    /* Responsywność kolumn (przyciski jeden pod drugim na telefonie) */
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

# --- 2. FUNKCJA POBIERANIA DANYCH ---
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

# --- 3. UI I NAWIGACJA ---
st.title("🏗️ CRM Dekarski")

# Inicjalizacja widoku
if 'view' not in st.session_state:
    st.session_state.view = "Start"

# TWOJE PRZYCISKI MENU
m1, m2, m3 = st.columns(3)
with m1:
    if st.button("🏗️ START", use_container_width=True): 
        st.session_state.view = "Start"
with m2:
    if st.button("👥 KLIENCI", use_container_width=True): 
        st.session_state.view = "Klienci"
with m3:
    if st.button("✅ ZADANIA", use_container_width=True): 
        st.session_state.view = "Zadania"

st.divider()

# --- 4. LOGIKA WIDOKÓW ---
df = get_data()

if df.empty:
    st.warning("Brak danych lub błąd połączenia.")
    st.stop()

# --- WIDOK: START (W realizacji) ---
if st.session_state.view == "Start":
    st.subheader("🏠 W realizacji")
    # Filtrujemy wiersze, które zawierają frazę "W realizacji"
    active_df = df[df.apply(lambda row: row.astype(str).str.contains("W realizacji", case=False).any(), axis=1)]
    
    if not active_df.empty:
        for i, row in active_df.iterrows():
            st.markdown(f"""<div class="client-card">
                <b>{row.iloc[0]}</b><br>📍 {row.iloc[3]}
            </div>""", unsafe_allow_html=True)
            if st.button(f"Szczegóły: {row.iloc[0]}", key=f"start_{i}"):
                st.session_state.selected_client = row
                st.switch_page("pages/details.py")
    else:
        st.write("Brak aktywnych budów.")

# --- WIDOK: KLIENCI (Baza) ---
elif st.session_state.view == "Klienci":
    st.subheader("👥 Baza Klientów")
    search = st.text_input("", placeholder="Szukaj klienta...").lower()
    
    df_display = df.copy()
    if search:
        df_display = df_display[df_display.apply(lambda row: search in str(row.iloc[0]).lower() or search in str(row.iloc[3]).lower(), axis=1)]

    for i, row in df_display.iterrows():
        st.markdown(f"""
            <div class="client-card">
                <h3 style="margin:0; color:#00e676;">{row.iloc[0]}</h3>
                <div style="margin: 10px 0; color:#e0e0e0;">
                    <span>📅 <b>Data:</b> {row.iloc[1] if len(row)>1 else "---"}</span><br>
                    <span>📍 {row.iloc[3] if len(row)>3 else "Brak adresu"}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Otwórz kartę", key=f"kli_{i}", use_container_width=True):
            st.session_state.selected_client = row
            st.switch_page("pages/details.py")

# --- WIDOK: ZADANIA ---
elif st.session_state.view == "Zadania":
    st.subheader("✅ Twoje Zadania")
    st.info("Tutaj pojawią się zadania z kolumny terminarza.")

# Sidebar (ukryty, ale dostępny pod przyciskiem odśwież)
if st.sidebar.button("🔄 Odśwież dane"):
    st.rerun()
