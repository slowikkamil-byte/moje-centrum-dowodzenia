import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# 1. Konfiguracja strony
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# 2. Link CSV
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

# 3. Wczytywanie danych
@st.cache_data(ttl=5) # Częstsze odświeżanie dla lepszej responsywności
def load_data():
    try:
        df = pd.read_csv(URL)
        # Czyszczenie danych z pustych wartości, żeby wyszukiwarka się nie zawieszała
        df = df.fillna("")
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# --- STYLIZACJA (Poprawka menu i odstępów) ---
st.markdown("""
    <style>
    .main { margin-bottom: 70px; }
    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- GLOBALNA WYSZUKIWARKA ---
# Pasek wyszukiwania na samym górze
search_query = st.text_input("🔍 Szukaj klienta...", placeholder="Zacznij pisać (miasto, nazwisko, ulica)...").lower()

if not df.empty:
    # 4. LOGIKA FILTROWANIA (Reaguje na każdą literę)
    if search_query:
        # Przeszukiwanie wszystkich kolumn jednocześnie
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        df_results = df[mask]
        
        if not df_results.empty:
            st.subheader(f"🔎 Wyniki ({len(df_results)})")
            for index, row in df_results.iterrows():
                # Tworzymy czytelny kafelek wyniku
                with st.container():
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.markdown(f"**{row.iloc[0]}** | 📍 {row.iloc[3]} | 📞 {row.iloc[6]}")
                    with col_b:
                        if st.button("Karta", key=f"src_{index}"):
                            st.session_state['selected_client'] = row
                            st.switch_page("pages/details.py")
            st.divider()
        else:
            st.warning("Brak wyników dla tej frazy.")

    # --- DOLNE MENU ---
    # Menu jest poza blokiem wyszukiwania, więc zawsze się wyświetli
    selected = option_menu(
        menu_title=None,
        options=["Start", "Aktualności", "Klienci", "Telefony", "Zadania"],
        icons=["house", "lightning", "people", "telephone", "check2-square"],
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#111", "position": "fixed", "bottom": "0"},
            "icon": {"color": "orange", "font-size": "14px"}, 
            "nav-link": {"font-size": "10px", "text-align": "center", "margin":"0px"},
            "nav-link-selected": {"background-color": "#444"},
        }
    )

    # --- ZAKŁADKI ---
    if selected == "Start":
        st.header("🏗️ W realizacji")
        if 'Status' in df.columns:
            df_active = df[df['Status'] == "W realizacji"]
            if not df_active.empty:
                cols = st.columns(2)
                for i, (index, row) in enumerate(df_active.iterrows()):
                    typ = str(row.get('Typ pracy', '')).lower()
                    color = "#FF4B4B" if "malowanie" in typ else "#00CC96" if "elewacja" in typ else "#636EFA" if "przekrywka" in typ else "#31333F"
                    
                    with cols[i % 2]:
                        st.markdown(f"""
                            <div style="background-color:{color}; padding:10px; border-radius:10px; color:white; margin-bottom:5px;">
                                <strong>{row.iloc[0]}</strong><br><small>{row.iloc[3]}</small>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Szczegóły", key=f"start_{index}"):
                            st.session_state['selected_client'] = row
                            st.switch_page("pages/details.py")
            else:
                st.info("Brak aktywnych zleceń.")

    elif selected == "Aktualności":
        st.header("⚡ Ostatnie rozmowy")
        df_recent = df.iloc[::-1].head(10)
        for index, row in df_recent.iterrows():
            with st.expander(f"📌 {row.iloc[0]} - {row.iloc[3]}"):
                st.write(f"📞 {row.iloc[6]}")
                st.info(f"💡 {row.iloc[9]}")
                if st.button("Otwórz", key=f"news_{index}"):
                    st.session_state['selected_client'] = row
                    st.switch_page("pages/details.py")

    elif selected == "Klienci":
        st.header("👥 Pełna baza")
        st.dataframe(df.iloc[::-1], use_container_width=True)

else:
    st.error("Problem z bazą danych lub Arkusz jest pusty.")
