uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, parents'
        ).execute()
        # DODAJ TĘ LINIĘ:
        st.write(f"DEBUG: Plik o ID {uploaded_file.get('id')} został wysłany do folderu o ID: {uploaded_file.get('parents')}")
