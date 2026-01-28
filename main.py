import streamlit as st
import pandas as pd

# Konfiguracja strony
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# Link do Arkusza (upewnij się, że jest udostępniony: Każdy z linkiem może przeglądać)
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        # on_bad_lines='skip' naprawia błąd ParserError ze screena
        df = pd.read_csv(URL, on_bad_lines='skip', engine='python').fillna("")
        # Usuwamy ewentualne puste spacje z nazw kolumn
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Błąd bazy: {e}")
        return pd.DataFrame()

df = load_data()

# --- EKSTREMALNY CSS DLA MOBILNEGO MENU ---
st.markdown("""
    <style>
    /* Ukrycie elementów systemowych */
    [data-testid="stSidebar"], .stDeployButton, header {display: none !important;}
    .main .block-container { padding: 10px 10px 100px 10px !important; }

    /* STYLIZACJA WYSZUKIWARKI */
    div[data-baseweb="input"] {
        border-radius: 25px !important;
        border: 2px solid #ffaa00 !important;
    }

    /* SZTYWNE MENU DOLNE - HTML/CSS */
    .mobile-menu {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111;
        display: flex;
        flex-direction: row;
        justify-content: space-around;
        padding: 10px 0;
        border-top: 2px solid #ffaa00;
        z-index: 999999;
    }
    .menu-item {
        color: white;
        text-align: center;
        text-decoration: none;
        font-size: 10px;
        flex: 1;
        background: none;
        border: none;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# Zarządzanie stanem zakładki
if 'tab' not in st.session_state:
    st.session_state.tab = "Start"

# --- GÓRA: WYSZUKIWARKA ---
st.markdown("### 🏠 Dekarz CRM")
search_query = st.text_input("Szukaj...", placeholder="Wpisz cokolwiek...", label_visibility="collapsed").lower()

if search_query and not df.empty:
    results = df[df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    if not results.empty:
        st.caption(f"Wyniki: {len(results)}")
        for i, row in results.iterrows():
            if st.button(f"👤 {row.iloc[0]} | {row.iloc[3]}", key=f"s_{i}", use_container_width=True):
                st.session_state.selected_client = row
                st.switch_page("pages/details.py")
    st.divider()

# --- ŚRODEK: TREŚĆ ---
if st.session_state.tab == "Start":
    st.markdown("#### 🏗️ W realizacji")
    if not df.empty and 'Status' in df.columns:
        # Filtrujemy dokładnie po frazie "W realizacji"
        active = df[df['Status'].astype(str).str.contains("W realizacji", case=False)]
        if not active.empty:
            for idx, row in active.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row.iloc[0]}**\n\n📍 {row.iloc[3]}")
                    if st.button("Szczegóły", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.selected_client = row
                        st.switch_page("pages/details.py")
        else:
            st.warning("Brak aktywnych budów w Arkuszu.")
    else:
        st.info("Nie znaleziono kolumny 'Status'. Sprawdź nagłówki w Arkuszu.")

elif st.session_state.tab == "Aktualności":
    st.markdown("#### ⚡ Ostatnie zdarzenia")
    if not df.empty:
        for i, row in df.iloc[::-1].head(10).iterrows():
            st.info(f"**{row.iloc[0]}**\n{row.iloc[9]}")

# --- DÓŁ: HORIZONTALNE MENU ---
# Używamy st.columns(5) ale w specyficzny sposób, który zablokuje zawijanie
st.markdown('<div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #111; z-index: 10000; border-top: 2px solid #ffaa00; padding: 5px;">', unsafe_allow_html=True)
m1, m2, m3, m4, m5 = st.columns(5)
with m1: 
    if st.button("🏠\nStart"): st.session_state.tab = "Start"; st.rerun()
with m2: 
    if st.button("⚡\nAkt"): st.session_state.tab = "Aktualności"; st.rerun()
with m3: 
    if st.button("👥\nKli"): st.session_state.tab = "Klienci"; st.rerun()
with m4: 
    if st.button("📞\nTel"): st.session_state.tab = "Telefony"; st.rerun()
with m5: 
    if st.button("✅\nZad"): st.session_state.tab = "Zadania"; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# CSS wymuszający układ poziomy przycisków
st.markdown("""
    <style>
    [data-testid="column"] {
        width: 20% !important;
        flex: 1 1 20% !important;
        min-width: 20% !important;
        padding: 0px !important;
    }
    button[kind="secondary"] {
        padding: 5px 0px !important;
        font-size: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)
