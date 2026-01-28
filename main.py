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
        if 'Status' in df.columns:
            df_active = df[df['Status'] == "W realizacji"]
        else:
            df_active = pd.DataFrame() # Pusta tabela jeśli nie ma jeszcze kolumny Status

        # Logika wyszukiwania
        if search_query and not df_active.empty:
            df_active = df_active[df_active.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        # Wyświetlanie kafelków
        if not df_active.empty:
            cols = st.columns(2)
            for index, row in df_active.iterrows():
                typ = str(row.get('Typ pracy', '')).lower()
                color = "#31333F"
                if "malowanie" in typ: color = "#FF4B4B"
                elif "elewacja" in typ: color = "#00CC96"
                elif "przekrywka" in typ: color = "#636EFA"

                with cols[index % 2]:
                    st.markdown(f"""
                    <div style="background-color:{color}; padding:20px; border-radius:15px; margin-bottom:10px;">
                        <h3 style="margin:0; color:white;">{row.iloc[0]}</h3>
                        <p style="margin:5px 0; color:white;">📍 {row.iloc[3]}</p>
                        <p style="margin:0; color:white;">📞 {row.iloc[6]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Szczegóły: {row.iloc[0]}", key=f"btn_{index}"):
                        st.session_state['selected_client'] = row
                        st.switch_page("pages/details.py")
        else:
            st.info("Brak zleceń o statusie 'W realizacji'.")

    elif selected == "Aktualności":
        st.header("⚡ Ostatnie rozmowy")
        if not df.empty:
            # Odwracamy kolejność, żeby najnowsze były na górze
            df_recent = df.iloc[::-1].head(10)
            for index, row in df_recent.iterrows():
                with st.expander(f"📌 {row.iloc[0]} - {row.iloc[3]}"):
                    st.write(f"📞 {row.iloc[6]}")
                    st.info(f"💡 Esencja: {row.iloc[9]}")
                    if st.button(f"Otwórz kartę: {row.iloc[0]}", key=f"news_{index}"):
                        st.session_state['selected_client'] = row
                        st.switch_page("pages/details.py")

    elif selected == "Klienci":
        st.header("👥 Pełna baza")
        st.dataframe(df.iloc[::-1], use_container_width=True)

except Exception as e:
    st.error(f"Czekam na połączenie z bazą... Błąd: {e}")
    st.info("Upewnij się, że udostępniłeś arkusz Google (Każdy z linkiem może przeglądać).")
