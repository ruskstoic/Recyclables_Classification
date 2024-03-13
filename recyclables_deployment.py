# -*- coding: utf-8 -*-
"""recyclables_deployment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aYBKTRhOD8gxXxqPUC9T1K-lDPaxloEV
"""

import sys
print(sys.version)

## Import
import streamlit as st
# import tensorflow as tf
# from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from PIL import Image
import requests
import uuid
from datetime import datetime, timedelta

## Functions
# Function to get or create a unique ID for current session
def get_or_create_user_ID():
    if 'user_id' not in st.session_state:
        # Generate a UUID for the tab ID
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

# def get_or_create_user_ID():
#     if 'user_id' not in st.session_state:
#         # Generate a UUID for the user ID
#         user_id = str(uuid.uuid4())
#         # Set Expiration Time to be 100 Days
#         expiration_time = datetime.now() + timedelta(days=100)
#         # Store User ID and Expiration Time in session state
#         st.session_state.user_id = user_id
#         st.session_state.expiration_time = expiration_time
#     else:
#         # Check if user ID has expired
#         if datetime.now() > st.session_state.expiration_time
#         # Regenerate user ID
#         user_id = str(uuid.uuid4())
#         # Set Expiration Time
#         expiration_time = datetime.now() + timedelta(days=100)
#         # Store User ID and Expiration Time in session state
#         st.session_state.user_id = user_id
#         st.session_state.expiration_time = expiration_time
#     return user_id

# Function to get a unique tab ID for current session
def get_or_create_tab_ID():
    if 'tab_id' not in st.session_state:
        # Generate a UUID for the tab ID
        st.session_state.tab_id = str(uuid.uuid4())
    return st.session_state.tab_id

# Function to log user info
def log_user_info(user_name, user_id, datetime_entered, tab_id):
    # Generate log entry
    log_entry = f'{user_name} | {user_id} | {formatted_datetime} | {tab_id}'
    # Append log entry to log file
    with open('user_log.txt', 'a') as file:
        file.write(log_entry)

## Streamlit Interface
st.title('Can We Predict Which Recyclable Category Your Trash is Under?')
st.subheader("Model Disclaimer: Work in Progress 🚧\n\nOur model is in its early stages and is continuously undergoing training and improvements. \
Please note that it's a beginner model, and while it shows promising results, it is not perfect. We appreciate your understanding as we strive to enhance its performance over time.")

#Prompt user to enter their name
user_name = st.text_input('Hi! What is your name?')

if user_name:
    #Get or create a unique user ID for current session
    user_id = get_or_create_user_ID()

    #Get or create a unique tab ID for current session
    tab_id = get_or_create_tab_ID()

    #Create datetime and format it for log entry
    datetime_entered = datetime.now()
    formatted_datetime = datetime_entered.strftime('%Y-%m-%d %H-:%M:%S')

    #Logging user information
    log_user_info(user_name=user_name, user_id=user_id, datetime_entered=formatted_datetime, tab_id=tab_id)

    #Merge and display user info
    user_info = f'Name: {user_name} | User ID: {user_id} | Date Entered: {formatted_datetime} | Tab ID: {tab_id}'
    st.subheader('User Information')
    st.write(f'{user_info}')
    
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
    
                    st.write('Prediction:')
                    st.write(f'Class: {class_names[np.argmax(predictions)]}')
                    st.write(f'Confidence: {np.max(predictions) * 100:.2f}%')
                else:
                    st.write('Failed to download the model file from GitHub.')


