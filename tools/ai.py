import tempfile
import assemblyai as aai
from openai import OpenAI

def get_transcript(api_key, audio):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(audio)
        temp_audio_path = temp_audio.name

    aai.settings.api_key = api_key
    aai_config = aai.TranscriptionConfig(
        speech_model      = aai.SpeechModel.best,
        speaker_labels    = True,
        language_code     = "es"
    )

    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe(
        temp_audio_path,
        config = aai_config
    )

    transcript_uts  = [f"Speaker {utterance.speaker}: {utterance.text}" for utterance in transcript.utterances]
    full_transcript = "\n".join(transcript_uts)

    return full_transcript


def gen_system_prompt():
    prompt = '''
    Eres un experto consultor en educación especializado en tutoría y métodos de enseñanza efectivos. Recibirás transcripciones de sesiones 
    de tutoría en matemáticas entre un tutor y un estudiante de primaria (cuarto a sexto grado). Tu tarea es analizar la metodología de 
    enseñanza del tutor y proporcionar recomendaciones prácticas para mejorar su desempeño.

    Tu análisis debe incluir:

    1. Evaluación de técnicas de explicación
        
        - Analiza la claridad, estructura y precisión de las explicaciones.
        - Evalúa el uso de ejemplos, analogías y estrategias didácticas.
        - Determina si las explicaciones están adaptadas al nivel de comprensión del estudiante.
    
    2. Evaluación del compromiso y la eficacia pedagógica

        - Observa cómo el tutor involucra al estudiante y verifica su comprensión.
        - Identifica si usa métodos interactivos o reflexivos para reforzar el aprendizaje.
    
    3. Retroalimentación constructiva

        - Proporciona sugerencias específicas y accionables para mejorar su enseñanza.
        - Considera prácticas como simplificar conceptos, usar ejemplos relevantes, resumir puntos clave y fomentar la participación.
        - Asegúrate de que la retroalimentación sea objetiva, alentadora y orientada al crecimiento profesional del tutor.
    
    4. Consideraciones y contexto

        - Basa tu evaluación en la transcripción proporcionada y en buenas prácticas pedagógicas.
        - Mantén un tono claro, breve y amable, ya que el tutor leerá directamente las recomendaciones.
    
    Tu respuesta debe consistir exclusivamente en un conjunto de recomendaciones derivadas de tu evaluación.
    '''

    return prompt

def gen_context_prompt(transcript):
    prompt = f'''
    La siguiente es una transcripción de una sesión de tutoría de matemáticas entre un tutor y un estudiante de cuarto a sexto grado de 
    primaria:

    [INICIO DE LA TRANSCRIPCIÓN]

    {transcript}

    [FIN DE LA TRANSCRIPCIÓN]

    La transcripción puede contener errores y omisiones, especialmente en intervenciones cortas. No te enfoques en errores gramaticales o 
    tipográficos. Además, la transcripción separa las intervenciones por interlocutor, pero no especifica quién es el tutor y quién es el 
    estudiante. Deberás inferirlo según el contenido.

    INSTRUCCIONES:

    Con base en la transcripción, evalúa las técnicas de explicación, el compromiso y la eficacia pedagógica del tutor. Luego, elabora un 
    conjunto estructurado de recomendaciones breves y específicas para mejorar su enseñanza.

    Asegúrate de que tu retroalimentación sea:

    - Objetiva, alentadora y enfocada en el crecimiento profesional del tutor.
    - Limitada a 1000 caracteres.
    - Escrita en formato de lista con viñetas, sin títulos ni encabezados.
    - Directa, clara y utilizando un tono amable, ya que será leída directamente por el tutor.
    - Contextualizada, es decir, procura añadir 1 o 2 ejemplos de cómo el tutor podría haber implementado tus recomendaciones en la sesión previa

    ASPECTOS A EVALUAR:

    - Estructura de la tutoría: ¿Hay una introducción clara y un cierre efectivo?
    - Interacción: ¿El estudiante participa activamente? ¿El tutor verifica su comprensión? ¿Cómo responde el tutor a las preguntas y dudas?
    - Técnicas pedagógicas: ¿Se usan ejemplos relevantes y estrategias efectivas?
    - Manejo del tiempo: ¿El tutor ajusta el ritmo y aprovecha los 30 minutos disponibles?
    - Aspectos específicos: Claridad de explicaciones, detección de confusiones, motivación del estudiante, uso de preguntas guía.

    CONSIDERACIONES ADICIONALES:

    - Concéntrate en la forma en que el tutor enseña, no en modificar el contenido de la guía de ejercicios.
    - Evita resaltar aspectos positivos, salvo para contrastarlos con áreas de mejora.
    - Recuerda que el estudiante tiene entre 8 y 10 años, por lo que las explicaciones deben ser adecuadas a su nivel.
    - Las sesiones de tutoría se realizan vía telefónica, por lo que el tutor no puede hacer uso de medios visuales, solo auditivos.
    - Enfoca tu set de recomendaciones EXCLUSIVAMENTE en los aspectos a mejorar y en las acciones específicas para lograrlo.

    Gracias por tu valiosa contribución a la mejora de la calidad educativa.
    '''

    return prompt
    
def get_feedback(api_key, transcript):

    client = OpenAI(
        api_key = api_key
    )

    history = [
        {"role": "system", "content": gen_system_prompt()},
        {"role": "user",   "content": gen_context_prompt(transcript)}
    ]

    chat_completion = client.chat.completions.create(
        messages = history,
        model    = "gpt-4o-2024-08-06"
        # model    = "gpt-4.5-preview-2025-02-27"
    )

    feedback = chat_completion.choices[0].message.content

    return feedback
