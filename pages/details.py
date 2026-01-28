import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Sprawdzenie, czy klient został wybrany
if 'selected_client' not in st.session_state:
    st.error("Nie wybrano klienta! Wróć do strony głównej.")
    if st.button("⬅️ Powrót"):
        st.switch_page("main.py")
    st.stop()

client = st.session_state['selected_client']

# CSS dla mobilnej wygody
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; }
    .upload-box { border: 2px dashed #ffaa00; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# Nagłówek z danymi klienta
st.title(f"👤 {client.iloc[0]}")
st.caption(f"📍 {client.iloc[3]} | 📞 {client.iloc[6]}")

st.divider()

# --- SEKCJA: TWOJA WYCENA ---
st.subheader("📝 Twoja wycena")

# Notatka tekstowa
note = st.text_area("Dodatkowe uwagi / Notatka z dachu:", placeholder="Np. dachówka do wymiany, komin do obróbki...")

# Upload zdjęć i nagrań
st.info("📸 Wrzuć zdjęcie obliczeń lub 🎤 nagranie głosowe")
uploaded_files = st.file_uploader(
    "Wybierz pliki lub zrób zdjęcie/nagranie", 
    type=['jpg', 'png', 'jpeg', 'mp3', 'wav', 'm4a'], 
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# Podgląd przesłanych plików
if uploaded_files:
    st.write("### Podgląd do zapisu:")
    for uploaded_file in uploaded_files:
        if uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption=f"Foto: {uploaded_file.name}", width=200)
        elif uploaded_file.type.startswith('audio'):
            st.audio(uploaded_file)
        st.caption(f"Plik: {uploaded_file.name}")

st.divider()

# --- PRZYCISKI AKCJI ---
col1, col2 = st.columns(2)

with col1:
    if st.button("💾 Zapisz wszystko"):
        # Logika zapisu (Na razie symulacja - tutaj wejdzie funkcja wysyłki na GDrive)
        with st.spinner("Wysyłam dane do bazy i na dysk..."):
            # 1. Tutaj kod dopisujący notatkę do Arkusza Google
            # 2. Tutaj kod tworzący folder na GDrive i wrzucający pliki
            st.success("Wycena i pliki zapisane pomyślnie!")
            # st.switch_page("main.py")

with col2:
    if st.button("❌ Anuluj"):
        st.switch_page("main.py")

# Wyświetlenie pozostałych danych klienta (dla przypomnienia)
with st.expander("🔍 Pełne dane klienta"):
    st.write(client)
