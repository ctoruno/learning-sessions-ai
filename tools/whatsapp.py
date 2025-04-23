# import os
import re
import requests

def process_text(text):
    text_nospaces = re.sub(
        '\\n|-', '', text
    ).strip()

    return text_nospaces

def send_feedback(phone_id, token, recipient, name, feedback):
    """
    Send a feedback message to a WhatsApp user using the WhatsApp Business API.
    Args:     
        phone_id (str): The phone ID of the WhatsApp Business account.
        token (str): The access token for the WhatsApp Business API.
        recipient (str): The recipient's phone number in international format.
        name (str): The name of the tutor.
        feedback (str): The feedback message to be sent.
    Returns:
        dict: A dictionary containing the status code and response content.
    """
    
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

