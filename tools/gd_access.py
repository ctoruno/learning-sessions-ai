import io
import os
import re
import json
import tempfile
import pandas as pd
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

buckets = {
    'recordings'   : {
        'root'     : '1z2nxlaCc6QPY9yIwUMIz_58-2DagVSJc',
        'abareiro' : '1eksBTjJjgrJNU2Idokh6aGFoBuKa6G1y',
        'cobregon' : '13hVca4d_0-5FwgvI5sQuRlOb02TIpH3q',
        'lariel'   : '1NXR1YTABhoxwpjplks6WP0c1MNcfNwuc',
        'lmayans'  : '1XYgQPq3ILY3-D-2MrwFQzjuBosqZtSkm'
    },
    'transcripts'  : {
        'root'     : '14c_oSCVHEkSBb59-68qJlJmSu9-WYqfO',
        'abareiro' : '1ydTDALaXrq1BnqWZ7dLYGVO29FUrQg9Q',
        'cobregon' : '1bK9z7e_BNkVh8ltvHesS1q1S5UqL2QHi',
        'lariel'   : '10DGiC6MCOCtTmWep_2eQr6MhTmFc91qR',
        'lmayans'  : '1FdY4Y2RjHYJSSjOaOxMg_Mt-49-7YItv'
    },
    'feedback'     : {
        'root'     : '1FKJ5dez8TJAoSIiCtVR6P1rYTrwSE0TT',
        'abareiro' : '1fPGe9O5A8tlO-6FlIwrUEFjlpugjkAGI',
        'cobregon' : '1n4816o7cqQBoR0GcGXVP6R1KxtabORtj',
        'lariel'   : '1Dg-WQq4ak4pxWqcsM052nPdpvM8t7RgB',
        'lmayans'  : '1_6mg0LuzomvFpBAEoqtzYCR3RO0MypV3'
    },
    'tutors' : {
        'abareiro' : {
            'name' : 'Ana Bareiro',
            'phone': ['595983172719', '595981003427']
        },
        'cobregon' : {
            'name' : 'Christian Obregón',
            'phone': ['595984947525', '595984831886']
        },
        'lariel'   : {
            'name' : 'Lucas Morel',
            'phone': ['595994253166', '595981724678']
        },
        'lmayans'  : {
            'name' : 'Larissa Mayans',
            'phone': ['595972611548']
        }
    },
    'logs' : '1OGbV6ub6r-G8z7IwBpV9ucPbyOerGYM_',
    'test' : '1gx-_FV5onGEYmT7WDZW0l3Vlmp2nNQeW'
}


def get_gd_info(token, rtoken, cid, csec):
    """
    Generates a JSON string with the credentials information.
    Args:
        token (str): Access token.
        rtoken (str): Refresh token.
        cid (str): Client ID.
        csec (str): Client secret.
    Returns:
        str: JSON string with the credentials information.
    """

    info = {
        "token": token, 
        "refresh_token": rtoken, 
        "token_uri": "https://oauth2.googleapis.com/token", 
        "client_id": cid, 
        "client_secret": csec, 
        "scopes": ["https://www.googleapis.com/auth/drive"], 
        "universe_domain": "googleapis.com", 
        "account": "", 
        "expiry": "2025-02-24T18:52:51.516199Z"
    }
    return json.dumps(info)


def create_service(creds):
    """
    Creates a Google Drive service instance using the provided credentials.
    Args:
        creds (str): JSON string with the credentials information.
    Returns:
        service: Google Drive service instance.
    """

    scopes = ['https://www.googleapis.com/auth/drive']
    api_service_name = 'drive', 
    api_version      = 'v3',

    creds_json = json.loads(creds)
    credentials = Credentials.from_authorized_user_info(creds_json, scopes=scopes)
    
    try:
        service = build(
            api_service_name, 
            api_version, 
            credentials = credentials, 
            static_discovery = False
        )
        print(api_service_name, api_version, 'service created successfully')
        return service

    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {api_service_name}')
        # os.remove(os.path.join(working_dir, token_dir, token_file_name))
        return None


def get_available_logs(service, logs_id = buckets['logs']):
    """
    Retrieves a list of available logs from a specified Google Drive folder.
    Args:
        service: Google Drive service instance.
        logs_id (str): ID of the Google Drive folder containing the logs.
    Returns:
        dict: Dictionary containing the names and IDs of the available logs.
    """

    query= f"parents = '{logs_id}'"
    folder_elements = (
            service
            .files()
            .list(supportsAllDrives=True, includeItemsFromAllDrives=True, q=query)
            .execute()
        )
    
    file_names = [
        item['name'] for item in folder_elements['files']
    ]
    file_ids = [
        item['id'] for item in folder_elements['files']
    ]

    return dict(zip(file_names, file_ids))


