import streamlit as st
import pandas as pd

# 1. Ustawienia strony
st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# 2. Bezpieczne wczytywanie danych
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        # engine='python' i on_bad_lines rozwiązują błąd ParserError
        df = pd.read_csv(URL, on_bad_lines='skip', engine='python').fillna("")
        df.columns = df.columns.str.strip() # Czyścimy nazwy kolumn
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# --- STYLIZACJA WIZUALNA ---
st.markdown("""
    <style>
    /* Zaokrąglone kafelki i wyszukiwarka */
    div[data-baseweb="input"] { border-radius: 15px !important; }
    .stAlert { border-radius: 15px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    /* Styl przycisku 'Otwórz' */
    .stButton>button { border-radius: 10px; width: 100%; border: 1px solid #ffaa00; }
    </style>
    """, unsafe_allow_html=True)

# --- STANDARDOWE, CZYTELNE MENU ---
with st.sidebar:
    st.title("🏗️ Nawigacja")
    selected = st.radio(
        "Wybierz sekcję:",
        ["🏠 Start", "⚡ Aktualności", "👥 Klienci", "📞 Telefony", "✅ Zadania"],
        label_visibility="collapsed"
    )
    st.divider()
    st.info("Baza odświeża się co 5 sekund.")

# --- GŁÓWNA WYSZUKIWARKA (Zawsze na górze) ---
search_query = st.text_input("🔍 Szukaj klienta...", placeholder="Wpisz nazwisko, miasto lub ulicę...").lower()

if not df.empty:
    # FILTROWANIE GLOBALNE
    if search_query:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        results = df[mask]
        if not results.empty:
            st.subheader(f"🔎 Wyniki wyszukiwania ({len(results)})")
            for i, row in results.iterrows():
                with st.expander(f"👤 {row.iloc[0]} | 📍 {row.iloc[3]}"):
                    st.write(f"📞 Telefon: {row.iloc[6]}")
                    if st.button("Otwórz kartę", key=f"search_{i}"):
                        st.session_state.selected_client = row
                        st.switch_page("pages/details.py")
            st.divider()

    # --- OBSŁUGA ZAKŁADEK ---
    if "Start" in selected:
        st.header("🏗️ W realizacji")
        
        # Sprawdzamy czy kolumna Status istnieje
        status_col = 'Status' if 'Status' in df.columns else None
        
        if status_col:
            # Filtrujemy rekordy
            active_df = df[df[status_col].astype(str).str.contains("W realizacji", case=False)]
            
            if not active_df.empty:
                # Wyświetlamy kafelki
                for i, row in active_df.iterrows():
                    with st.container():
                        # Kafelek wizualny
                        st.info(f"**{row.iloc[0]}**\n\n📍 {row.iloc[3]}")
                        if st.button(f"Szczegóły: {row.iloc[0]}", key=f"active_{i}"):
                            st.session_state.selected_client = row
                            st.switch_page("pages/details.py")
                        st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.warning("Nie znaleziono zleceń ze statusem 'W realizacji'. Sprawdź kolumnę L w Arkuszu.")
        else:
            st.error("Błąd: Nie znaleziono kolumny 'Status' w Twoim Arkuszu.")

    elif "Aktualności" in selected:
        st.header("⚡ Ostatnie rozmowy")
        for i, row in df.iloc[::-1].head(10).iterrows():
            with st.chat_message("user"):
                st.write(f"**{row.iloc[0]}** - {row.iloc[3]}")
                st.caption(f"💡 Esencja: {row.iloc[9]}")

    elif "Klienci" in selected:
        st.header("👥 Pełna baza")
        st.dataframe(df, use_container_width=True)

else:
    st.error("Nie udało się pobrać danych. Sprawdź, czy link do Arkusza jest poprawny i czy ma status 'Każdy z linkiem może przeglądać'.")
