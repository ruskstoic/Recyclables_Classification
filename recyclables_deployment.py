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
# import tensorflow as tf
# from tensorflow.keras.preprocessing.image import load_img, img_to_array
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

##TEST DETA Drive

# DETA_key = os.environ.get()
# deta = Deta(DETA_key)
# drive = deta.Drive('insert_drive_name')
# st.set_option('deprecation.showfileUploaderEncoding', False) # Enabling the automatic file decoder

#Put at bottom of code
# uploaded_img = st.file_uploader("Choose photos to upload", accept_multiple_files=True, type=['png', 'jpeg', 'jpg'])
# name = f'{confidence}%{likely_class}_{user_info}'
# path ='./' + name # Creating path string which is basically ["./image.jpg"]
# drive.put(name, path=path) # so, we have our file name and path, so uploading images to the drive
# os.remove(name) # Finally deleting it from root folder


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
def log_user_info(user_name, user_id, formatted_datetime_entered, tab_id):
    #Create a dictionary
    user_info = {
        'Name': user_name,
        'User_ID': user_id,
        'Datetime_Entered': formatted_datetime_entered,
        'Tab_ID': tab_id
    }
    #Convert the dictionary to a DataFrame
    log_entry_df = pd.DataFrame([user_info])
    return log_entry_df

## Streamlit Interface
st.title('Can We Predict Which Recyclable Category Your Trash is Under?')
st.subheader("Model Disclaimer: Work in Progress 🚧\n\nOur model is in its early stages and is continuously undergoing training and improvements. \
Please note that it's a beginner model, and while it shows promising results, it is not perfect. We appreciate your understanding as we strive to enhance its performance over time.")


#Prompt user to enter their name
user_name = st.text_input('Hi! What is your name?')

if user_name:
    #Get or create a unique user ID for current session
    user_id = cookies["user_id"]

    #Get or create a unique tab ID for current session
    tab_id = get_or_create_tab_ID()

    #Create datetime and format it for log entry
    datetime_format = '%Y-%m-%d %H:%M:%S'
    converted_timezone = pytz.timezone('Asia/Singapore')
    converted_datetime_entered = datetime.now(converted_timezone)
    formatted_datetime_entered = converted_datetime_entered.strftime(datetime_format)

    #Logging user information
    user_log_filename = 'user_log.txt'
    log_entry_df = log_user_info(user_name=user_name, user_id=user_id, formatted_datetime_entered=formatted_datetime_entered, tab_id=tab_id)

    #Create Google Sheet Connection Object
    conn = st.connection('gsheets', type=GSheetsConnection)
    
    # Read existing data from the worksheet
    existing_data = conn.read(worksheet='Sheet1', usecols=[0,1,2,3], end='A')
    
    # Convert the existing data to a DataFrame (assuming it's already in tabular format)
    existing_df = pd.DataFrame(existing_data, columns=['Name', 'User_ID', 'Datetime_Entered', 'Tab_ID'])
    
    # Concatenate the existing DataFrame with the new entry DataFrame
    combined_df = pd.concat([existing_df, log_entry_df], ignore_index=True)
    # st.write('combined_df', combined_df)
    
    # Write the combined DataFrame back to the worksheet
    conn.update(worksheet='Sheet1', data=combined_df)
    
    # Clear cache and display success message
    st.cache_data.clear()
    st.write('Data appended successfully!')
    
    #Merge and display user info
    user_info_headers = f'Name: {user_name} | User ID: {user_id} | Date Entered: {formatted_datetime_entered} | Tab ID: {tab_id}'
    user_info = f'{user_name}_{user_id}_{formatted_datetime_entered}_{tab_id}'
    st.subheader('User Information')
    st.write(log_entry_df + '\n')
    
    uploaded_image = st.file_uploader("Upload your image...", type=['jpeg','jpg','png'])
    
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
                    st.success('Model file downloaded successfully!')
                except requests.exceptions.RequestException as e:
                    st.error(f'Failed to download the model file: {str(e)}')
                
                # Check if the download was successful
                if response.status_code == 200:
                    # Save the model file locally
                    with open(model_filename, 'wb') as f:
                        f.write(response.content)
    
                    # Load the model
                    import tensorflow as tf
                    from tensorflow.keras.preprocessing.image import load_img, img_to_array
                    model = tf.keras.models.load_model(model_filename)
    
                    # Preprocess the uploaded image
                    img = Image.open(uploaded_image)
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    img = img.resize((224, 224))
                    img = np.array(img) / 255.0
                    img = np.expand_dims(img, axis=0)
    
                    # Make predictions
                    predictions = model.predict(img)
                    class_names = ['Glass', 'Metal', 'Paper', 'Plastic']
                    confidence = format(np.max(predictions) * 100, ".2f")
                    likely_class = class_names[np.argmax(predictions)]
    
                    st.write('Prediction:')
                    st.write(f'Class: {likely_class}')
                    st.write(f'Confidence: {confidence}%')

                    # Save Img and Result to Deta Drive
                
                else:
                    st.write('Failed to download the model file from GitHub.')

#Streamlit Tracker End
streamlit_analytics.stop_tracking(unsafe_password="test123")
