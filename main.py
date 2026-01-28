import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# 1. Konfiguracja strony
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# 2. Link CSV
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

# 3. Wczytywanie danych z obsługą błędów
@st.cache_data(ttl=5)
def load_data():
    try:
        # Próba odczytu z wymuszeniem kodowania utf-8 i czyszczeniem
        df = pd.read_csv(URL).fillna("")
        return df
    except Exception:
        return pd.DataFrame()

df = load_data()

# --- STYLIZACJA CSS (Naprawa widoczności menu) ---
st.markdown("""
    <style>
    /* Odstęp na dole, żeby menu nic nie zasłaniało */
    .main { margin-bottom: 100px !important; }
    /* Styl dla paska wyszukiwania */
    div[data-baseweb="input"] { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- GLOBALNA WYSZUKIWARKA ---
st.write("### 🔍 Szukaj klienta")
# Dodajemy klucz 'search', aby Streamlit lepiej zarządzał stanem
search_query = st.text_input("Wyszukiwarka", placeholder="Wpisz np. 'war' dla Warszawy...", label_visibility="collapsed").lower()

# --- DOLNE MENU (Zawsze na wierzchu) ---
# Przeniesione tutaj, aby nie znikało przy wyszukiwaniu
selected = option_menu(
    menu_title=None,
    options=["Start", "Aktualności", "Klienci", "Telefony", "Zadania"],
    icons=["house", "lightning", "people", "telephone", "check2-square"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#111", "position": "fixed", "bottom": "0", "width": "100%", "z-index": "1000"},
        "icon": {"color": "orange", "font-size": "14px"}, 
        "nav-link": {"font-size": "10px", "text-align": "center", "margin":"0px", "color": "white"},
        "nav-link-selected": {"background-color": "#333"},
    }
)

if not df.empty:
    # 4. LOGIKA WYŚWIETLANIA WYSZUKIWANIA
    if search_query:
        st.write("---")
        # Filtracja fragmentów tekstu (case-insensitive)
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        df_results = df[mask]
        
        if not df_results.empty:
            for index, row in df_results.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{row.iloc[0]}** | {row.iloc[3]}")
                    with col2:
                        if st.button("Otwórz", key=f"src_{index}"):
                            st.session_state['selected_client'] = row
                            st.switch_page("pages/details.py")
            st.write("---")
        else:
            st.info("Brak pasujących wyników.")

    # --- ZAKŁADKI ---
    if selected == "Start":
        st.header("🏗️ W realizacji")
        if 'Status' in df.columns:
            df_active = df[df['Status'] == "W realizacji"]
            if not df_active.empty:
                cols = st.columns(2)
                for i, (index, row) in enumerate(df_active.iterrows()):
                    # Kolorystyka
                    typ = str(row.get('Typ pracy', '')).lower()
                    color = "#FF4B4B" if "malowanie" in typ else "#00CC96" if "elewacja" in typ else "#636EFA" if "przekrywka" in typ else "#31333F"
                    
                    with cols[i % 2]:
                        st.markdown(f"""
                            <div style="background-color:{color}; padding:15px; border-radius:10px; color:white; margin-bottom:10px; min-height:100px;">
                                <div style="font-weight:bold; font-size:16px;">{row.iloc[0]}</div>
                                <div style="font-size:12px; opacity:0.9;">📍 {row.iloc[3]}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Szczegóły", key=f"start_{index}", use_container_width=True):
                            st.session_state['selected_client'] = row
                            st.switch_page("pages/details.py")
            else:
                st.info("Brak aktywnych zleceń (zmień status w arkuszu na 'W realizacji')")

    elif selected == "Aktualności":
        st.header("⚡ Ostatnie rozmowy")
        # Pokazuje 10 najnowszych wpisów z esencją
        df_recent = df.iloc[::-1].head(10)
        for index, row in df_recent.iterrows():
            with st.expander(f"📌 {row.iloc[0]} - {row.iloc[3]}"):
                st.write(f"📞 {row.iloc[6]}")
                st.info(f"💡 Esencja: {row.iloc[9]}")
                if st.button("Karta klienta", key=f"news_{index}"):
                    st.session_state['selected_client'] = row
                    st.switch_page("pages/details.py")

    elif selected == "Klienci":
        st.header("👥 Baza klientów")
        st.dataframe(df.iloc[::-1], use_container_width=True)

else:
    st.error("Nie udało się załadować bazy. Sprawdź Udostępnianie -> Każdy z linkiem (Przeglądający)")
