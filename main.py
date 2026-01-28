import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# 1. Konfiguracja strony
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# 2. Link CSV (Twój link z końcówką export)
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

# 3. Wczytywanie danych
@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(URL)
        return df
    except Exception as e:
        st.error(f"Nie udało się pobrać danych: {e}")
        return pd.DataFrame()

# 4. Logika aplikacji
df = load_data()

if not df.empty:
    # --- PASEK WYSZUKIWANIA ---
    search_query = st.text_input("🔍 Szukaj (ulica, miasto, nazwisko...)", "").lower()

    # --- DOLNE MENU ---
    selected = option_menu(
        menu_title=None,
        options=["Start", "Aktualności", "Klienci", "Telefony", "Zadania"],
        icons=["house", "lightning", "people", "telephone", "check2-square"],
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#111"},
            "icon": {"color": "orange", "font-size": "18px"}, 
            "nav-link": {"font-size": "12px", "text-align": "center", "margin":"0px"},
            "nav-link-selected": {"background-color": "#444"},
        }
    )

    if selected == "Start":
        st.header("🏗️ W realizacji")
        
        # Filtrowanie
        if 'Status' in df.columns:
            df_active = df[df['Status'] == "W realizacji"]
        else:
            df_active = pd.DataFrame()

        if search_query and not df_active.empty:
            df_active = df_active[df_active.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        if not df_active.empty:
            cols = st.columns(2)
            for index, row in df_active.reset_index().iterrows():
                typ = str(row.get('Typ pracy', '')).lower()
                color = "#31333F"
                if "malowanie" in typ: color = "#FF4B4B"
                elif "elewacja" in typ: color = "#00CC96"
                elif "przekrywka" in typ: color = "#636EFA"

                with cols[index % 2]:
                    st.markdown(f"""
                    <div style="background-color:{color}; padding:15px; border-radius:10px; margin-bottom:10px; min-height:150px; border: 1px solid #555">
                        <h4 style="margin:0; color:white;">{row.iloc[1]}</h4>
                        <p style="font-size:12px; margin:5px 0; color:#ddd;">📍 {row.iloc[4]}</p>
                        <p style="font-size:12px; margin:0; color:#ddd;">📞 {row.iloc[7]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Otwórz: {row.iloc[1]}", key=f"active_{index}"):
                        st.session_state['selected_client'] = row
                        st.switch_page("pages/details.py")
        else:
            st.info("Brak aktywnych zleceń 'W realizacji'.")

    elif selected == "Aktualności":
        st.header("⚡ Ostatnie rozmowy")
        df_recent = df.iloc[::-1].head(10)
        for index, row in df_recent.reset_index().iterrows():
            with st.expander(f"📌 {row.iloc[1]} - {row.iloc[4]}"):
                st.write(f"📞 {row.iloc[7]}")
                st.info(f"💡 Esencja: {row.iloc[10]}")
                if st.button("Szczegóły klienta", key=f"news_{index}"):
                    st.session_state['selected_client'] = row
                    st.switch_page("pages/details.py")

    elif selected == "Klienci":
        st.header("👥 Pełna baza")
        st.dataframe(df.iloc[::-1], use_container_width=True)

else:
    st.warning("Baza danych jest pusta lub link do Arkusza jest niepoprawny.")
    st.info("Upewnij się, że w Arkuszu Google ustawiono: Udostępnij -> Każda osoba mająca link (Przeglądający).")
