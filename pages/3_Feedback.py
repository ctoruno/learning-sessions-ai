import streamlit as st
import pandas as pd
from tools import gd_access as gd
from tools import ai

# Instatiating a Google Service to connect with GDrive
creds = gd.get_gd_info(
    st.secrets['gd_token'],
    st.secrets['gd_rtoken'],
    st.secrets['gd_cid'],
    st.secrets['gd_csecret']
)
gd_service = gd.create_service(creds)

# Intro text
st.markdown(
    '''
    <h3>
    Paso 3: Procesa la transcripción para recibir un feedback
    </h3>
    <p class='jtext'>
    El tercer paso es procesar las transcripciones procesadas en el paso anterior. No obstante, antes de proceder, 
    <b>asegurate de que las transcripciones fueron procesadas correctamente en el paso 2</b>. A continuación, se muestra
    un listado de las transcripciones que están disponibles para ser procesadas
    </p>
    ''',
    unsafe_allow_html = True
)

if "trids" in st.session_state:
    available_trs = st.session_state.trids
    st.write(available_trs)
    process_tr = st.button('Procesar información')

else:
    st.markdown("<b>No data found in session state.</b>", unsafe_allow_html = True)
    process_tr = False


if process_tr: 
    st.markdown(
        '<br><h5>INICIANDO PROCESO... Esto puede tardar unos momentos...</h5>',
        unsafe_allow_html = True
    )
    st.write('----')

    n_rows  = len(available_trs)
    counter = 1
    for name, id in available_trs.items():

        st.markdown(f'<h5>Processing transcript {counter} of {n_rows}: {name}</h5>', unsafe_allow_html = True)

        tr = gd.download_file(gd_service, id)
        feedback = ai.get_feedback(st.secrets['OPENAI_API_KEY'], tr)
        feed_name  = f'fb_{name}.txt'

        gd.upload_file(
            service    = gd_service, 
            file_name  = feed_name, 
            content    = feedback,
            type       = 'txt', 
            parent_id  = gd.buckets['test']    ## CHANGE!!!!!
        )
        st.write(f'Retroalimentación cargada a Google Drive')

        counter += 1
        st.write('----')