import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(page_title="CRM Dekarski", layout="wide", initial_sidebar_state="collapsed")

# --- 2. STYLIZACJA CSS (Pełna responsywność i styl kart) ---
st.markdown("""
    <style>
    /* Ukrycie elementów systemowych */
    .stDeployButton, header {display: none !important;}
    
    /* Styl dla całego przycisku-karty (Jeden duży klikalny obszar) */
    div.stButton > button {
        border: 2px solid #00e676 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        background-color: #1d2129 !important;
        width: 100% !important;
        min-height: 110px !important;
        text-align: left !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        transition: 0.3s !important;
        margin-bottom: 12px !important;
    }
    
    div.stButton > button:hover {
        border-color: #ffffff !important;
        background-color: #262c36 !important;
    }

    /* Wymuszenie pełnej szerokości na urządzeniach mobilnych */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 auto !important;
        min-width: 100% !important;
    }

    /* Formatowanie tekstu wewnątrz przycisku */
    .stButton p {
        width: 100% !important;
        text-align: left !important;
        margin: 0 !important;
        line-height: 1.5 !important;
    }

    /* Styl nawigacji górnej (Start/Klienci/Zadania) */
    .nav-btn button {
        height: 3.5em !important;
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKCJA POBIERANIA DANYCH Z GOOGLE SHEETS ---
def get_data():
    try:
        if "gcp_service_account" not in st.secrets:
            st.error("Brak konfiguracji Secrets!")
            return pd.DataFrame()
            
        info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=creds)
        
        sheet = service.spreadsheets()
        # Pobieramy zakres od A do M (kolumna M to indeks 12)
        result = sheet.values().get(
            spreadsheetId=st.secrets["spreadsheet_id"],
            range="Arkusz1!A:M"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return pd.DataFrame()
        
        # Tworzymy DataFrame, zakładając że pierwszy wiersz to nagłówki
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    except Exception as e:
        st.error(f"Błąd połączenia z Google Sheets: {e}")
        return pd.DataFrame()

# --- 4. GŁÓWNE UI I NAWIGACJA ---
st.title("🏗️ CRM Dekarski")

if 'view' not in st.session_state:
    st.session_state.view = "Start"

# Menu główne (Twoje przyciski)
m1, m2, m3 = st.columns(3)
with m1:
    if st.button("🏗️ START", key="nav_start", use_container_width=True):
        st.session_state.view = "Start"
with m2:
    if st.button("👥 KLIENCI", key="nav_klienci", use_container_width=True):
        st.session_state.view = "Klienci"
with m3:
    if st.button("✅ ZADANIA", key="nav_zadania", use_container_width=True):
        st.session_state.view = "Zadania"

st.divider()

# Pobranie danych
df = get_data()

if df.empty:
    st.warning("Baza danych jest pusta lub nie udało się połączyć.")
    if st.button("🔄 Odśwież połączenie"):
        st.rerun()
    st.stop()

# --- 5. FUNKCJA RENDEROWANIA KARTY KLIENTA ---
def render_client_card(row, idx):
    nazwisko = row.iloc[0] if len(row) > 0 else "Nieznany"
    data_k = row.iloc[1] if len(row) > 1 else "---"
    adres = row.iloc[3] if len(row) > 3 else "Brak adresu"
    status_l = row.iloc[11] if len(row) > 11 else "Brak statusu"
    zajawka_m = row.iloc[12] if len(row) > 12 else ""

    # Budowanie treści karty
    # --- użyte w markdown wewnątrz buttona tworzy linię oddzielającą
    card_content = f"**{nazwisko}** \n📍 {adres}  \n📅 {data_k} | {status_l}"
    
    if zajawka_m:
        card_content += f"  \n\n---\n\n*{zajawka_m}*"

    if st.button(card_content, key=f"btn_card_{idx}", use_container_width=True):
        st.session_state.selected_client = row
        st.switch_page("pages/details.py")

# --- 6. LOGIKA WIDOKÓW ---

# --- WIDOK: START ---
if st.session_state.view == "Start":
    st.subheader("🏠 W realizacji")
    # Filtrowanie po kolumnie L (indeks 11) dla statusu "W realizacji"
    if df.shape[1] > 11:
        active_df = df[df.iloc[:, 11].str.contains("W realizacji", case=False, na=False)]
        
        if not active_df.empty:
            for i, row in active_df.iterrows():
                render_client_card(row, f"start_{i}")
        else:
            st.info("Brak aktywnych budów.")
    else:
        st.error("Arkusz nie posiada kolumny L (Status).")

# --- WIDOK: KLIENCI ---
elif st.session_state.view == "Klienci":
    st.subheader("👥 Pełna Baza")
    
    # Szukajka
    search = st.text_input("", placeholder="Szukaj (nazwisko lub adres)...").lower()
    
    # Filtry i Sortowanie
    with st.expander("🔍 Filtrowanie i Sortowanie"):
        sort_order = st.radio("Kolejność daty:", ["Najnowsze", "Najstarsze"], horizontal=True)
        
        available_statuses = list(df.iloc[:, 11].unique()) if df.shape[1] > 11 else []
        status_filter = st.multiselect("Filtruj status (Kolumna L):", options=available_statuses)

    # Logika filtrowania
    df_display = df.copy()
    
    if search:
        df_display = df_display[df_display.apply(lambda row: search in str(row.iloc[0]).lower() or search in str(row.iloc[3]).lower(), axis=1)]
    
    if status_filter:
        df_display = df_display[df_display.iloc[:, 11].isin(status_filter)]
    
    # Logika sortowania (Kolumna B / indeks 1)
    if df_display.shape[1] > 1:
        df_display.iloc[:, 1] = pd.to_datetime(df_display.iloc[:, 1], errors='coerce')
        df_display = df_display.sort_values(by=df_display.columns[1], ascending=(sort_order == "Najstarsze"))

    # Wyświetlanie
    if not df_display.empty:
        for i, row in df_display.iterrows():
            render_client_card(row, f"kli_{i}")
    else:
        st.write("Brak klientów spełniających kryteria.")

# --- WIDOK: ZADANIA ---
elif st.session_state.view == "Zadania":
    st.subheader("✅ Zadania i Terminarz")
    st.info("Tu możesz dodać widok zadań wyciągnięty z innej części arkusza.")

# --- SIDEBAR (Opcjonalny) ---
st.sidebar.markdown("### CRM Dekarski v2")
if st.sidebar.button("🔄 Wymuś odświeżenie danych"):
    st.cache_data.clear()
    st.rerun()
