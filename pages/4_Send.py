import streamlit as st
from tools import gd_access as gd
from tools import whatsapp as wa

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
        Paso 4: Revisa, edita, y manda el feedback por WhatsApp
    </h3>
    <p class='jtext'>
        El cuarto paso consiste en revisar, editar, y mandar las recomendaciones producidas por GPT a través de WhatsApp.
        No obstante, antes de proceder, <b>asegurate de que las recomendaciones fueron enviadas y procesadas correctamente 
        en el paso 3</b>.
    </p>
    <p>
        El programa deja un margen de personalización para las recomendaciones. Por lo tanto, selecciona un tutor, un tipo
        de recomendación, y un listado de recomendaciones a enviar.
    </p>
    ''',
    unsafe_allow_html = True
)

# Input form
tutors = [
    tutor_name for tutor_name,_ in gd.buckets['transcripts'].items() 
    if tutor_name not in ['root']
]
tutor = st.selectbox(
    'Selecciona un tutor',
    tutors
)
feedback_type = st.selectbox(
    'Selecciona qué tipo de feedback te gustaría revisar',
    ['Feedback general', 'Feedback focalizado']
)

available_feedbacks = gd.get_available_feedbacks(
    gd_service,
    gd.buckets['feedback'][tutor]    
    # gd.buckets['test']    # !! CHANGE !!
)

if 'general' in feedback_type:
    selected_feedback_name = st.selectbox(
        'Selecciona un transcript a revisar',
        [
            f['name'] 
            for f in available_feedbacks
            if f['name'].startswith('fb_')
        ]
    )
if 'focalizado' in feedback_type:
    selected_feedback_name = st.selectbox(
        'Selecciona un transcript a revisar',
        [
            f['name'] 
            for f in available_feedbacks
            if f['name'].startswith('tgfb_')
        ]
    )

selected_feedback = [
    fb for fb in available_feedbacks
    if fb['name'] == selected_feedback_name
][0]

feedback = gd.download_file(
    gd_service,
    selected_feedback['id']
)

edited_feedback = st.text_area(
    'Sugerencias recomendadas',
    feedback,
    height = 350,
    max_chars = 800
)
st.markdown(
    '''
    <p class='jtext'>
        Si el set de recomendaciones sugeridas por GPT supera los 800 caracteres, <b>es muy importante que
        se editen para que no superen el límite establecido</b>.
    </p>
    <p class='jtext'>
        El mensaje será procesado en WhatsApp y no contendrá saltos de línea. Revisa la previsualización abajo.
        Es recomendable sustituir las viñetas por bullets enumerados de la siguiente forma: *(1)*, *(2)*, etc
    </p>
    ''',
    unsafe_allow_html = True
)
preview_message = st.expander('Haz click aquí para ver una previsualización del mensaje en Whatsapp:')
with preview_message:
    st.text(
        f'''
        Buenos días estimado(a) {gd.buckets['tutors'][tutor]['name']}. Le escribo para informarle que nuestro sistema ha 
        generado las siguientes recomendaciones automáticas para sus próximas sesiones:

        {wa.process_text(edited_feedback)}

        Le deseamos un excelente día.
        '''
    )

send_fb = st.button('Enviar recomendaciones')

testing = st.toggle('Enviar mensaje de prueba')

if send_fb:
    if testing:
        phones = ['17869289137', '573192499151']        # CHANGE!!!!
    else:
        phones = gd.buckets['tutors'][tutor]['phone']     
    
    for phone in phones:
        st.markdown(f'<h5>Enviando recomendaciones a {tutor} - Tel: {phone}</h5>', unsafe_allow_html = True)
        wa.send_feedback(
            phone_id  = st.secrets['wa_phone'], 
            token     = st.secrets['wa_token'], 
            recipient = phone, 
            name      = gd.buckets['tutors'][tutor]['name'], 
            feedback  = wa.process_text(edited_feedback)
        )