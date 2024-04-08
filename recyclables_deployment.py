# -*- coding: utf-8 -*-
"""recyclables_deployment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aYBKTRhOD8gxXxqPUC9T1K-lDPaxloEV
"""

## Import
import sys
print(sys.version)
import subprocess
import streamlit as st
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from PIL import Image
import requests
import uuid
from datetime import datetime, timedelta
import pytz
import os
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import streamlit_analytics
from streamlit.runtime import get_instance
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from streamlit_cookies_manager import EncryptedCookieManager
from flask import Flask, request, jsonify
import threading
from flask_cors import CORS
import socket
from deta import Deta
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import tempfile
from google.auth.credentials import Credentials
from google.oauth2 import service_account
import io

## Streamlit Tracker Start
streamlit_analytics.start_tracking()

## Cookies Manager
cookies = EncryptedCookieManager(
    # This prefix will get added to all your cookie names. This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
    prefix="recyclables-class/",
    # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    password=os.environ.get("STREAMLIT_COOKIES_MANAGER_PASSWORD", "My secret password"),
)
if not cookies.ready(): # Wait for the component to load and send us current cookies.
    st.stop()

# Retrieve the user_id from the cookies
cookies_user_id = cookies.get("user_id")
    
# If user_id is None, generate a new one
if cookies_user_id is None:
    cookies_user_id = str(uuid.uuid4())
    cookies["user_id"] = cookies_user_id


## TEST ###############################
# # TEST IPA
# # Create a Flask app
# app = Flask(__name__)
# CORS(app)

# #Initialize session state
# if 'user_ip' not in st.session_state:
#     st.session_state.user_ip = None

# # # Display a text input field for the user's IPA
# user_ip = None
# user_ip = st.text_input("User IPA", "")


# #Get Port Javascript is connected to
# java_port = None

# # Route to receive the port number from JavaScript
# @app.route('/set-port', methods=['POST'])
# def set_port():
#     global java_port
#     data = request.json
#     if 'port' in data:
#         java_port = data['port']
#         return jsonify({'message': 'Port number received successfully'}), 200
#     else:
#         return jsonify({'error': 'Port number not found in request'}), 400
        
# @app.route('/get-port', methods=['GET'])
# def get_port():
#     return jsonify({'java_port': java_port})

# st.write(f"Javascript app is running on port {java_port}")

# # Define a route for handling POST requests
# @app.route('/update-ip', methods=['POST'])
# def update_ip():
#     data = request.json
#     if 'ip' in data:
#         ipa = data['ip']
#         user_ip = ipa
#         st.write('User IP:', ipa)
#         return jsonify({'message': 'IPA received successfully'}), 200
#     else:
#         return jsonify({'error': 'IPA not found in request'}), 400

# # Run the Flask app in a separate thread
# def get_free_port():
#     """Find an available port."""
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind(('localhost', 0))
#     port = s.getsockname()[1]
#     s.close()
#     return port

# if __name__ == '__main__':
#     port = get_free_port()
#     server = threading.Thread(target=app.run, kwargs={'port': port})
#     server.start()

#     st.write(f"Flask app is running on port {port}")


# # Display a message in the Streamlit app
# st.write('Flask app is running.')

# # If you receive an IP address from the Flask server, update the text input field
# st.write(f'User IP: {st.session_state.user_ip}')

# java_port_response = requests.get(f'http://127.0.0.1:{port}/get-port')
# if java_port_response.status_code == 200:
#     java_port = java_port_response.json()['java_port']
#     st.write(f'Java app is running on port {java_port}')

##################

## Functions
# Function to get or create a unique ID for current session
# def get_or_create_user_ID():
#     if 'user_id' not in st.session_state:
#         # Generate a UUID for the tab ID
#         st.session_state.user_id = str(uuid.uuid4())
#     return st.session_state.user_id

# Function to get a unique tab ID for current session
def get_or_create_tab_ID():
    if 'tab_id' not in st.session_state:
        # Generate a UUID for the tab ID
        st.session_state.tab_id = str(uuid.uuid4())
    return st.session_state.tab_id
                    
