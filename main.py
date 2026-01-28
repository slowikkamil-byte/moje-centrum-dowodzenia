import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# 1. Konfiguracja strony pod telefon
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# 2. Link CSV
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

@st.cache_data(ttl=2) # Bardzo krótkie cache dla dynamiki
def load_data():
    try:
        df = pd.read_csv(URL).fillna("")
        return df
    except:
        return pd.DataFrame()

df = load_data()

# --- STYLIZACJA CSS (Wizualizacja: Nowoczesne Menu na dole) ---
st.markdown("""
    <style>
    .main { margin-bottom: 80px; }
    div[data-baseweb="input"] { border-radius: 20px; border: 1px solid #ffaa00; }
    .stButton>button { border-radius: 10px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- GLOBALNA WYSZUKIWARKA (Zawsze na górze) ---
search_query = st.text_input("🔍 Szukaj klienta...", placeholder="Wpisz miasto, nazwisko lub ulica (np. war...)", key="main_search").lower()

if not df.empty:
    # FILTROWANIE DYNAMICZNE
    if search_query:
        # To szuka fragmentów tekstu w każdej kolumnie
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        df_results = df[mask]
        
        if not df_results.empty:
            st.markdown(f"**Wyniki wyszukiwania ({len(df_results)}):**")
            for index, row in df_results.iterrows():
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{row.iloc[0]}** | 📍 {row.iloc[3]}")
                    with col2:
                        if st.button("Karta", key=f"src_{index}"):
                            st.session_state['selected_client'] = row
                            st.switch_page("pages/details.py")
            st.divider()

    # --- NOWOCZESNE MENU DOLNE (Jak na Twojej wizualizacji) ---
    selected = option_menu(
        menu_title=None,
        options=["Start", "Aktualności", "Klienci", "Telefony", "Zadania"],
        icons=["house", "lightning-charge", "people", "telephone", "check2-square"],
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#111", "position": "fixed", "bottom": "0", "width": "100%", "z-index": "1000"},
            "icon": {"color": "#ffaa00", "font-size": "20px"}, 
            "nav-link": {"font-size": "10px", "text-align": "center", "margin":"0px", "color": "white", "padding": "10px 0px"},
            "nav-link-selected": {"background-color": "#222", "border-top": "2px solid #ffaa00"},
        }
    )

    # --- ZAKŁADKI ---
    if selected == "Start":
        st.header("🏗️ W realizacji")
        df_active = df[df['Status'] == "W realizacji"] if 'Status' in df.columns else pd.DataFrame()
        
        if not df_active.empty:
            cols = st.columns(2)
            for i, (index, row) in enumerate(df_active.iterrows()):
                typ = str(row.get('Typ pracy', '')).lower()
                color = "#FF4B4B" if "malowanie" in typ else "#00CC96" if "elewacja" in typ else "#636EFA" if "przekrywka" in typ else "#31333F"
                
                with cols[i % 2]:
                    st.markdown(f"""
                        <div style="background-color:{color}; padding:15px; border-radius:12px; color:white; min-height:100px; margin-bottom:5px;">
                            <div style="font-weight:bold; font-size:16px;">{row.iloc[0]}</div>
                            <div style="font-size:12px; opacity:0.9;">📍 {row.iloc[3]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Otwórz", key=f"st_{index}", use_container_width=True):
                        st.session_state['selected_client'] = row
                        st.switch_page("pages/details.py")
        else:
            st.info("Brak prac 'W realizacji'.")

    elif selected == "Aktualności":
        st.header("⚡ Ostatnie rozmowy")
        # 10 najnowszych (od końca arkusza)
        df_recent = df.iloc[::-1].head(10)
        for index, row in df_recent.iterrows():
            with st.container():
                st.markdown(f"**{row.iloc[0]}** | {row.iloc[3]}")
                st.info(f"💡 {row.iloc[9]}") # Esencja
                if st.button("Szczegóły", key=f"news_{index}"):
                    st.session_state['selected_client'] = row
                    st.switch_page("pages/details.py")
                st.divider()

    elif selected == "Klienci":
        st.header("👥 Baza klientów")
        st.dataframe(df.iloc[::-1], use_container_width=True)

else:
    st.error("Problem z bazą danych. Sprawdź Udostępnianie Arkusza!")
