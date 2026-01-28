import streamlit as st
import pandas as pd

# Ustawienia strony
st.set_page_config(page_title="Dekarz CRM", layout="wide")

# Link do Arkusza
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

@st.cache_data(ttl=5)
def load_data():
    try:
        # Wczytujemy dane, ignorując błędy formatowania
        df = pd.read_csv(URL, on_bad_lines='skip', engine='python')
        # Usuwamy puste znaki z nazw kolumn i samych danych
        df.columns = df.columns.str.strip()
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        return df
    except Exception as e:
        st.error(f"Błąd połączenia z bazą: {e}")
        return pd.DataFrame()

df = load_data()

# --- MENU GÓRNE (Zamiast bocznego) ---
st.markdown("### 🛠️ Menu")
m1, m2, m3 = st.columns(3)
with m1:
    btn_start = st.button("🏗️ START", use_container_width=True)
with m2:
    btn_klienci = st.button("👥 KLIENCI", use_container_width=True)
with m3:
    btn_zadania = st.button("✅ ZADANIA", use_container_width=True)

# Zarządzanie zakładkami przez przyciski
if 'view' not in st.session_state:
    st.session_state.view = "Start"
if btn_start: st.session_state.view = "Start"
if btn_klienci: st.session_state.view = "Klienci"
if btn_zadania: st.session_state.view = "Zadania"

st.divider()

# --- GLOBALNA WYSZUKIWARKA (Zawsze widoczna) ---
search_query = st.text_input("🔍 Szukaj (wpisz min. 3 litery):", placeholder="Nazwisko, miasto, ulica...").lower()

if not df.empty:
    # 1. LOGIKA WYSZUKIWANIA
    if len(search_query) > 2:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        results = df[mask]
        
        if not results.empty:
            st.success(f"Znaleziono: {len(results)}")
            for i, row in results.iterrows():
                with st.expander(f"👤 {row.iloc[0]} | 📍 {row.iloc[3]}"):
                    st.write(f"📞 Tel: {row.iloc[6]}")
                    if st.button("Otwórz kartę", key=f"s_{i}"):
                        st.session_state.selected_client = row
                        st.switch_page("pages/details.py")
            st.divider()

    # 2. WIDOKI ZAKŁADEK
    if st.session_state.view == "Start":
        st.subheader("🏗️ Budowy w realizacji")
        
        # Sprawdzamy kolumnę L (zazwyczaj indeks 11) lub szukamy nazwy "Status"
        # Przeszukujemy wszystkie kolumny w poszukiwaniu frazy "W realizacji"
        active_df = df[df.apply(lambda row: row.astype(str).str.contains("W realizacji", case=False).any(), axis=1)]
        
        if not active_df.empty:
            for i, row in active_df.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row.iloc[0]}**")
                    st.caption(f"📍 {row.iloc[3]}")
                    if st.button("Pokaż szczegóły", key=f"act_{i}", use_container_width=True):
                        st.session_state.selected_client = row
                        st.switch_page("pages/details.py")
        else:
            st.warning("Nie znaleziono statusu 'W realizacji'. Upewnij się, że w Arkuszu (kolumna L) wpisane jest dokładnie to hasło.")
            # Pomocniczy podgląd dla Ciebie (usuń po naprawie)
            with st.expander("Podgląd surowych danych (tylko kolumna L)"):
                st.write(df.iloc[:, 11].unique() if df.shape[1] > 11 else "Brak kolumny L")

    elif st.session_state.view == "Klienci":
        st.subheader("👥 Wszystkie kontakty")
        st.dataframe(df, use_container_width=True)

else:
    st.error("Baza danych jest pusta lub link nie działa.")
