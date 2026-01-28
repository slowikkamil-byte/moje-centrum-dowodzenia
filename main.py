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

# --- CZARODZIEJSKI CSS (Naprawia menu i wyszukiwarkę) ---
st.markdown("""
    <style>
    /* Ukrywamy wszystko co zbędne */
    [data-testid="stSidebar"], .stDeployButton, header {display: none !important;}
    .main .block-container { padding: 10px 10px 120px 10px !important; }

    /* STYLIZACJA WYSZUKIWARKI */
    div[data-baseweb="input"] {
        border-radius: 20px !important;
        background-color: #1e1e1e !important;
        border: 1px solid #ffaa00 !important;
    }

    /* PASEK DOLNY (NAWIGACJA) */
    .nav-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0e1117;
        display: flex;
        justify-content: space-around;
        padding: 15px 0;
        border-top: 2px solid #ffaa00;
        z-index: 999999;
    }
    
    /* Ukrycie domyślnych przycisków Streamlit w stopce, żeby zrobić miejsce na nasze */
    [data-testid="stVerticalBlock"] > div:last-child { position: static !important; }
    </style>
    """, unsafe_allow_html=True)

# Inicjalizacja zakładki
if 'tab' not in st.session_state:
    st.session_state.tab = "Start"

# --- GÓRA: TYTUŁ I WYSZUKIWARKA ---
st.markdown("### 🏠 Dekarz CRM")
# Dynamiczna wyszukiwarka
search_query = st.text_input("Szukaj...", placeholder="Wpisz np. 'war' lub nazwisko", label_visibility="collapsed").lower()

# --- LOGIKA WYSZUKIWANIA ---
if search_query and not df.empty:
    results = df[df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    if not results.empty:
        st.caption(f"Wyniki: {len(results)}")
        for i, row in results.iterrows():
            if st.button(f"👤 {row.iloc[0]} | {row.iloc[3]}", key=f"s_{i}", use_container_width=True):
                st.session_state.selected_client = row
                st.switch_page("pages/details.py")
    st.divider()

# --- ŚRODEK: TREŚĆ ZAKŁADEK ---
if st.session_state.tab == "Start":
    st.markdown("#### 🏗️ W realizacji")
    active = df[df['Status'] == "W realizacji"] if 'Status' in df.columns else pd.DataFrame()
    if not active.empty:
        for idx, row in active.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row.iloc[0]}**\n\n📍 {row.iloc[3]}")
                if st.button("Szczegóły", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.selected_client = row
                    st.switch_page("pages/details.py")
    else:
        st.info("Brak aktywnych budów.")

elif st.session_state.tab == "Aktualności":
    st.markdown("#### ⚡ Aktualności")
    for i, row in df.iloc[::-1].head(10).iterrows():
        st.info(f"**{row.iloc[0]}**\n{row.iloc[9]}")

# --- DÓŁ: MOJE MENU (FIXED) ---
# Używamy st.columns, ale musimy je zmusić do zostania w poziomie przez CSS wbudowany
m_cols = st.columns(5)
labels = ["Start", "Akt", "Kli", "Tel", "Zad"]
icons = ["🏠", "⚡", "👥", "📞", "✅"]
tabs = ["Start", "Aktualności", "Klienci", "Telefony", "Zadania"]

for i, col in enumerate(m_cols):
    with col:
        # Przycisk z ikoną i krótkim podpisem
        if st.button(f"{icons[i]}\n{labels[i]}", key=f"nav_{i}", use_container_width=True):
            st.session_state.tab = tabs[i]
            st.rerun()

# CSS wymuszający układ 5 kolumn obok siebie na dole
st.markdown(f"""
    <style>
    [data-testid="stHorizontalBlock"] {{
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        background: #0e1117 !important;
        padding: 10px !important;
        z-index: 100000 !important;
        border-top: 2px solid #ffaa00 !important;
        display: flex !important;
        flex-direction: row !important;
    }}
    [data-testid="column"] {{
        min-width: 0px !important;
        flex: 1 !important;
    }}
    button p {{ font-size: 10px !important; }}
    </style>
    """, unsafe_allow_html=True)
