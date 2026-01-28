import streamlit as st
import pandas as pd

# 1. Konfiguracja strony
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# 2. Link do danych (CSV)
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        # Wczytujemy dane i czyścimy puste pola
        data = pd.read_csv(URL).fillna("")
        return data
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# --- NAWIGACJA (Zastępujemy option_menu bezpiecznym paskiem bocznym) ---
with st.sidebar:
    st.header("MENU")
    selected = st.radio(
        "Wybierz zakładkę:",
        ["Start", "Aktualności", "Klienci", "Telefony", "Zadania"],
        index=0
    )

# --- GLOBALNA WYSZUKIWARKA ---
st.write("### 🔍 Szukaj")
# Używamy on_change, aby wymusić reakcję, ale w Streamlit tekst wysyła się po zmianie fokusu lub Enter. 
# Aby było dynamicznie "co literę", Streamlit wymagałby dodatkowych komponentów, 
# ale sprawdzimy czy ten filtr fragmentów (contains) teraz ruszy:
search_query = st.text_input("Wpisz fragment frazy (np. nazwisko lub miasto):", key="main_search").lower()

if not df.empty:
    # FILTROWANIE DYNAMICZNE (Fragmenty tekstu)
    if search_query:
        # Szukamy fragmentu (np. "war" znajdzie "Warszawa")
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        df_results = df[mask]
        
        if not df_results.empty:
            st.success(f"Znaleziono: {len(df_results)}")
            for index, row in df_results.iterrows():
                with st.expander(f"👤 {row.iloc[0]} | {row.iloc[3]}"):
                    st.write(f"📞 {row.iloc[6]}")
                    if st.button("Otwórz Kartę", key=f"src_{index}"):
                        st.session_state['selected_client'] = row
                        st.switch_page("pages/details.py")
            st.divider()

    # --- ZAKŁADKI ---
    if selected == "Start":
        st.header("🏗️ W realizacji")
        # Sprawdzamy czy kolumna Status istnieje (indeks 11 to kolumna L)
        if 'Status' in df.columns:
            df_active = df[df['Status'] == "W realizacji"]
            if not df_active.empty:
                cols = st.columns(2)
                for i, (index, row) in enumerate(df_active.iterrows()):
                    # Kolory w zależności od kolumny M (Typ pracy)
                    typ = str(row.get('Typ pracy', '')).lower()
                    color = "#FF4B4B" if "malowanie" in typ else "#00CC96" if "elewacja" in typ else "#636EFA" if "przekrywka" in typ else "#31333F"
                    
                    with cols[i % 2]:
                        st.markdown(f"""
                            <div style="background-color:{color}; padding:15px; border-radius:10px; color:white; margin-bottom:10px;">
                                <strong>{row.iloc[0]}</strong><br>📍 {row.iloc[3]}
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Szczegóły", key=f"st_{index}", use_container_width=True):
                            st.session_state['selected_client'] = row
                            st.switch_page("pages/details.py")
            else:
                st.info("Brak zleceń 'W realizacji'.")

    elif selected == "Aktualności":
        st.header("⚡ Ostatnie rozmowy")
        df_recent = df.iloc[::-1].head(10)
        for index, row in df_recent.iterrows():
            with st.container():
                st.write(f"**{row.iloc[0]}** | {row.iloc[3]}")
                st.caption(f"💡 {row.iloc[9]}") # Esencja
                if st.button("Karta", key=f"news_{index}"):
                    st.session_state['selected_client'] = row
                    st.switch_page("pages/details.py")
                st.divider()

    elif selected == "Klienci":
        st.header("👥 Baza klientów")
        st.dataframe(df.iloc[::-1], use_container_width=True)

else:
    st.error("Błąd ładowania danych. Sprawdź czy Arkusz jest udostępniony 'Każdy z linkiem'.")
