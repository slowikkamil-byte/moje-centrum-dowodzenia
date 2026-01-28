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
    
    /* Styl dla całego przycisku-karty */
    div.stButton > button {
        border: 2px solid #00e676 !important;
        border-radius: 12px !important;
        padding: 0px !important;
        background-color: #1d2129 !important;
        width: 100% !important;
        height: auto !important;
        text-align: left !important;
        transition: 0.3s !important;
        margin-bottom: 10px !important;
        display: block !important;
    }
    
    div.stButton > button:hover {
        border-color: #ffffff !important;
        background-color: #262c36 !important;
    }

    /* Kontener treści wewnątrz przycisku */
    .card-content {
        padding: 15px;
    }

    .client-name {
        color: #00e676;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .client-info {
        color: #e0e0e0;
        font-size: 0.9em;
        margin-bottom: 3px;
    }

    .client-note {
        color: #aaaaaa;
        font-size: 0.85em;
        font-style: italic;
        margin-top: 8px;
        border-top: 1px solid #333;
        padding-top: 5px;
    }

    /* Styl nawigacji górnej */
    .nav-button button {
        height: 3.5em !important;
        text-align: center !important;
    }

    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 auto !important;
        min-width: 100% !important;
    }
    @media (min-width: 768px) {
        [data-testid="column"] {
            min-width: 0 !important;
            flex: 1 1 0% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. POBIERANIE DANYCH ---
def get_data():
    try:
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        # Pobieramy do kolumny M (indeks 12)
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

# --- 4. NAWIGACJA ---
st.title("🏗️ CRM Dekarski")

if 'view' not in st.session_state:
    st.session_state.view = "Start"

cols = st.columns(3)
nav_items = [("🏗️ START", "Start"), ("👥 KLIENCI", "Klienci"), ("✅ ZADANIA", "Zadania")]

for i, (label, view_name) in enumerate(nav_items):
    with cols[i]:
        if st.button(label, key=f"nav_{view_name}", use_container_width=True):
            st.session_state.view = view_name

st.divider()
df = get_data()

if df.empty:
    st.warning("Brak danych...")
    st.stop()

# --- 5. LOGIKA WIDOKÓW ---

def render_client_card(row, idx):
    """Renderuje cały kafelek jako jeden klikalny przycisk"""
    nazwisko = row.iloc[0]
    data_k = row.iloc[1] if len(row) > 1 else "---"
    adres = row.iloc[3] if len(row) > 3 else "Brak adresu"
    status = row.iloc[11] if len(row) > 11 else "Brak statusu"
    zajawka = row.iloc[12] if len(row) > 12 else "" # Kolumna M (indeks 12)

    # Budujemy HTML, który wstrzykniemy do etykiety przycisku (nie zadziała bezpośrednio, 
    # więc używamy markdown do opisu, a przycisk jako 'invisible overlay' lub po prostu stylizujemy przycisk)
    
    button_label = f"""
        {nazwisko}
        📍 {adres}
        📅 {data_k} | {status}
        {"📝 " + zajawka if zajawka else ""}
    """
    
    # Tworzymy kontener, który wizualnie wygląda jak karta, ale przycisk jest w środku
    # W Streamlit najskuteczniej jest użyć przycisku z sformatowanym tekstem
    
    card_text = f"**{nazwisko}**\n\n📍 {adres}\n\n"
    if zajawka:
        card_text += f"*{zajawka}*"

    if st.button(card_text, key=f"card_{idx}"):
        st.session_state.selected_client = row
        st.switch_page("pages/details.py")

# --- WIDOK START ---
if st.session_state.view == "Start":
    st.subheader("🏠 W realizacji")
    active_df = df[df.apply(lambda row: "W realizacji" in str(row.iloc[11]), axis=1)] if df.shape[1] > 11 else pd.DataFrame()
    for i, row in active_df.iterrows():
        render_client_card(row, f"start_{i}")

# --- WIDOK KLIENCI ---
elif st.session_state.view == "Klienci":
    st.subheader("👥 Baza Klientów")
    search = st.text_input("", placeholder="Szukaj klienta...").lower()
    
    with st.expander("🔍 Filtrowanie"):
        sort_order = st.radio("Kolejność:", ["Najnowsze", "Najstarsze"], horizontal=True)
        statuses = list(df.iloc[:, 11].unique()) if df.shape[1] > 11 else []
        status_filter = st.multiselect("Status (L):", options=statuses)

    df_display = df.copy()
    if search:
        df_display = df_display[df_display.apply(lambda row: search in str(row.iloc[0]).lower() or search in str(row.iloc[3]).lower(), axis=1)]
    if status_filter:
        df_display = df_display[df_display.iloc[:, 11].isin(status_filter)]
    
    # Sortowanie
    if df_display.shape[1] > 1:
        df_display.iloc[:, 1] = pd.to_datetime(df_display.iloc[:, 1], errors='coerce')
        df_display = df_display.sort_values(by=df_display.columns[1], ascending=(sort_order == "Najstarsze"))

    for i, row in df_display.iterrows():
        render_client_card(row, f"kli_{i}")

# --- WIDOK ZADANIA ---
elif st.session_state.view == "Zadania":
    st.subheader("✅ Zadania")
    st.info("Sekcja w przygotowaniu.")

if st.sidebar.button("🔄 Odśwież"):
    st.rerun()
