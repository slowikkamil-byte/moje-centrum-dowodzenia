import streamlit as st
import pandas as pd

# 1. Konfiguracja pod telefon
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# 2. Dane
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_csv(URL).fillna("")
        return df
    except:
        return pd.DataFrame()

df = load_data()

# --- STYLIZACJA (To naprawi wygląd menu i wyszukiwarki) ---
st.markdown("""
    <style>
    /* Ukrycie paska bocznego i standardowych ikon Streamlit */
    [data-testid="stSidebar"], .stDeployButton, header {display: none !important;}
    
    /* Główne tło i marginesy */
    .main .block-container { padding: 10px; margin-bottom: 80px; }

    /* STYLIZACJA PASKA WYSZUKIWANIA */
    div[data-baseweb="input"] {
        border-radius: 15px !important;
        background-color: #262730 !important;
    }

    /* PRZYKLEJONE MENU DOLNE (Z Twojej wizualizacji) */
    .nav-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111;
        display: flex;
        justify-content: space-around;
        padding: 10px 0;
        border-top: 2px solid #ffaa00;
        z-index: 9999;
    }
    .nav-item {
        color: white;
        text-align: center;
        text-decoration: none;
        font-size: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicjalizacja stanu menu
if 'tab' not in st.session_state:
    st.session_state.tab = "Start"

# --- GÓRA: WYSZUKIWARKA ---
st.title("🏠 Dekarz CRM")
# Dodajemy on_change dla lepszej dynamiki
search_query = st.text_input("Szukaj...", placeholder="Wpisz miasto, nazwisko (np. war...)", label_visibility="collapsed").lower()

# Logika wyszukiwania
if search_query and not df.empty:
    results = df[df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    if not results.empty:
        st.subheader(f"🔎 Wyniki ({len(results)})")
        for i, row in results.iterrows():
            if st.button(f"👤 {row.iloc[0]} | {row.iloc[3]}", key=f"s_{i}", use_container_width=True):
                st.session_state.selected_client = row
                st.switch_page("pages/details.py")
    st.divider()

# --- ŚRODEK: TREŚĆ ZAKŁADEK ---
if st.session_state.tab == "Start":
    st.header("🏗️ W realizacji")
    active = df[df['Status'] == "W realizacji"] if 'Status' in df.columns else pd.DataFrame()
    if not active.empty:
        cols = st.columns(2)
        for i, (idx, row) in enumerate(active.iterrows()):
            with cols[i % 2]:
                st.info(f"**{row.iloc[0]}**\n\n📍 {row.iloc[3]}")
                if st.button("Szczegóły", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.selected_client = row
                    st.switch_page("pages/details.py")
    else:
        st.write("Brak aktywnych budów.")

elif st.session_state.tab == "Aktualności":
    st.header("⚡ Aktualności")
    st.write("Ostatnie zdarzenia z bazy...")

# --- DÓŁ: POZIOME MENU (NAPRAWA) ---
# Używamy kolumn, aby przyciski były obok siebie na dole
st.markdown("<br><br>", unsafe_allow_html=True) # Odstęp
footer = st.container()
with footer:
    # Ten blok CSS/HTML "pływa" na dole dzięki stylowi 'position: fixed'
    cols = st.columns(5)
    with cols[0]:
        if st.button("🏠\nStart"): st.session_state.tab = "Start"; st.rerun()
    with cols[1]:
        if st.button("⚡\nAkt"): st.session_state.tab = "Aktualności"; st.rerun()
    with cols[2]:
        if st.button("👥\nKli"): st.session_state.tab = "Klienci"; st.rerun()
    with cols[3]:
        if st.button("📞\nTel"): st.session_state
