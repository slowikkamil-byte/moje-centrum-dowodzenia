import streamlit as st
import pandas as pd

# 1. Konfiguracja strony
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# 2. Link CSV
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_csv(URL).fillna("")
        return df
    except:
        return pd.DataFrame()

df = load_data()

# --- STYLIZACJA CSS (Wymuszamy menu na dole i brak paska bocznego) ---
st.markdown("""
    <style>
    /* Ukrycie domyślnego menu bocznego Streamlit */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* Odstęp na dole dla treści, żeby menu nic nie zasłaniało */
    .main .block-container { margin-bottom: 100px; }

    /* Stylizacja paska wyszukiwania */
    div[data-baseweb="input"] { border-radius: 15px !important; }

    /* KONTENER DOLNEGO MENU */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #111;
        color: white;
        text-align: center;
        z-index: 1000;
        padding: 10px 0;
        border-top: 1px solid #333;
        display: flex;
        justify-content: space-around;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIKA NAWIGACJI ---
# Skoro nie działa zewnętrzna biblioteka, używamy session_state do sterowania widokiem
if 'menu_wybor' not in st.session_state:
    st.session_state['menu_wybor'] = "Start"

# --- GLOBALNA WYSZUKIWARKA ---
st.write("### 🏠 Dekarz CRM")
search_query = st.text_input("🔍 Szukaj...", placeholder="Wpisz cokolwiek (np. war...)").lower()

# Wyświetlanie wyników wyszukiwania (zawsze na górze jeśli coś wpisano)
if search_query and not df.empty:
    mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
    df_results = df[mask]
    if not df_results.empty:
        st.subheader(f"🔎 Wyniki ({len(df_results)})")
        for index, row in df_results.iterrows():
            if st.button(f"👤 {row.iloc[0]} | 📍 {row.iloc[3]}", key=f"src_{index}"):
                st.session_state['selected_client'] = row
                st.switch_page("pages/details.py")
    st.divider()

# --- TREŚĆ ZAKŁADEK ---
if st.session_state['menu_wybor'] == "Start":
    st.header("🏗️ W realizacji")
    # ... (tutaj Twój kod kafelków "W realizacji") ...
    st.write("Lista Twoich aktywnych budów pojawi się tutaj.")

elif st.session_state['menu_wybor'] == "Aktualności":
    st.header("⚡ Ostatnie rozmowy")
    # ... kod aktualności ...

elif st.session_state['menu_wybor'] == "Klienci":
    st.header("👥 Baza klientów")
    st.dataframe(df, use_container_width=True)

# --- DOLNE MENU (Ręcznie robione kolumny na dole) ---
# To zastępuje znikające menu boczne i zewnętrzne biblioteki
st.markdown('<div class="footer">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    if st.button("🏠\nStart"): st.session_state['menu_wybor'] = "Start"; st.rerun()
with c2:
    if st.button("⚡\nAktualki"): st.session_state['menu_wybor'] = "Aktualności"; st.rerun()
with c3:
    if st.button("👥\nKlienci"): st.session_state['menu_wybor'] = "Klienci"; st.rerun()
with c4:
    if st.button("📞\nTel"): st.session_state['menu_wybor'] = "Telefony"; st.rerun()
with c5:
    if st.button("✅\nZadania"): st.session_state['menu_wybor'] = "Zadania"; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