# Function to log user info
def log_user_info(user_name, user_id, formatted_datetime_entered, tab_id, img, m3_glass_percent, m3_metal_percent, m3_paper_percent, m3_plastic_percent,
                 m2_glass_percent, m2_metal_percent, m2_paper_percent, m2_plastic_percent, m1_glass_percent, m1_metal_percent, m1_paper_percent, m1_plastic_percent):
    #Create a dictionary
    user_info = {
        'Name': user_name,
        'User_ID': user_id,
        'Datetime_Entered': formatted_datetime_entered,
        'Tab_ID': tab_id,
        'Image Name': img,
        'M3 Glass %': m3_glass_percent,
        'M3 Metal %': m3_metal_percent,
        'M3 Paper %': m3_paper_percent,
        'M3 Plastic %': m3_plastic_percent,
        'M2 Glass %': m2_glass_percent,
        'M2 Metal %': m2_metal_percent,
        'M2 Paper %': m2_paper_percent,
        'M2 Plastic %': m2_plastic_percent,
        'M1 Glass %': m1_glass_percent,
        'M1 Metal %': m1_metal_percent,
        'M1 Paper %': m1_paper_percent,
        'M1 Plastic %': m1_plastic_percent
    }
    #Convert the dictionary to a DataFrame
    log_entry_df = pd.DataFrame([user_info])
    return log_entry_df

## TEST Create Scope and Authenticate Google Drive
# Define the scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive',
         # 'https://www.googleapis.com/auth/drive.appdata',
         #  'https://www.googleapis.com/auth/drive.appfolder',
         #  'https://www.googleapis.com/auth/drive.install',
         #  'https://www.googleapis.com/auth/drive.file'          
]

# Function to authenticate with Google Drive API
def authenticate():
    gdrive_auth_secret = st.secrets['GDRIVE_AUTHENTICATION_CREDENTIALS']
    # st.write('gdrive_auth_secret', gdrive_auth_secret)
    # st.write("client_email", gdrive_auth_secret["client_email"])
    # st.write("private_key", gdrive_auth_secret["private_key"])
    creds = service_account.Credentials.from_service_account_info(gdrive_auth_secret, scopes=SCOPES)
    return creds

# Authenticate with Google Drive API
credentials = authenticate()
service = build('drive', 'v3', credentials=credentials)

## Streamlit Interface
st.title('Can We Predict Which Recyclable Category Your Trash is Under?')
st.subheader("Model Disclaimer: Work in Progress 🚧\n\nOur model is in its early stages and is continuously undergoing training and improvements. \
Please note that it's a beginner model, and while it shows promising results, it is not perfect. We appreciate your understanding as we strive to enhance its performance over time. \
\n\nCurrently we are on our 3rd model, and we will be using all 3 models to predict for you.")
user_name = st.text_input('Hi! What is your name?')

