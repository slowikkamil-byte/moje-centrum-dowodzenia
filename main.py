import streamlit as st
import pandas as pd

# Konfiguracja strony dla telefonu
st.set_page_config(page_title="Centrum Dowodzenia", layout="wide")

st.title("🚀 Business Hub")

# Sekcja Live - Dane z Webhooka n8n
st.header("📞 Ostatnie Połączenie")
# Tu n8n będzie przesyłać dane przez API
call_data = {"klient": "Czekam na dane...", "notatka": "Brak nowych zdarzeń"}

with st.container():
    st.info(f"👤 **Klient:** {call_data['klient']}")
    st.warning(f"📝 **Ostatnia notatka:** {call_data['notatka']}")

st.divider()

# Sekcja Maili AI
st.header("📧 Ważne E-maile")
# Symulacja danych, które wyciągniesz z Google Sheets/n8n
emails = pd.DataFrame([
    {"Temat": "Zapytanie o ofertę", "Status": "🔴 WAŻNE"},
    {"Temat": "Faktura do opłacenia", "Status": "🟡 DO SPRAWDZENIA"}
])
st.table(emails)
