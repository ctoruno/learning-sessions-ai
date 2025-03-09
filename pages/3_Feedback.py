import streamlit as st
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
        Paso 3: Procesa las transcripciones para recibir un feedback
    </h3>
    <p class='jtext'>
        El tercer paso es procesar las transcripciones y enviarlas a OpenAI para obtener un set de recomendaciones generado por 
        IA. No obstante, antes de proceder, <b>asegurate de que las transcripciones fueron procesadas correctamente en el paso 2</b>.
    </p>
    <p>
        Las transcripciones se mandan en lotes para ser procesadas por GPT. Por lo tanto, debes establecer una ventana de tiempo
        sobre las transcripciones que quieres mandar a GPT.
    </p>
    ''',
    unsafe_allow_html = True
)

# Input form
tr_dates = st.form('tr-dates')
with tr_dates:
    date1, date2 = st.columns(2)
    with date1:
        start_date = st.date_input(
            'Fecha de inicio de la ventana', 
            value     = date.today() - timedelta(days=5), 
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
    feedback_type = st.selectbox(
        'Selecciona qué tipo de feedback te gustaría procesar',
        ['Feedback general', 'Feedback focalizado']
    )
    submit2gpt = st.toggle(
        'Evaluar y mandar directamente a GPT',
        value = False
    )
    process_tr = st.form_submit_button('Proceder')

# Processing selected transcripts
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

        transcripts2process = [
            {
                'transcript': gd.download_file(gd_service, tr['id']),
                'student_id': tr['student_id']
            } 
            for tr in available_transcripts
            if tr['within_window']
        ]

        formatted_transcripts = ' '.join([
            f'''
            [INICIO DE TRANSCRIPCIÓN - ID ESTUDIANTE: {tr['student_id']}]

            {tr['transcript']}

            [FIN DE TRANSCRIPCIÓN - ID ESTUDIANTE: {tr['student_id']}]
            '''
            for tr in transcripts2process
        ])

        st.markdown(
            f'''
            <b>{len(transcripts2process)} transcripciones encontradas para {tutor} dentro de la ventana de tiempo</b>
            ''', 
            unsafe_allow_html = True
        )
        if len(transcripts2process) == 0 :
            st.warning('No hay transcripciones para evaluar y/o procesar con GPT')
            continue

        n_chars = len(formatted_transcripts.split())
        if n_chars < 100000:
            st.success(f'Número total de tokens es: {n_chars}. Es posible procesar con GPT.')
        else:
            st.warning(f'Número total de tokens es: {n_chars}. No será posible procesar con GPT.', icon='🚨')

        if submit2gpt: 
            if n_chars < 100000:

                st.markdown(
                    '<b>Mandando información a GPT... Esto puede tardar unos momentos...</b>',
                    unsafe_allow_html = True
                )

                if 'general' in feedback_type:
                    feedback = ai.get_feedback(
                        st.secrets['OPENAI_API_KEY'], 
                        formatted_transcripts, 
                        general = True
                    )
                    feed_name  = f'fb_{tutor}_{date.today()}.txt'
                    gd.upload_file(
                        service    = gd_service, 
                        file_name  = feed_name, 
                        content    = feedback,
                        type       = 'txt', 
                        # parent_id  = gd.buckets['feedback'][tutor]
                        parent_id  = gd.buckets['test']       # CHANGE!!!!
                    )

                if 'focalizado' in feedback_type:
                    feedback = ai.get_feedback(
                        st.secrets['OPENAI_API_KEY'], 
                        formatted_transcripts, 
                        general = False
                    )

                    for response in feedback:
                        feed_name  = f'tgfb_{tutor}_{response[0]}_{date.today()}.txt'
                        gd.upload_file(
                            service    = gd_service, 
                            file_name  = feed_name, 
                            content    = response[1].feedback,
                            type       = 'txt', 
                            # parent_id  = gd.buckets['feedback'][tutor]
                            parent_id  = gd.buckets['test']       # CHANGE!!!!
                        )

                st.success(f'Retroalimentación cargada a Google Drive')

            else:
                st.warning(f'Número total de tokens es: {n_chars}. No será posible procesar con GPT.', icon='🚨')

        st.write('----')