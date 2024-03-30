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

## Functions
# Function to get or create a unique ID for current session
def get_or_create_user_ID():
    if 'user_id' not in st.session_state:
        # Generate a UUID for the tab ID
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

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
    # log_entry_df = pd.DataFrame([user_info])
    
    return log_entry_df

    return user_info

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
    datetime_format = '%Y-%m-%d %H:%M:%S'
    converted_timezone = pytz.timezone('Asia/Singapore')
    converted_datetime_entered = datetime.now(converted_timezone)
    formatted_datetime_entered = converted_datetime_entered.strftime(datetime_format)

    #Logging user information
    user_log_filename = 'user_log.txt'
    log_entry = log_user_info(user_name=user_name, user_id=user_id, formatted_datetime_entered=formatted_datetime_entered, tab_id=tab_id)

    #Create Google Sheet Connection Object
    conn = st.connection('gsheets', type=GSheetsConnection)

    # if st.button("Update worksheet"):
    # df = conn.update(
    #     worksheet='Sheet1',
    #     data=log_entry,
    # )

    # st.cache_data.clear()
    # st.write('It works!')

    #TEST
    # Read existing data from the worksheet
    existing_data = conn.read(worksheet='Sheet1')
    
    # Convert the existing data to a DataFrame (assuming it's already in tabular format)
    existing_df = pd.DataFrame(existing_data)
    
    # Create a DataFrame for the new log entry
    new_entry_df = pd.DataFrame([log_entry])
    
    # Concatenate the existing DataFrame with the new entry DataFrame
    combined_df = pd.concat([existing_df, new_entry_df], ignore_index=True)
    
    # Write the combined DataFrame back to the worksheet
    conn.update(worksheet='Sheet1', data=combined_df.values.tolist())
    
    # Clear cache and display success message
    st.cache_data.clear()
    st.write('Data appended successfully!')
    
    # #Dispatch workflow
    # github_token = os.environ.get('WORKFLOW_ACTION_TOKEN')
    # workflow_dispatch_url = f'https://api.github.com/repos/ruskstoic/Recyclables_Classification/actions/workflows/Log%20User%20Input/dispatches'
    # headers = {
    #     'Accept': 'application/vnd.github.v3+json',
    #     'Authorization': f'token {github_token}'
    # }
    # payload = {
    #     'ref': 'main',
    #     'inputs': {
    #         'log_entry': log_entry
    #     }
    # }
    # response = requests.post(workflow_dispatch_url, headers=headers, json=payload)
    # st.write('Status Code:', response.status_code)
    # st.write('Content:', response.content)
    # st.write('Headers:', response.headers)

    # if response.ok:
    #     st.success('User info logged successfully!')
    # else:
    #     st.error('Failed to log user info.')
    
    # subprocess.run([
    #     'curl',
    #     '-X', 'POST',
    #     '-H', f'Authorization: token {github_token}',
    #     '-d', f'{{"ref":"main","inputs":{{"log_entry":"{log_entry}"}}}}',
    #     f'https://api.github.com/repos/ruskstoic/Recyclables_Classification/actions/workflows/Log User Input/dispatches'
    #     ])
    # st.success('User info logged successfully!')

    #Merge and display user info
    user_info = f'Name: {user_name} | User ID: {user_id} | Date Entered: {formatted_datetime_entered} | Tab ID: {tab_id}'
    st.subheader('User Information')
    st.write(log_entry + '\n')
    
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


