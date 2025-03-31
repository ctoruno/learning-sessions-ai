Learning Sessions AI is an app with the objective of extracting and processing audio recording from math tutoring sessions and providing (and delivering) tailored suggestions for tutors to improve their future tutoring sessions. The app makes use of AI tools for processing large volumes of information and quickly prepare personalized feedback for each tutor.

The source code of the app is publicly available on the following GitHub repository: [ctoruno/learning-sessions-ai](https://github.com/ctoruno/learning-sessions-ai).

![image](https://github.com/user-attachments/assets/20dd08a3-b0f1-4f16-8955-a2ac6a8cf406)

## App Design

The app was programmed using the [Streamlit web framework](https://streamlit.io/). Streamlit is an open-source Python framework that allows you to program and deliver dynamic data apps with few lines of code. It is a lightweight framework that allows the user to quickly set up data web apps without having knowledge of web development. For more information, please read [the official documentation in their website](https://docs.streamlit.io/).

So far, the app is not containerized and it is currently designed to be run locally. However, Streamlit provides detailed instructions on how to containerize an app using [Docker](https://docs.streamlit.io/deploy/tutorials/docker) and [Kubernetes](https://docs.streamlit.io/deploy/tutorials/kubernetes). For deploying this app online, it is highly suggested to follow these guides.

The app is designed to process the information in stages. Currently, the process is divided in four stages:

1. Log Update
2. Audio-to-Text Transcription
3. Feedback Processing
4. Feedback Delivery

###  Log Update

To keep track of the audio recordings that has been processed by the program and those who hasn't, the program is designed to follow a log file logic. A log file is a CSV file that contains the information of all the audio recordings already proccesed by the program in the past. These log files are stored [in a designated Google Drive folder](https://drive.google.com/drive/folders/1OGbV6ub6r-G8z7IwBpV9ucPbyOerGYM) and they are saved according to the date in which they were created.

As a first step, the program will display the latest log file detected in the system. The user is able to select a different log file from a dropdown menu for exploration and testing purposes. However, in order to avoid doble processing and system failures, **IT IS HIGHLY IMPORTANT TO SELECT AND PROCESS THE LATEST LOG FILE** during this stage.

![image](https://github.com/user-attachments/assets/b2392836-7917-4c58-b375-b0a95c188424)

Once a log file is selected, the system will display a table containing the information of all the recordings that has been already processed by the system and it will compare it with the current data in SurveyCTO. Depending on the result, two different actions can happen. If the program detects that the latest log file matches the current database in SurveyCTO, no further action is required and the program will display the following message:

> According to the selected log, the system is updated.

If the system detects that the current database in SurveyCTO contains records that have not yet being proccessed by the program, it will display a table with the information of those recordings that has not been processed by the system. At this point, the user should carefully review the records displayed in this second table to assess the following: (i) Does the new records match what it is expected according to the scheduled tutoring sessions? (ii) Are the *Submission Dates* happening AFTER the date of the selected log file? Once the user has assessed the new recordings, proceed and click on the **UPDATE** button. This will create a new log file in the system with a column of booleans (TRUE/FALSE) marking the missing recordings.

![image](https://github.com/user-attachments/assets/8a5f205c-5a4c-4570-a1f2-dfa647857889)

For the execution of this stage, two external libraries are used:

- `pysurveycto`: A Python SDK that is used to download data collected on SurveyCTO using the SurveyCTO REST API. This library allows the program to access the data in SurveyCTO. Three secrets are required: `server_name`, `username`, and `password`. These information is highly sensitive and it is not available in the GitHub repository online. Therefore, for the app to be able to run locally, you need to create a `secrets.toml` file within the `.streamlit/` directory with this information. When deploying the app onlin, please consult the official documentation of your hosting provider regarding how to manage secrets in their platform. The code that handles the server connection can be found in the [`tools/gd_access.py` file](https://github.com/ctoruno/learning-sessions-ai/blob/main/tools/gd_access.py). Please read the [library documentation](https://github.com/IDinsight/surveycto-python) on how to use the Python SDK.

-  `googleapiclient` and the `google.oauth2`: These libraries are used to provide the system with access to the Google Drive where the information is being stored. A JSON token file from Google is needed for the app to be able to interact with Google Drive. Please refer to the [`notebooks/create_token_files.ipynb` file](https://github.com/ctoruno/learning-sessions-ai/blob/main/notebooks/create_token_files.ipynb) for detailed instriuctions on how to create this file. The code that handles the connection to Google services can be found in the [`tools/gd_access.py` file](https://github.com/ctoruno/learning-sessions-ai/blob/main/tools/gd_access.py).

### Audio-to-Text Transcription

Updating the log file takes a few seconds. As soon as the log file is processed, it is HIGHLY suggested to run the transcription stage. Make sure that the recently updated log file is selected in the dropdown menu, which should be the case given that the program is supposed to do it by default. Then, the user can proceed with two different actions: listening to a sample audio recording, or process the recordings displayed in the table presented. 

As mentioned above, the log files have a column that marks which audio recordings have not yet been processed by the system, in this stage, the program will filter the SurveyCTO data using this column and only proceed with the ones marked as missing. Additionally, the program will filter out those recordings where the language is set as "Guaraní". Currently, this program offers no support for recordings in Guaraní.

Once the user clicks on the "**PROCESS RECORDINGS**" button, the system will triggerthe following actions sequentially for each recording:

1. The system will use the media URL (column "llamada" in the log file) to access and download the audio recording using the `pysurveycto` library.
2. The system will save the recording in a [designated Google Drive folder](https://drive.google.com/drive/folders/1z2nxlaCc6QPY9yIwUMIz_58-2DagVSJc) as a mp3 file. Audio recordings are organized in buckets per tutor.
3. The system leverages the power of the Automatic Speech Recognition models provided by [AssemblyAI](https://www.assemblyai.com/) to perform an audio transcription with speaker diarization (ability to assign interventions to different interlocutors).
4. The system will save the transcription in a [designated Google Drive folder](https://drive.google.com/drive/folders/14c_oSCVHEkSBb59-68qJlJmSu9-WYqfO) as a plain txt file.

Besides the external libraries mentioned above, the execution of this stage also requires the use of the [`assemblyai` Python SDK](https://github.com/AssemblyAI/assemblyai-python-sdk). An AssemblyAI key is required to be able to use their API service. This key is saved in the `secrets.toml` file along with all other secrets. The code that handles the AssemblyAI API can be found in the [`tools/ai.py` file](https://github.com/ctoruno/learning-sessions-ai/blob/main/tools/ai.py).

### Feedback Processing

Once the system has retrieved audio transcriptions with interlocutor labels, the next stage is to send this information to be processed by a Large Language Model. There are two types of feedbacks generated by the system: general and targeted.

The general feedback has the objective of analyzing ALL the tutoring transcriptions submitted within a time window and provide a feedback with the purpose of providing guidance and suggestion for tutors to improve their future sessions. On the other hand, the targeted feedback has the objective of analyzing ALL the tutoring transcriptions submitted within a time window and then identify the two students that showed the most confusion or issues during their session and then provide two different sets of suggestions focused to better handle or guide those students according to their identified issues.

To generate these feedbacks, the user needs to define a time window (starting and ending date) and a type of feedback in the app. There is a toggle button that is turned off by default ("**EVALUATE AND SEND TO GPT**). While turned off, the app will only evaluate how many transcriptions within the time window there is per tutor, and also the total amount of tokens that these transcriptions represent. The total amount of tokens should be lower than 100,000 due to the context window of the Large Language Model used by the program. It is highly suggested to first run this stage with this button toggle off to evaluate the information that is about to be send to be processed by the AI models. If everything looks ok, the user should turn on this toggle button which will proceed to evaluate and send the information to a AI provider.

![image](https://github.com/user-attachments/assets/b7c81b9b-7527-4d5a-92aa-e209c3a4d72c)

The program is designed to process the text transcriptions using [OpenAI's GPT-4o model](https://platform.openai.com/docs/models/gpt-4o). For this, the text transcriptions from the audio recordings are sent for inference using OpenAI's API service along with a specific set of instructions (prompts). The instructions differ depending if the user wants to retrieve a general or a targeted feedback. Additionally two different sets of prompts are defined: one for the developer role and one for the user role. Developer messages are instructions provided by the application developer, weighted ahead of user messages. User messages are instructions provided by an end user, weighted behind developer messages. Therefore, developer messages are going to set the general behavior of the AI assistant that will process the information and generate the feedback for us.

- The prompts used to generate a general feedback can be found in the [`notebooks/General_Feedback_Prompts.md` file](https://github.com/ctoruno/learning-sessions-ai/blob/main/notebooks/General_Feedback_Prompts.md)
- The prompts used to generate a targeted feedback can be found in the [`notebooks/Targeted_Feedback_Prompts.md` file](https://github.com/ctoruno/learning-sessions-ai/blob/main/notebooks/Targeted_Feedback_Prompts.md)

Besides the external libraries mentioned above, the execution of this stage also requires the use of the [`openai` Python SDK]([https://github.com/AssemblyAI/assemblyai-python-sdk](https://platform.openai.com/docs/libraries?language=python)). An OpenAI key is required to be able to use their API service. This key is saved in the `secrets.toml` file along with all other secrets. The code that handles the OpenAI API can be found in the [`tools/ai.py` file](https://github.com/ctoruno/learning-sessions-ai/blob/main/tools/ai.py).

Feedbacks generated by the system are then saved in [a designated Google Drive folder](https://drive.google.com/drive/folders/1FKJ5dez8TJAoSIiCtVR6P1rYTrwSE0TT).

### Feedback Delivery

Feedbacks are tailored to be brief (Around 800 characters) with the purpose of sending them as WhatsApp messages. In the last stage of the process, the will have to select a tutor, a type of feedback and the specific set of suggestions generated by AI. The app will display the set of suggestions. It is higly suggested for a human to quickly review and (if needed) edit these suggestions before sending them to the tutors' phone numbers directly.

![image](https://github.com/user-attachments/assets/cc71722f-0ca4-43d4-a9fb-9d2a571958e0)

To send these messages through WhatsApp without the messaging platform to flag them as spam, the program leverages the [Meta Developers Platform](https://developers.facebook.com/). For this, the following is required:

- A Meta Developers account
- A (verified) Meta Business portfolio
- A phone number not associated or linked to any existing WhatsApp personal or business apps
- Permissions have to be set up for corresponding developers from the administrators of these accounts to the app developers

Once the previous three items are associated and linked together as a Meta App. For more information you can read [the official documentation](https://developers.facebook.com/docs/whatsapp/cloud-api). Whatsapp regulates the way that business accounts interacts with personal numbers so business accounts can only start conversations using [message templates](https://developers.facebook.com/docs/whatsapp/message-templates/guidelines). It is important to set up a template message. For the purposes of this project, a Utility template has been set up that reads as follows:

![image](https://github.com/user-attachments/assets/baf05601-6f81-4aff-84ba-be179e057ad7)

A "**RECEIPT**" button is also added at the end of the template for tutors to confirm their lecture and avoid the messaging platform to flag outgoing messages as spam. WhatsApp messages are supposed to be short (~100 characters), given that the feedback sent to tutors is usually larger (600-800 characters), the likelihood of these messages to be flag as spam is higher. Therefore, **IT IS VERY IMPORTANT FOR TUTORS TO INTERACT WITH THE RECEIPT BUTTON** to generate interaction statistics that reduce the likelihood of our messages not being delivered.

Finally, the program fills the empty information in the template and asks WhatsApp to send the message using POST HTTP protocols. These protocols are handle through cURL commands that can be found in the [`tools/whatsapp.py` file]([https://github.com/ctoruno/learning-sessions-ai/blob/main/tools/ai.py](https://github.com/ctoruno/learning-sessions-ai/blob/main/tools/whatsapp.py)).


