import streamlit as st
import pandas as pd

# 1. Konfiguracja
st.set_page_config(page_title="Dekarz CRM", layout="wide")

# 2. Dane
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL, on_bad_lines='skip', engine='python')
        df.columns = df.columns.str.strip()
        # Konwersja daty (zakładając, że data jest w pierwszej kolumnie lub ma nazwę 'Data')
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        return df.fillna("")
    except:
        return pd.DataFrame()

df = load_data()

# --- CSS (Stylizacja kart i czystego layoutu) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"], .stDeployButton, header {display: none !important;}
    .main .block-container { padding-top: 10px !important; }
    div[data-baseweb="input"] { border-radius: 10px !important; }
    .client-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffaa00;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. WYSZUKIWARKA NA SAMEJ GÓRZE ---
search_query = st.text_input("", placeholder="Szukaj klienta...", label_visibility="collapsed").lower()

# --- 2. MENU PRZYCISKOWE (Bez napisu MENU) ---
m1, m2, m3 = st.columns(3)
with m1:
    if st.button("🏗️ START", use_container_width=True): st.session_state.view = "Start"
with m2:
    if st.button("👥 KLIENCI", use_container_width=True): st.session_state.view = "Klienci"
with m3:
    if st.button("✅ ZADANIA", use_container_width=True): st.session_state.view = "Zadania"

if 'view' not in st.session_state: st.session_state.view = "Start"

st.divider()

# Logika wyszukiwania (wyświetla się przed zakładkami, jeśli coś wpisano)
if search_query and not df.empty:
    mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
    results = df[mask]
    if not results.empty:
        for i, row in results.iterrows():
            with st.container():
                st.markdown(f"**{row.iloc[0]}** | 📍 {row.iloc[3]}")
                if st.button("Otwórz", key=f"s_{i}", use_container_width=True):
                    st.session_state.selected_client = row
                    st.switch_page("pages/details.py")
        st.divider()

# --- 3. ZAKŁADKI ---

if st.session_state.view == "Start":
    st.subheader("W realizacji")
    # Filtrowanie po statusie "W realizacji" w całym wierszu
    active_df = df[df.apply(lambda row: row.astype(str).str.contains("W realizacji", case=False).any(), axis=1)]
    
    if not active_df.empty:
        for i, row in active_df.iterrows():
            with st.container():
                st.info(f"**{row.iloc[0]}**\n\n📍 {row.iloc[3]}")
                if st.button("Szczegóły", key=f"act_{i}", use_container_width=True):
                    st.session_state.selected_client = row
                    st.switch_page("pages/details.py")
    else:
        st.write("Brak budów.")

elif st.session_state.view == "Klienci":
    st.subheader("Baza Klientów")
    
    # --- FILTRY MOBILNE ---
    with st.expander("🔍 Filtrowanie i Sortowanie"):
        # Sortowanie po dacie
        sort_order = st.radio("Kolejność:", ["Najnowsze", "Najstarsze"], horizontal=True)
        
        # Filtry statusu i zakresu (wyciągane dynamicznie z kolumn)
        status_filter = st.multiselect("Status:", options=list(df['Status'].unique()) if 'Status' in df.columns else [])
        work_filter = st.multiselect("Zakres prac:", options=list(df['Typ pracy'].unique()) if 'Typ pracy' in df.columns else [])

    # Logika filtrów
    df_display = df.copy()
    if status_filter:
        df_display = df_display[df_display['Status'].isin(status_filter)]
    if work_filter:
        df_display = df_display[df_display['Typ pracy'].isin(work_filter)]
    
    # Logika sortowania
    if 'Data' in df_display.columns:
        df_display = df_display.sort_values(by='Data', ascending=(sort_order == "Najstarsze"))

    # Wyświetlanie jako KARTY zamiast tabeli
    for i, row in df_display.iterrows():
        with st.container():
            st.markdown(f"""
                <div class="client-card">
                    <div style="font-size:18px; font-weight:bold;">{row.iloc[0]}</div>
                    <div style="color:#aaa; font-size:12px;">📍 {row.iloc[3]} | 📞 {row.iloc[6]}</div>
                    <div style="margin-top:5px;"><span style="background:#444; padding:2px 8px; border-radius:5px; font-size:10px;">{row.get('Status', '')}</span></div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Szczegóły klienta", key=f"kli_{i}", use_container_width=True):
                st.session_state.selected_client = row
                st.switch_page("pages/details.py")
            st.markdown("---")
