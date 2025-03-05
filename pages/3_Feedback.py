import streamlit as st
import pandas as pd
from tools import gd_access as gd
from tools import ai
from datetime import datetime, date, timedelta

if "time_window" not in st.session_state:
    st.session_state.time_window = False

def update_tracking(button_name):
    st.session_state[button_name] = True

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
        El tercer paso es procesar las transcripciones y enviarlas a OpenAI para obtener un set de recomendaciones basado
        generrdo por IA. No obstante, antes de proceder, <b>asegurate de que las transcripciones fueron procesadas correctamente 
        en el paso 2</b>.
    </p>
    <p>
        Las transcripciones se mandan en lotes para ser procesadas por GPT. Por lo tanto, debes establecer una ventana de tiempo
        sobre las transcripciones que quieres mandar a gpt.
    </p>
    ''',
    unsafe_allow_html = True
)

tr_dates = st.form('tr-dates')
with tr_dates:
    date1, date2 = st.columns(2)
    with date1:
        start_date = st.date_input(
            'Fecha de inicio de la ventana', 
            value     = date.today()- timedelta(days=3), 
            min_value = datetime.strptime('2025/02/14', '%Y/%m/%d'), 
            max_value = 'today',
            format    = "YYYY/MM/DD"
        )
    with date2:
        end_date = st.date_input(
            'Fecha final de la ventana', 
            value     = "today", 
            min_value = datetime.strptime('2025/02/14', '%Y/%m/%d'), 
            max_value = 'today',
            format    = "YYYY/MM/DD"
        )
    gpt_submit = st.toggle(
        'Solo evaluar, sin procesar por GPT',
        value = True
    )
    process_tr = st.form_submit_button('Proceder')

if process_tr:
    update_tracking("time_window")

if st.session_state["time_window"]: 

    tutors = [
        tutor_name for tutor_name,_ in gd.buckets['transcripts'].items() 
        if tutor_name not in ['root']
    ]

    for tutor in tutors:

        st.markdown(f'<h5>Evaluando data de {tutor}</h5>', unsafe_allow_html = True)

        available_transcripts = gd.get_available_transcripts(gd_service, gd.buckets['transcripts'][tutor])
        for file in available_transcripts:
            file["within_window"] = start_date <= file["date"] <= end_date

        transcripts2process_ids = [
            tr['id'] for tr in available_transcripts
            if tr['within_window']
        ]

        transcripts2process = [
            gd.download_file(gd_service, id) for id in transcripts2process_ids
        ]
        formatted_transcripts = ' '.join([
            f'''
            [INICIO DE TRANSCRIPCIÓN {i+1}]

            {content}

            [FIN DE TRANSCRIPCIÓN {i+1}]
            '''
            for i,content in enumerate(transcripts2process)
        ])

        st.markdown(
            f'''
            <b>{len(transcripts2process)} transcripciones encontradas para {tutor} dentro de la ventana de tiempo</b>
            ''', 
            unsafe_allow_html = True
        )

        if not gpt_submit: 
            st.markdown(
                '<b>Mandando información a GPT... Esto puede tardar unos momentos...</b>',
                unsafe_allow_html = True
            )

            feedback = ai.get_feedback(st.secrets['OPENAI_API_KEY'], formatted_transcripts)
            feed_name  = f'fb_{tutor}_{end_date}.txt'

            gd.upload_file(
                service    = gd_service, 
                file_name  = feed_name, 
                content    = feedback,
                type       = 'txt', 
                # parent_id  = gd.buckets['feedback'][tutor]
                parent_id  = gd.buckets['test']       # CHANGE!!!!
            )
            st.write(f'Retroalimentación cargada a Google Drive')

        st.write('----')