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

# --- AGRESYWNY CSS (Wymuszamy poziome menu na dole) ---
st.markdown("""
    <style>
    /* Ukrycie paska bocznego i nagłówków */
    [data-testid="stSidebar"], .stDeployButton, header {display: none !important;}
    
    /* Marginesy treści */
    .main .block-container { padding: 10px; margin-bottom: 100px; }

    /* PASEK NAWIGACJI NA DOLE (Jak na Twoim rysunku) */
    .nav-wrapper {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111111;
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 15px 0;
        border-top: 2px solid #ffaa00;
        z-index: 99999;
    }
    
    .nav-button {
        background: none;
        border: none;
        color: white;
        text-align: center;
        font-size: 24px;
        text-decoration: none;
        flex: 1;
        cursor: pointer;
    }

    .nav-label {
        font-size: 10px;
        display: block;
        margin-top: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# Zarządzanie zakładkami
if 'tab' not in st.session_state:
    st.session_state.tab = "Start"

# --- WYSZUKIWARKA ---
st.markdown("## 🏠 Dekarz CRM")
# Używamy st.text_input. Jeśli wpiszesz fragment i klikniesz "Gotowe" na klawiaturze, zadziała natychmiast.
search_query = st.text_input("Szukaj klienta...", placeholder="Wpisz np. 'war' lub nazwisko", label_visibility="collapsed").lower()

if search_query and not df.empty:
    results = df[df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    if not results.empty:
        st.write(f"🔎 Wyniki ({len(results)}):")
        for i, row in results.iterrows():
            if st.button(f"👤 {row.iloc[0]} | {row.iloc[3]}", key=f"s_{i}", use_container_width=True):
                st.session_state.selected_client = row
                st.switch_page("pages/details.py")
    st.divider()

# --- TREŚĆ ZAKŁADEK ---
if st.session_state.tab == "Start":
    st.markdown("### 🏗️ W realizacji")
    active = df[df['Status'] == "W realizacji"] if 'Status' in df.columns else pd.DataFrame()
    if not active.empty:
        for idx, row in active.iterrows():
            st.info(f"**{row.iloc[0]}**\n\n📍 {row.iloc[3]}")
            if st.button("Szczegóły", key=f"btn_{idx}", use_container_width=True):
                st.session_state.selected_client = row
                st.switch_page("pages/details.py")
    else:
        st.write("Brak aktywnych budów o statusie 'W realizacji'.")

elif st.session_state.tab == "Aktualności":
    st.markdown("### ⚡ Aktualności")
    # Wyświetlamy 10 najnowszych
    df_recent = df.iloc[::-1].head(10)
    for i, row in df_recent.iterrows():
        with st.expander(f"📌 {row.iloc[0]} - {row.iloc[3]}"):
            st.write(f"📞 {row.iloc[6]}")
            st.info(f"💡 {row.iloc[9]}")

# --- DODAWANIE PRZYCISKÓW DO MENU (Trik z HTML) ---
# Ponieważ przyciski Streamlit wewnątrz HTML nie działają bezpośrednio,
# używamy natywnych kolumn, ale wymuszamy ich szerokość CSSem, by nie przeskakiwały do pionu.
st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True) # Dystans

# Ten kontener będzie "pływał" na dole
menu_container = st.container()
with menu_container:
    # Wymuszamy 5 kolumn obok siebie nawet na telefonie
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

# CSS wymuszający układ poziomy dla kolumn menu
st.markdown("""
    <style>
    [data-testid="column"] {
        width: 20% !important;
        flex: 1 1 20% !important;
        min-width: 20% !important;
    }
    [data-testid="stVerticalBlock"] > div:last-child {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #111;
        padding: 10px;
        z-index: 10000;
        border-top: 2px solid orange;
    }
    </style>
    """, unsafe_allow_html=True)