## Prompt user to enter their name
if user_name:
    
    #Say Hi
    st.write(f'Hello {user_name}!')
    
    #Get or create a unique user ID for current session
    user_id = cookies["user_id"]

    #Get or create a unique tab ID for current session
    tab_id = get_or_create_tab_ID()

    #Create datetime and format it for log entry
    datetime_format = '%Y-%m-%d %H:%M:%S'
    converted_timezone = pytz.timezone('Asia/Singapore')
    converted_datetime_entered = datetime.now(converted_timezone)
    formatted_datetime_entered = converted_datetime_entered.strftime(datetime_format)
    
    #Merge and display user info
    user_info_headers = f'Name: {user_name} | User ID: {user_id} | Date Entered: {formatted_datetime_entered} | Tab ID: {tab_id}'
    uploaded_image = st.file_uploader("Upload your image...", type=['jpeg','jpg','png'])

    ##Upload Image
    if uploaded_image is not None:
        st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)
    
        if st.button('Predict'):
            if uploaded_image:
                # Define the GitHub repository URL and model file path
                github_repo_url = 'https://github.com/ruskstoic/Recyclables_Classification/raw/master/Downloads'
                model_filename = 'best_model_checkpoint.h5'
                
                # Download the model file from GitHub
                model_url = f'{github_repo_url}/{model_filename}'
                # response = requests.get(model_url)
                
                try:
                    response = requests.get(model_url)
                    response.raise_for_status()  # Check for HTTP errors
                    with open('downloaded_model.h5', 'wb') as model_file:
                        model_file.write(response.content)
                    st.success('Model1 file downloaded successfully! Now downloading Model2...')
                except requests.exceptions.RequestException as e:
                    st.error(f'Failed to download the model file: {str(e)}')
                
                # Check if the download was successful
                if response.status_code == 200:
                    # Save the model file locally
                    with open(model_filename, 'wb') as f:
                        f.write(response.content)
        
                    # Load the Original Model
                    import tensorflow as tf
                    from tensorflow.keras.preprocessing.image import load_img, img_to_array
                    model = tf.keras.models.load_model(model_filename)

                    ## Loading of Models from Google Drive
                    # Define the file ID of your TensorFlow model
                    resnet50_1o1_id = '1CgUsxJ-0Hk4WqdxvJh45a1obiQQ_14JC'
                    finetuned_1o1_id = '1-38aYBp6oNYJqbsGEnqFi-pAvWtb2jal'
                    
                    # Download resnet50 model file
                    request = service.files().get_media(fileId=resnet50_1o1_id)
                    fh = io.BytesIO()
                    downloader = request.execute()
                    fh.write(downloader)
                    fh.seek(0)
                    # Save resnet50 model to a temporary file
                    temp_file_path = "/tmp/resnet50_1o1_model.h5"
                    with open(temp_file_path, "wb") as f:
                        f.write(fh.read())
                    # Load the model from the downloaded file
                    resnet50_1o1_model = tf.keras.models.load_model(temp_file_path)
                    st.success('Model2 file downloaded successfully! Now downloading Model3...')

                    # Download finetuned model file
                    request = service.files().get_media(fileId=finetuned_1o1_id)
                    fh = io.BytesIO()
                    downloader = request.execute()
                    fh.write(downloader)
                    fh.seek(0)
                    # Save resnet50 model to a temporary file
                    temp_file_path_finetuned = "/tmp/resnet50_1o1_finetuned_model.h5"
                    with open(temp_file_path_finetuned, "wb") as f:
                        f.write(fh.read())
                    # Load the model from the downloaded file
                    resnet50_1o1_finetuned_model = tf.keras.models.load_model(temp_file_path_finetuned)
                    st.success('Model3 file downloaded successfully! Now making predictions...')
    
                    # Preprocess the uploaded image
                    img = Image.open(uploaded_image)
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    img = img.resize((224, 224))
                    file_details = {'FileName': uploaded_image.name, 'FileType': uploaded_image.type}
                    st.write(file_details)
                    array_img = np.array(img) / 255.0
                    array_img = np.expand_dims(array_img, axis=0)
    
                    # Make predictions
                    predictions = model.predict(array_img)
                    predictions_resnet = resnet50_1o1_model.predict(array_img)
                    predictions_finetuned = resnet50_1o1_finetuned_model.predict(array_img)
                    class_names = ['Glass', 'Metal', 'Paper', 'Plastic']
                    
                    confidence = format(np.max(predictions) * 100, ".2f")
                    confidence_resnet = format(np.max(predictions_resnet) * 100, ".2f")
                    confidence_finetuned = format(np.max(predictions_finetuned) * 100, ".2f")
                    
                    likely_class = class_names[np.argmax(predictions)]
                    likely_class_resnet = class_names[np.argmax(predictions_resnet)]
                    likely_class_finetuned = class_names[np.argmax(predictions_finetuned)]
    
                    st.write(f'Model1 Prediction: Class-{likely_class}, Confidence-{confidence}%')
                    st.write(f'Model2 Prediction: Class-{likely_class_resnet}, Confidence-{confidence_resnet}%')
                    st.write(f'Model3 Prediction: Class-{likely_class_finetuned}, Confidence-{confidence_finetuned}%')
                    
                    # Save Img and Material Confidence Intervals to Google Sheet
                    m1_glass_percent, m1_metal_percent, m1_paper_percent, m1_plastic_percent = predictions[0][0], predictions[0][1], predictions[0][2], predictions[0][3]
                    m2_glass_percent, m2_metal_percent, m2_paper_percent, m2_plastic_percent = predictions_resnet[0][0], predictions_resnet[0][1], predictions_resnet[0][2], predictions_resnet[0][3]
                    m3_glass_percent, m3_metal_percent, m3_paper_percent, m3_plastic_percent = predictions_finetuned[0][0], predictions_finetuned[0][1], predictions_finetuned[0][2], predictions_finetuned[0][3]
        
                    #Create dictionary of all user info
                    log_entry_df_predictions = log_user_info(user_name=user_name, user_id=user_id, formatted_datetime_entered=formatted_datetime_entered, tab_id=tab_id,img=uploaded_image.name, 
                                                             m3_glass_percent=m3_glass_percent, m3_metal_percent=m3_metal_percent, m3_paper_percent=m3_paper_percent, m3_plastic_percent=m3_plastic_percent,
                                                             m2_glass_percent=m2_glass_percent, m2_metal_percent=m2_metal_percent, m2_paper_percent=m2_paper_percent, m2_plastic_percent=m2_plastic_percent,
                                                             m1_glass_percent=m1_glass_percent, m1_metal_percent=m1_metal_percent, m1_paper_percent=m1_paper_percent, m1_plastic_percent=m1_plastic_percent)
                    #Create Google Sheet Connection Object
                    conn = st.connection('gsheets', type=GSheetsConnection)
                    # Read existing data from the worksheet
                    existing_data = conn.read(worksheet='Sheet1', usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], end='A')
                    # Convert the existing data to a DataFrame (assuming it's already in tabular format)
                    existing_df = pd.DataFrame(existing_data, columns=['Name', 'User_ID', 'Datetime_Entered', 'Tab_ID', 'Image Name', 'M3 Glass %', 'M3 Metal %', 'M3 Paper %', 'M3 Plastic %',
                                                                      'M2 Glass %', 'M2 Metal %', 'M2 Paper %', 'M2 Plastic %', 'M1 Glass %', 'M1 Metal %', 'M1 Paper %', 'M1 Plastic %'])
                    # Concatenate the existing DataFrame with the new entry DataFrame
                    combined_df = pd.concat([existing_df, log_entry_df_predictions], ignore_index=True)
                    # Write the combined DataFrame back to the worksheet
                    conn.update(worksheet='Sheet1', data=combined_df) ##### COMMENT OUT TO TURN OFF UPDATING
                    # Clear cache and display success message
                    st.cache_data.clear()

                    #TEST Save Image into Google Drive
                    img_filename = f'{uploaded_image.name}_{likely_class_finetuned}{confidence_finetuned}%_{user_name}_{user_id[0:8]}.jpg'  # Assuming you want to save as JPEG
                    file_metadata = {
                    'name': img_filename,
                    'parents': ['1fBIYzV6_Q4xt4oPzqYN-2ELSyMU9mYAW']  # Specify the folder ID in which you want to upload the image
                    }
                    # Save the image to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        img.save(temp_file.name, format='JPEG')
                    media = MediaFileUpload(temp_file.name, mimetype='image/jpeg')  # Adjust mimetype as per your file type
                    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute() ##### COMMENT OUT TO TURN OFF UPLOADING
                    st.success(f'Image loaded and predictions made successfully!')
                    # st.success(f'File ID: {file.get("id")}')
                
                else:
                    st.write('Failed to download the model file from GitHub.')

#Streamlit Tracker End
streamlit_analytics.stop_tracking(unsafe_password="test123")
