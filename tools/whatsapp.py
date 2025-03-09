import os
import re
import requests

def process_text(text):
    text_nospaces = re.sub(
        '\\n|-', '', text
    ).strip()

    return text_nospaces

def send_feedback(phone_id, token, recipient, name, feedback):
    url = f'https://graph.facebook.com/v22.0/{phone_id}/messages'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': f'{recipient}',
        'type': 'template',
        'template': {
            'name': 'feedback_tutorias_2',
            'language': {
                'code': 'es'
            },
            'components': [
                {
                    'type': 'body',
                    'parameters': [
                        {
                            'type': 'text',
                            'parameter_name': "name_tutor",
                            'text': f'{name}'
                        },
                        {
                            'type': 'text',
                            'parameter_name': "feedback",
                            'text': f'{feedback}'
                        },
                    ]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=data)

    return {
        'status'  : response.status_code,
        'content' : response.json()
    }

