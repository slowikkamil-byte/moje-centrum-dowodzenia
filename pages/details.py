import streamlit as st

# Sprawdzamy, czy wybrano klienta na stronie głównej
if 'selected_client' not in st.session_state:
    st.warning("Wróć do strony głównej i wybierz klienta.")
    if st.button("⬅️ Powrót"):
        st.switch_page("main.py")
else:
    c = st.session_state['selected_client']
    
    st.title(f"👤 {c.iloc[0]}") # Nazwisko
    
    # Przycisk ZADZWOŃ - duży i widoczny
    numer = str(c.iloc[6])
    st.link_button(f"📞 ZADZWOŃ: {numer}", f"tel:{numer}", use_container_width=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"📍 **Adres:** {c.iloc[3]}")
        st.write(f"🏷️ **Status:** {c['Status']}")
    with col2:
        st.write(f"🏗️ **Typ pracy:** {c['Typ pracy']}")
        st.write(f"💰 **Wycena:** {c.get('Wycena', 'Brak')}")

    st.divider()
    
    # Odtwarzacz rozmowy (Kolumna O)
    st.subheader("🎙️ Ostatnia rozmowa")
    nagranie_url = c.iloc[14] # Kolumna O (indeks 14)
    if isinstance(nagranie_url, str) and "drive.google.com" in nagranie_url:
        # Przerabiamy link drive na bezpośredni do odtwarzacza
        file_id = nagranie_url.split('/')[-2]
        direct_url = f"https://docs.google.com/uc?export=download&id={file_id}"
        st.audio(direct_url)
    else:
        st.info("Brak dostępnego nagrania.")

    st.divider()
    
    st.subheader("📝 Notatka (Esencja)")
    st.info(c.iloc[9]) # Esencja

    # Miejsce na wpisanie wyceny
    st.subheader("✍️ Twoja wycena")
    nowa_wycena = st.text_area("Wpisz ustalenia finansowe:", value=str(c.get('Wycena', '')))
    
    if st.button("💾 Zapisz zmiany (Wkrótce)"):
        st.success("W następnym kroku połączymy ten przycisk z n8n, aby zapisał to w Twoim arkuszu!")

    if st.button("⬅️ Powrót do listy"):
        st.switch_page("main.py")
