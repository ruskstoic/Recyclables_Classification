# -*- coding: utf-8 -*-
"""recyclables_deployment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aYBKTRhOD8gxXxqPUC9T1K-lDPaxloEV
"""

# Import
import streamlit as st
import requests
# import tensorflow as tf
# from tensorflow.keras.preprocessing.image import load_img, img_to_array
# import numpy as np
# from PIL import Image

# Streamlit Interface
st.title('Can We Predict Which Recyclable Category Your Trash is Under?')

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
            response = requests.get(model_url)
            
            # Check if the download was successful
            if response.status_code == 200:
                # Save the model file locally
                with open(model_filename, 'wb') as f:
                    f.write(response.content)

                # Load the model
                model = tf.keras.models.load_model(model_filename)

                # Preprocess the uploaded image
                img = Image.open(uploaded_image)
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


