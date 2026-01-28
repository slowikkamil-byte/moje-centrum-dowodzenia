import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(page_title="CRM Dekarski", layout="wide", initial_sidebar_state="collapsed")

# --- 2. STYLIZACJA CSS ---
st.markdown("""
    <style>
    .stDeployButton, header {display: none !important;}
    .client-card {
        border: 2px solid #00e676;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: #1d2129;
    }
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

# --- 3. FUNKCJA POBIERANIA DANYCH ---
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

# --- 4. GŁÓWNE UI I NAWIGACJA ---
st.title("🏗️ CRM Dekarski")

if 'view' not in st.session_state:
    st.session_state.view = "Start"

m1, m2, m3 = st.columns(3)
with m1:
    if st.button("🏗️ START", use_container_width=True): st.session_state.view = "Start"
with m2:
    if st.button("👥 KLIENCI", use_container_width=True): st.session_state.view = "Klienci"
with m3:
    if st.button("✅ ZADANIA", use_container_width=True): st.session_state.view = "Zadania"

st.divider()

df = get_data()

if df.empty:
    st.warning("Oczekiwanie na dane...")
    st.stop()

# --- 5. LOGIKA WIDOKÓW ---

# --- START ---
if st.session_state.view == "Start":
    st.subheader("🏠 W realizacji")
    # Filtrowanie po kolumnie L (indeks 11)
    active_df = df[df.apply(lambda row: "W realizacji" in str(row.iloc[11]), axis=1)] if df.shape[1] > 11 else pd.DataFrame()
    
    if not active_df.empty:
        for i, row in active_df.iterrows():
            st.markdown(f"""<div class="client-card">
                <b>{row.iloc[0]}</b><br><small>📍 {row.iloc[3]}</small>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Szczegóły: {row.iloc[0]}", key=f"start_{i}"):
                st.session_state.selected_client = row
                st.switch_page("pages/details.py")
    else:
        st.info("Brak budów ze statusem 'W realizacji' w kolumnie L.")

# --- KLIENCI ---
elif st.session_state.view == "Klienci":
    st.subheader("👥 Baza Klientów")
    search = st.text_input("", placeholder="Szukaj klienta...").lower()
    
    with st.expander("🔍 Filtrowanie i Sortowanie"):
        sort_order = st.radio("Kolejność:", ["Najnowsze", "Najstarsze"], horizontal=True)
        # ZMIANA: Pobieranie statusów z kolumny L (indeks 11)
        statuses = list(df.iloc[:, 11].unique()) if df.shape[1] > 11 else []
        status_filter = st.multiselect("Filtruj status (Kolumna L):", options=statuses)

    df_display = df.copy()
    if search:
        df_display = df_display[df_display.apply(lambda row: search in str(row.iloc[0]).lower() or search in str(row.iloc[3]).lower(), axis=1)]
    
    if status_filter:
        # ZMIANA: Filtrowanie po kolumnie L (indeks 11)
        df_display = df_display[df_display.iloc[:, 11].isin(status_filter)]
    
    if df_display.shape[1] > 1:
        df_display.iloc[:, 1] = pd.to_datetime(df_display.iloc[:, 1], errors='coerce')
        df_display = df_display.sort_values(by=df_display.columns[1], ascending=(sort_order == "Najstarsze"))

    for i, row in df_display.iterrows():
        st.markdown(f"""
            <div class="client-card">
                <h3 style="margin:0; color:#00e676;">{row.iloc[0]}</h3>
                <div style="margin: 10px 0; color:#e0e0e0; font-size: 0.9em;">
                    📅 <b>Data:</b> {row.iloc[1].strftime('%Y-%m-%d') if isinstance(row.iloc[1], pd.Timestamp) else row.iloc[1]}<br>
                    📍 {row.iloc[3]}<br>
                    <span style="background:#00e676; color:#1d2129; padding:2px 8px; border-radius:5px; font-weight:bold; font-size:0.8em;">
                        {row.iloc[11] if len(row) > 11 else 'Brak statusu'}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        if st.button(f"Szczegóły: {row.iloc[0]}", key=f"kli_{i}", use_container_width=True):
            st.session_state.selected_client = row
            st.switch_page("pages/details.py")

# --- ZADANIA ---
elif st.session_state.view == "Zadania":
    st.subheader("✅ Zadania")
    st.info("Sekcja w przygotowaniu.")

if st.sidebar.button("🔄 Odśwież dane"):
    st.rerun()
