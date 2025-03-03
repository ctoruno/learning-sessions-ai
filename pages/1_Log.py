from datetime import date
from io import StringIO
import streamlit as st
import pandas as pd
from tools import gd_access as gd
from tools import scto_access as scto

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
    Paso 1: Actualiza el log en el sistema
    </h3>
    <p class='jtext'>
    El primer paso es evaluar si el log en el sistema está actualizado con la data más reciente de SurveyCTO. Para ello,
    selecciona el último log disponible en el sistema para evaluarlo contra la data más reciente en SurveyCTO.
    </p>
    ''',
    unsafe_allow_html = True
)

available_logs = gd.get_available_logs(gd_service)
selected_log = st.selectbox(
    'Hemos detectado los siguientes logs en el sistema.',
    available_logs
)

log_data = gd.download_log(gd_service, available_logs[selected_log])
st.write(log_data)

keys_processed = log_data.KEY.to_list()

latest_form = scto.get_latest_data(
    st.secrets['SCTO_server'],
    st.secrets['SCTO_user'],
    st.secrets['SCTO_password']
)
latest_form_keys = latest_form.KEY.to_list()

missing_keys = [key for key in latest_form_keys if key not in keys_processed]
if missing_keys:

    st.markdown(
        f'''
        <p class='jtext'>
        De acuerdo al log seleccionado, parece que hay un total de {len(missing_keys)} tutorias que no se han procesado con el sistema.
        A continuación se muestra un listado de las tutorías no encontradas:
        </p>
        ''',
        unsafe_allow_html = True
    )

    latest_form['missing_record'] = latest_form['KEY'].isin(missing_keys)

    latest_form_reduced = (
        latest_form.copy()
        .loc[latest_form['KEY'].isin(missing_keys),['username', 'SubmissionDate', 'id_estudiante', 'nombre', 'idioma', 'KEY', 'missing_record']]
    )
    st.write(latest_form_reduced)

    st.markdown(
        f'''
        <p class='jtext'>
        Una vez hayas confirmado que los registrados necesitan ser actualizados, procede a actualizar el log del sistema.
        </p>
        ''',
        unsafe_allow_html = True
    )

    update = st.button("Actualizar")

    if update:
        gd.upload_file(
            service    = gd_service, 
            file_name  = f'log_{date.today()}.csv', 
            content    = latest_form,
            type       = 'csv', 
            parent_id  = gd.buckets['logs']
        )
        st.write(f'Data uploaded successfully')

else:
    st.markdown(
        f'''
        <p class='jtext'>
        De acuerdo al log seleccionado, el sistema está actualizado.
        </p>
        ''',
        unsafe_allow_html = True
    )


    

    
    