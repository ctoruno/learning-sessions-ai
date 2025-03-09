import tempfile
import assemblyai as aai
from openai import OpenAI
from pydantic import BaseModel, Field


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


def gen_system_prompt_1():
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


def gen_system_prompt_2():
    prompt = '''
    Eres un consultor educativo experto especializado en pedagogía matemática y métodos de tutoría efectivos para educación primaria. 
    Tu experiencia abarca estrategias de enseñanza diferenciada, identificación de dificultades de aprendizaje y técnicas para 
    desarrollar competencias matemáticas en estudiantes de 9-12 años.

    Recibirás transcripciones de sesiones de tutoría en matemáticas entre un tutor y varios estudiantes de primaria (cuarto a sexto grado). 
    Deberás:

    1. Analizar cuidadosamente las interacciones tutor-estudiante en cada transcripción.
    2. Identificar a los dos estudiantes que muestren mayores dificultades de comprensión matemática.
    3. Basados en los problemas conceptuales específicos que presentan, así como los patrones de error y confusión recurrentes que identifiques, 
    deberás proporcionar recomendaciones prácticas y accionables para el tutor para cada uno de estos dos estudiantes.

    Basa tu evaluación en la transcripción proporcionada y en buenas prácticas pedagógicas. Mantén un tono claro, breve y amable, ya que el 
    tutor leerá directamente las recomendaciones.
    
    Tu respuesta debe consistir exclusivamente en un conjunto de recomendaciones derivadas de tu evaluación.
    '''

    return prompt


def gen_context_prompt_1(full_transcript):
    prompt = f'''
    A continuación, tienes una serie de transcripciones de una o varias sesiones de tutoría de matemáticas 
    entre un tutor y diversos estudiantes de cuarto a sexto grado de primaria:

    {full_transcript}

    Las transcripciones puede contener errores y omisiones, especialmente en intervenciones cortas. No te enfoques en errores gramaticales o 
    tipográficos. Además, la transcripción separa las intervenciones por interlocutor, pero no especifica quién es el tutor y quién es el 
    estudiante. Deberás inferirlo según el contenido.

    INSTRUCCIONES:

    Con base en la transcripciones, evalúa las técnicas de explicación, el compromiso y la eficacia pedagógica del tutor. Luego, elabora un 
    conjunto estructurado de recomendaciones breves y específicas para mejorar su enseñanza.

    Asegúrate de que tu retroalimentación sea:

    - Objetiva, alentadora y enfocada en el crecimiento profesional del tutor.
    - LIMITADA A 800 CARACTERES !!!MUY IMPORTANTE!!!.
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


def gen_context_prompt_2(full_transcript):
    prompt = f'''
    A continuación, tienes una serie de transcripciones de una o varias sesiones de tutoría de matemáticas 
    entre un tutor y diversos estudiantes de cuarto a sexto grado de primaria:

    {full_transcript}

    Las transcripciones puede contener errores y omisiones, especialmente en intervenciones cortas. No te enfoques en errores gramaticales o 
    tipográficos. Además, la transcripción separa las intervenciones por interlocutor, pero no especifica quién es el tutor y quién es el 
    estudiante. Deberás inferirlo según el contenido.

    INSTRUCCIONES:
    Deberás:

    1. Analizar cuidadosamente las interacciones tutor-estudiante en cada transcripción.
    2. Identificar a los dos estudiantes que muestren mayores dificultades de comprensión matemática
    3. Diagnosticar los problemas conceptuales específicos que presentan, así como identificar posibles patrones de error o 
    confusiones recurrentes y determinar sus fortalezas que puedan aprovecharse
    4. Proporcionar recomendaciones prácticas y accionables para el tutor.

    ASPECTOS A TOMAR EN CUENTA:
    A la hora de brindar recomendaciones prácticas, por favor considera los siguientes elementos:

    - Estrategias de andamiaje adaptadas a cada estudiante
    - Actividades concretas para abordar los conceptos problemáticos
    - Sugerencias para modificar el enfoque comunicativo del tutor
    
    Asegúrate de que tu retroalimentación sea:

    - LIMITADA A 800 CARACTERES POR ESTUDIANTE !!!MUY IMPORTANTE!!!.
    - Escrita en formato de lista enumerada, sin títulos ni encabezados.
    - Directa, clara y utilizando un tono amable, ya que será leída directamente por el tutor.
    - Contextualizada, es decir, procura añadir 1 o 2 ejemplos de cómo el tutor podría haber implementado tus recomendaciones en la sesión previa

    CONSIDERACIONES ADICIONALES:

    - Concéntrate en la forma en que el tutor enseña, no en modificar el contenido de la guía de ejercicios.
    - Evita resaltar aspectos positivos, salvo para contrastarlos con áreas de mejora.
    - Recuerda que el estudiante tiene entre 8 y 10 años, por lo que las explicaciones deben ser adecuadas a su nivel.
    - Las sesiones de tutoría se realizan vía telefónica, por lo que el tutor no puede hacer uso de medios visuales, solo auditivos.
    - Enfoca tu set de recomendaciones EXCLUSIVAMENTE en los aspectos a mejorar y en las acciones específicas para lograrlo.
    - Utiliza el identificador del estudiante (ID) para asociar un set de recomendaciones.
    - !!!MUY IMPORTANTE!!! Menciona el nombre del estudiante en tu set de recomendaciones.

    FORMATO DE RESPUESTA:
    Tu análisis debe presentarse en formato JSON con la siguiente estructura:

    {{
        "estudiante_1" :  {{
            "id" : ID del estudiante con mayores dificultades,
            "nombre" : Nombre del estudiante con mayores dificultades,
            "feedback" : "Recomendaciones para el estudiante con mayores dificultades como un listado enumerado"
        }},
        "estudiante_2" :  {{
            "id" : ID del segundo estudiante con mayores dificultades,
            "nombre" : Nombre del segundo estudiante con mayores dificultades,
            "feedback" : "Recomendaciones para el segundo estudiante con mayores dificultades como un listado enumerado"
        }},
    }}

    Donde:
    - Cada recomendación debe ser concreta, accionable y específica para ese estudiante particular.
    - No incluyas explicaciones o análisis adicionales fuera de la estructura JSON.

    Gracias por tu valiosa contribución a la mejora de la calidad educativa.
    '''

    return prompt


class StudentFeedback(BaseModel):
    id: str = Field(description="ID del estudiante con dificultades")
    nombre: str = Field(description="Nombre del estudiante con dificultades")
    feedback: str = Field(description="Recomendaciones como un listado enumerado")

    
class Feedback(BaseModel):
    estudiante_1: StudentFeedback
    estudiante_2: StudentFeedback

    
def get_feedback(api_key, transcript, general=True):

    client = OpenAI(
        api_key = api_key
    )

    if general:
        history = [
            {"role": "system", "content": gen_system_prompt_1()},
            {"role": "user",   "content": gen_context_prompt_1(transcript)}
        ]
        chat_completion = client.chat.completions.create(
            messages = history,
            model    = "gpt-4o-2024-08-06"
        )
        feedback = chat_completion.choices[0].message.content

    else:
        history = [
            {"role": "system", "content": gen_system_prompt_2()},
            {"role": "user",   "content": gen_context_prompt_2(transcript)}
        ]
        chat_completion = client.beta.chat.completions.parse(
            messages = history,
            model    = "gpt-4o-2024-08-06",
            response_format = Feedback
        )
        feedback = chat_completion.choices[0].message.parsed

    return feedback
