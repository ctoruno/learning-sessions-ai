import pandas as pd
from io import StringIO
from pysurveycto import SurveyCTOObject

def get_latest_data(server, user, key):
    """
    Get the latest data from SurveyCTO.
    Args:
        server (str): The server name.
        user (str): The username.
        key (str): The password.
    Returns:
        pd.DataFrame: The latest data from SurveyCTO.
    """

    scto = SurveyCTOObject(
        server_name = server, 
        username    = user, 
        password    = key
    )
    form_data = scto.get_form_data(
        form_id     = 'llamadas', 
        format      = 'csv'
    )
    SCTO_data = pd.read_csv(StringIO(form_data))
    SCTO_data = SCTO_data.loc[SCTO_data['username'].isin(['abareiro', 'cobregon', 'lmayans', 'lariel'])]

    return SCTO_data


def get_audio(server, user, key, url):
    """
    Get the audio file from SurveyCTO.
    Args:
        server (str): The server name.
        user (str): The username.
        key (str): The password.
        url (str): The URL of the audio file.
    Returns:
        bytes: The audio file.
    """

    s = SurveyCTOObject(
        server_name = server, 
        username    = user, 
        password    = key
    )
    audio = s.get_attachment(url)

    return audio