def download_log(service, file_id, reduce=True):
    """
    Downloads a log file from Google Drive and returns it as a pandas DataFrame.
    Args:
        service: Google Drive service instance.
        file_id (str): ID of the log file to download.
        reduce (bool): Whether to reduce the DataFrame to specific columns.
    Returns:
        pd.DataFrame: DataFrame containing the log data.
    """

    try:
        request = (
            service
            .files()
            .get_media(fileId = file_id, supportsAllDrives=True)
        )

        f = io.BytesIO()
        downloader = MediaIoBaseDownload(fd = f, request = request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

        df = pd.read_csv(io.StringIO(f.getvalue().decode('utf-8')))
        if reduce:
            df = df.loc[:,['username', 'SubmissionDate', 'id_estudiante', 'nombre', 'idioma', 'KEY']]

    except HttpError as error:
        print(f"An error occurred: {error}")
        df = None

    return df


def download_file(service, file_id):
    """
    Downloads a file from Google Drive and returns its content as a string.
    Args:
        service: Google Drive service instance.
        file_id (str): ID of the file to download.
    Returns:
        str: Content of the downloaded file.
    """

    try:
        request = (
            service
            .files()
            .get_media(fileId = file_id, supportsAllDrives=True)
        )

        f = io.BytesIO()
        downloader = MediaIoBaseDownload(fd = f, request = request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

        content = f.getvalue().decode('utf-8')

    except HttpError as error:
        print(f"An error occurred: {error}")
        content = None

    return content


def upload_file(service, file_name, content, type, parent_id, retid = False):
    """
    Uploads a file to Google Drive.
    Args:
        service: Google Drive service instance.
        file_name (str): Name of the file to upload.
        content (str): Content of the file to upload.
        type (str): Type of the file (e.g., 'csv', 'txt', 'mp3').
        parent_id (str): ID of the parent folder in Google Drive.
        retid (bool): Whether to return the file ID after upload.
    Returns:
        str: ID of the uploaded file if retid is True, otherwise None."""

    if type == 'csv':
        mtype = 'text/csv'
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmpfile:
            content.to_csv(tmpfile.name, index=False)
            tmpfile_path = tmpfile.name

    if type == 'txt':
        mtype = 'text/plain'
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmpfile:
            tmpfile.write(content.encode('utf-8'))
            tmpfile_path = tmpfile.name
            tmpfile.flush()
    
    if type == 'mp3':
        mtype = 'audio/mpeg'
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tmpfile.write(content)
            tmpfile_path = tmpfile.name

    metadata = {
        'name'     : file_name,
        'parents'  : [f'{parent_id}']
    }
    tfile = MediaFileUpload(tmpfile_path, mimetype=mtype)

    f = service.files().create(
        body       = metadata, 
        media_body = tfile, 
        fields     = 'id', 
        supportsAllDrives=True
    ).execute()
    os.remove(tmpfile_path)

    return f.get('id')


def get_available_transcripts(service, parent_id):
    """
    Retrieves a list of available transcripts from a specified Google Drive folder.
    Args:
        service: Google Drive service instance.
        parent_id (str): ID of the Google Drive folder containing the transcripts.
    Returns:
        list: List of dictionaries containing the names, IDs, dates, and student IDs of the available transcripts.
    """

    query= f"parents = '{parent_id}'"
    folder_elements = (
            service
            .files()
            .list(supportsAllDrives=True, includeItemsFromAllDrives=True, q=query)
            .execute()
        )
    
    file_names = [
        item['name'] for item in folder_elements['files']
    ]
    file_ids = [
        item['id'] for item in folder_elements['files']
    ]
    file_dates = [
        datetime.strptime(
            re.search(r"(\d{4}-\d{2}-\d{2})", file_name).group(1), 
            "%Y-%m-%d"
        ).date()
        for file_name in file_names
    ]
    student_ids = [
        re.search(r"PY\d+", item).group(0) for item in file_names
    ]

    result = [
        {"id": file_ids[i], "name": file_names[i], "date": file_dates[i], "student_id": student_ids[i]}
        for i in range(len(file_names))
    ]

    return result


def get_available_feedbacks(service, parent_id):
    """
    Retrieves a list of available feedback files from a specified Google Drive folder.
    Args:
        service: Google Drive service instance.
        parent_id (str): ID of the Google Drive folder containing the feedback files.
    Returns:
        list: List of dictionaries containing the names, IDs, and dates of the available feedback files.
    """

    query= f"parents = '{parent_id}'"
    folder_elements = (
            service
            .files()
            .list(supportsAllDrives=True, includeItemsFromAllDrives=True, q=query)
            .execute()
        )
    
    file_names = [
        item['name'] for item in folder_elements['files']
    ]
    file_ids = [
        item['id'] for item in folder_elements['files']
    ]
    file_dates = [
        datetime.strptime(
            re.search(r"(\d{4}-\d{2}-\d{2})", file_name).group(1), 
            "%Y-%m-%d"
        ).date()
        for file_name in file_names
    ]

    result = [
        {"id": file_ids[i], "name": file_names[i], "date": file_dates[i]}
        for i in range(len(file_names))
    ]

    return result