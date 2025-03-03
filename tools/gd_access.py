import io
import os
import json
import tempfile
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

buckets = {
    'recordings'   : {
        'root'     : '1z2nxlaCc6QPY9yIwUMIz_58-2DagVSJc',
        'abareiro' : '',
        'cobregon' : '',
        'lariel'   : '',
        'lmayans'  : ''
    },
    'transcripts'  : {
        'root'     : '14c_oSCVHEkSBb59-68qJlJmSu9-WYqfO',
        'abareiro' : '',
        'cobregon' : '',
        'lariel'   : '',
        'lmayans'  : ''
    },
    'feedback'     : {
        'root'     : '1FKJ5dez8TJAoSIiCtVR6P1rYTrwSE0TT',
        'abareiro' : '',
        'cobregon' : '',
        'lariel'   : '',
        'lmayans'  : ''
    },
    'logs' : '1OGbV6ub6r-G8z7IwBpV9ucPbyOerGYM_',
    'test' : '1gx-_FV5onGEYmT7WDZW0l3Vlmp2nNQeW'
}


def get_gd_info(token, rtoken, cid, csec):

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
        os.remove(os.path.join(working_dir, token_dir, token_file_name))
        return None


def get_available_logs(service, logs_id = buckets['logs']):

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

