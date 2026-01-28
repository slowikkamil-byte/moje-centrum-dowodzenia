import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu # Dodaj to do requirements.txt

# Konfiguracja strony
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# Link CSV (pamiętaj o końcówce export?format=csv)
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

# Wczytywanie danych
@st.cache_data(ttl=10) # Odświeżaj co 10 sekund
def load_data():
    df = pd.read_csv(URL)
    return df

try:
    df = load_data()
    
    # --- PASEK WYSZUKIWANIA ---
    search_query = st.text_input("🔍 Szukaj (ulica, miasto, nazwisko, telefon...)", "").lower()

    # --- DOLNE MENU (Nawigacja) ---
    selected = option_menu(
        menu_title=None,
        options=["Start", "Aktualności", "Klienci", "Telefony", "Zadania"],
        icons=["house", "lightning", "people", "telephone", "check2-square"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#111"},
            "icon": {"color": "orange", "font-size": "18px"}, 
            "nav-link": {"font-size": "14px", "text-align": "center", "margin":"0px", "--hover-color": "#333"},
            "nav-link-selected": {"background-color": "#444"},
        }
    )

    if selected == "Start":
        st.header("🏗️ W realizacji")
        
        # Filtrowanie po statusie "W realizacji"
        df_active = df[df['Status'] == "W realizacji"]
        
        # Logika wyszukiwania
        if search_query:
            df_active = df_active[df_active.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        # Wyświetlanie kafelków
        cols = st.columns(2) # 2 kafelki w rzędzie na telefonie
        for index, row in df_active.iterrows():
            # Kolorystyka w zależności od Typu Pracy
            typ = str(row['Typ pracy']).lower()
            color = "#31333F" # Standard
            if "malowanie" in typ: color = "#FF4B4B"
            elif "elewacja" in typ: color = "#00CC96"
            elif "przekrywka" in typ: color = "#636EFA"

            with cols[index % 2]:
                st.markdown(f"""
                <div style="background-color:{color}; padding:20px; border-radius:15px; margin-bottom:10px; cursor:pointer;">
                    <h3 style="margin:0;">{row.iloc[0]}</h3>
                    <p style="margin:5px 0;">📍 {row.iloc[3]}</p>
                    <p style="margin:0;">📞 {row.iloc[6]}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Szczegóły: {row.iloc[0]}", key=index):
                    st.session_state['selected_client'] = row
                    st.switch_page("pages/details.py") # Przejście do szczegółów

  elif selected == "Aktualności":
        st.header("⚡ Ostatnie rozmowy")
        # Wyświetlamy 5 najnowszych wpisów (od dołu arkusza)
        if not df.empty:
            for i in range(len(df)-1, max(-1, len(df)-6), -1):
                row = df.iloc[i]
                with st.expander(f"📌 {row.iloc[0]} - {row.iloc[3]}"):
                    st.write(f"📞 {row.iloc[6]}")
                    st.info(f"💡 Esencja: {row.iloc[9]}")
        else:
            st.info("Brak danych w arkuszu.")
