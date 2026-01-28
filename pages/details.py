import streamlit as st
import pandas as pd

# 1. Sprawdzanie wyboru klienta
if 'selected_client' not in st.session_state:
    st.warning("⚠️ Nie wybrano klienta!")
    if st.button("⬅️ Powrót"):
        st.switch_page("main.py")
    st.stop()

client = st.session_state['selected_client']
client_name = str(client.iloc[0])

# Stylizacja przycisku
st.markdown("""
    <style>
    .stDownloadButton, .stButton button {
        border-radius: 12px;
        height: 4em;
        font-weight: bold;
    }
    .form-button {
        background-color: #673ab7 !important;
        color: white !important;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        text-decoration: none;
        display: block;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title(f"👤 {client_name}")
st.caption(f"📍 {client.iloc[3]} | 📞 {client.iloc[6]}")
st.divider()

# SEKCJA NOTATEK
st.subheader("📝 Notatki i Wycena")
st.info("Tutaj możesz zapisać swoje uwagi (notatka zostanie w aplikacji do czasu odświeżenia).")
note = st.text_area("Twoje spostrzeżenia z dachu:", placeholder="Opisz stan dachu, wymiary...")

if st.button("💾 ZAPISZ NOTATKĘ LOKALNIE"):
    st.success("Notatka została tymczasowo zapamiętana!")

st.divider()

# SEKCJA MULTIMEDIÓW - ROZWIĄZANIE PROBLEMU
st.subheader("📸 Zdjęcia i Nagrania")
st.write("Aby dodać zdjęcia lub nagrania głosowe, kliknij poniższy przycisk. Przeniesie Cię on do bezpiecznego formularza Google, który nie blokuje przesyłu plików.")

# PODMIEŃ TEN LINK NA SWÓJ LINK DO FORMULARZA
form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfwVDwAYR4sfDJoVs0oW5vL3M03M28H_x_ap9ZL9IvH-k_Z-Q/viewform?usp=publish-editor"

st.link_button("🚀 OTWÓRZ APARAT / DODAJ PLIKI", form_url, use_container_width=True)

st.divider()

if st.button("⬅️ POWRÓT DO LISTY", use_container_width=True):
    st.switch_page("main.py")

with st.expander("📄 Dane klienta z arkusza"):
    st.write(client)
