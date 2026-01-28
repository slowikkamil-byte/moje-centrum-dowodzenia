import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dekarz CRM", layout="wide", page_icon="🏠")

# Link do Twojego Arkusza w formacie CSV
URL = "https://docs.google.com/spreadsheets/d/1lR3he8b7zSmtd1OyMwV_O8CfBITlbPSUrZaoC_9cxQo/export?format=csv"

st.title("⚒️ System Zarządzania Zleceniami")

try:
    # Wczytywanie danych
    df = pd.read_csv(URL)
    
    # Wyświetlanie ostatniego zlecenia jako duża karta
    if not df.empty:
        ostatnie = df.iloc[-1]
        st.subheader("🔔 Najnowsze ustalenia")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Klient", ostatnie.iloc[0]) # Zakładam, że Nazwisko to 1 kolumna
            st.write(f"📍 **Adres:** {ostatnie.iloc[3]}")
        with col2:
            st.metric("Termin", ostatnie.iloc[4])
            st.write(f"📞 **Telefon:** {ostatnie.iloc[6]}")
        
        st.info(f"💡 **Esencja:** {ostatnie.iloc[9]}") # Pole Esencja

    st.divider()
    st.header("📋 Pełna lista zleceń")
    st.dataframe(df.iloc[::-1], use_container_width=True) # Odwrócona kolejność (najnowsze na górze)

except Exception as e:
    st.error(f"Czekam na dane z arkusza... (Upewnij się, że arkusz nie jest pusty)")

# Automatyczne odświeżanie co 30 sekund
st.empty()
st.caption("Dane aktualizują się automatycznie co 30 sekund.")
