import tempfile
from datetime import datetime
from io import StringIO
import streamlit as st
import pandas as pd
from tools import gd_access as gd
from tools import scto_access as scto
from tools import ai

# Instatiating a Google Service to connect with GDrive
creds = gd.get_gd_info(
    st.secrets['gd_token'],
    st.secrets['gd_rtoken'],
    st.secrets['gd_cid'],
    st.secrets['gd_csecret']
)
gd_service = gd.create_service(creds)

# Initial display and calculations
st.markdown(
    '''
    <h3>
    Paso 2: Procesa el audio para su transcripción
    </h3>
    <p class='jtext'>
    El segundo paso es procesar losa audios recibidos. No obstante, antes de proceder, <b>asegurate
    de que el log ha sido actualizado en el paso 1</b>. Comienza por seleccionar el log que acabas 
    de actualizar del listado a continuación:
    </p>
    ''',
    unsafe_allow_html = True
)

available_logs = gd.get_available_logs(gd_service)
selected_log = st.selectbox(
    'Hemos detectado los siguientes logs en el sistema.',
    available_logs
)

log_data_raw = gd.download_log(
    gd_service, 
    available_logs[selected_log], 
    reduce = False
)
log_data = log_data_raw.loc[(log_data_raw['missing_record']) & (log_data_raw['idioma'] == 'español')]
st.write(log_data)

st.markdown(
    '''
    <p class='jtext'>
    Una vez hayas confirmado que todo está correcto, puedes proceder a escuchar un audio de prueba o 
    a procesar las grabaciones.
    </p>
    <p class='jtext'>
    El procesamiento de las grabaciones consta de dos etapas. En la primera, se jala la 
    grabación de SurveyCTO y se sube a Google Drive como un archivo mp3. En la segunda etapa, se manda
    el audio al endpoint de AssemblyAI para obtener una transcripción, la cual se sube a Google Drive
    como un archivo de texto plano txt.
    </p>
    ''',
    unsafe_allow_html = True
)

bt1, bt2, bt3 = st.columns(3)
with bt1:
    play_sample = st.button('Escuchar audio de muestra')
with bt2:
    process = st.button('Procesar grabaciones')
    
if play_sample:
    sample_url = log_data['llamada'].iloc[0]
    sample_audio_bytes = scto.get_audio(
        st.secrets['SCTO_server'],
        st.secrets['SCTO_user'],
        st.secrets['SCTO_password'],
        sample_url
    )
    st.audio(sample_audio_bytes, format='audio/mp3', autoplay=True)

# Processing audios from selected logs
if process: 
    st.markdown(
        '<br><h5>INICIANDO PROCESO... Esto puede tardar unos momentos...</h5>',
        unsafe_allow_html = True
    )
    st.write('----')

    n_rows = len(log_data)
    counter = 1
    for _, row in log_data.iterrows():

        audio_url   = row['llamada']
        audio_date  = datetime.strptime(row['SubmissionDate'], "%b %d, %Y %I:%M:%S %p")
        audio_date  = audio_date.strftime("%Y-%m-%d")
        audio_name  = f'{row['username']}_{row['id_estudiante']}_{audio_date}.mp3'

        st.markdown(f'<h5>Processing recording {n} of {n_rows}: {audio_name}</h5>', unsafe_allow_html = True)

        audio_bytes = scto.get_audio(
            st.secrets['SCTO_server'],
            st.secrets['SCTO_user'],
            st.secrets['SCTO_password'],
            audio_url
        )

        gd.upload_file(
            service    = gd_service, 
            file_name  = audio_name, 
            content    = audio_bytes,
            type       = 'mp3', 
            parent_id  = gd.buckets['recordings'][row['username']]
        )
        st.success(f'Grabación cargada a Google Drive')

        transcript = ai.get_transcript(api_key = st.secrets['aai_key'], audio = audio_bytes)
        transcript_name = f'tr_{row['username']}_{row['id_estudiante']}_{audio_date}.txt'

        x = gd.upload_file(
            service    = gd_service, 
            file_name  = transcript_name, 
            content    = transcript,
            type       = 'txt', 
            parent_id  = gd.buckets['transcripts'][row['username']]
        )
        st.success(f'Transcripción cargada a Google Drive')
        counter += 1

        st.write('----')

    

