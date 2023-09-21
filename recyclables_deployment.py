# -*- coding: utf-8 -*-
"""recyclables_deployment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aYBKTRhOD8gxXxqPUC9T1K-lDPaxloEV
"""

# Import
import streamlit as st
import subprocess
import pkgutil

if not pkgutil.find_loader("tensorflow"):
    st.warning("Installing TensorFlow...")
    subprocess.call(['pip', 'install', 'tensorflow'])

import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from PIL import Image



# Load Model
filename = 'best_model_checkpoint.h5'
model = tf.keras.load_model(f'/content/drive/MyDrive/Garbage Classification/Saved_Models/{filename}')

# Preprocess and Predict

def preprocess(uploaded_image):
  img = Image.open(uploaded_image)
  img = img.resize((224,224)) #resize to dimension
  img = np.array(img) / 255.0 #normalize pixel values
  img = np.expand_dims(img,axis=0)
  return img

def predict(uploaded_image):
  img = preprocess(uploaded_image)
  predictions = model.predict(img)
  return predictions

# Streamlit Interface

st.title('Can We Predict Which Recyclable Category Your Trash is Under?')

uploaded_image = st.file_uploader("Upload your image...", type=['jpeg','jpg','png'])

if uploaded_image is not None:
  st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)

  if st.button('Predict'):
    if uploaded_image:
      predictions = predict(uploaded_image)
      class_names = ['Glass','Metal','Paper','Plastic']

      st.write('Prediction:')
      st.write(f'Class: {class_names[np.argmax(predictions)]}')
      st.write(f'Confidence: {np.max(predictions) * 100:.2f}%')

