import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# 1. Konfiguracja strony
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# 2. Link CSV
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

# 3. Wczytywanie danych
@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(URL)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# --- GLOBALNA WYSZUKIWARKA (Zawsze widoczna) ---
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
search_query = st.text_input("🔍 Szybkie szukanie klienta...", placeholder="Wpisz nazwisko, miasto lub telefon...").lower()

if not df.empty:
    # Filtrowanie globalne
    if search_query:
        # Przeszukujemy wszystkie kolumny
        df_results = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
        
        st.subheader(f"🔎 Wyniki wyszukiwania ({len(df_results)})")
        if not df_results.empty:
            for index, row in df_results.iterrows():
                with st.expander(f"👤 {row.iloc[0]} - {row.iloc[3]}"):
                    st.write(f"📞 {row.iloc[6]}")
                    st.write(f"🏷️ Status: {row.get('Status', 'Nowy')}")
                    if st.button("Otwórz kartę", key=f"search_{index}"):
                        st.session_state['selected_client'] = row
                        st.switch_page("pages/details.py")
        else:
            st.warning("Nie znaleziono klienta o podanej frazie.")
        st.divider()

    # --- DOLNE MENU ---
    selected = option_menu(
        menu_title=None,
        options=["Start", "Aktualności", "Klienci", "Telefony", "Zadania"],
        icons=["house", "lightning", "people", "telephone", "check2-square"],
        orientation="horizontal",
        styles={
            "container": {"position": "fixed", "bottom": "0", "width": "100%", "z-index": "999"},
            "nav-link": {"font-size": "10px", "padding": "5px"},
        }
    )

    # --- LOGIKA ZAKŁADEK ---
    if selected == "Start":
        st.header("🏗️ W realizacji")
        df_active = df[df['Status'] == "W realizacji"] if 'Status' in df.columns else pd.DataFrame()
        
        if not df_active.empty:
            cols = st.columns(2)
            for index, row in df_active.reset_index().iterrows():
                typ = str(row.get('Typ pracy', '')).lower()
                color = "#FF4B4B" if "malowanie" in typ else "#00CC96" if "elewacja" in typ else "#636EFA" if "przekrywka" in typ else "#31333F"
                
                with cols[index % 2]:
                    st.markdown(f'<div style="background-color:{color}; padding:15px; border-radius:10px; margin-bottom:10px; color:white;">'
                                f'<strong>{row.iloc[1]}</strong><br><small>📍 {row.iloc[4]}</small></div>', unsafe_allow_html=True)
                    if st.button("Szczegóły", key=f"active_{index}"):
                        st.session_state['selected_client'] = row
                        st.switch_page("pages/details.py")
        else:
            st.info("Brak aktywnych prac.")

    elif selected == "Aktualności":
        st.header("⚡ Ostatnie rozmowy")
        # Wyświetlamy 10 najnowszych (od góry arkusza po odwróceniu)
        df_recent = df.iloc[::-1].head(10)
        for index, row in df_recent.reset_index().iterrows():
            with st.container():
                st.markdown(f"**{row.iloc[1]}** - {row.iloc[4]}")
                st.caption(f"📞 {row.iloc[7]}")
                st.info(f"💡 {row.iloc[10]}") # Esencja
                if st.button("Pokaż więcej", key=f"news_{index}"):
                    st.session_state['selected_client'] = row
                    st.switch_page("pages/details.py")
                st.divider()

    elif selected == "Klienci":
        st.header("👥 Baza klientów")
        st.dataframe(df.iloc[::-1], use_container_width=True)

else:
    st.error("Brak połączenia z Arkuszem. Sprawdź udostępnianie!")
