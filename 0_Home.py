import streamlit as st

# Reading CSS
with open('styles.css') as stl:
    st.markdown(f'<style>{stl.read()}</style>', 
                unsafe_allow_html=True)
    
# Intro text
st.title('Feedback AI automático')

st.markdown(
    '''
    <p class='jtext'>
    Esta es una app interactiva diseñada para extraer y procesar las grabaciones de las tutorías
    de matemáticas en Paraguay.
    </p>

    <p class='jtext'>
    Si tienes preguntas, sugerencias o necesitas reportar un bug en la app, puedes mandar un email a
    <b style="color:#003249">carlos.toruno@gmail.com</b>. El código en python de esta app está disponible
    en <a href="https://github.com/ctoruno/ROLI-Map-App" target="_blank" style="color:#003249"><b>este repositorio de GitHub</b></a>.
    </p>
    ''',
    unsafe_allow_html = True
)

st.markdown("""---""")
