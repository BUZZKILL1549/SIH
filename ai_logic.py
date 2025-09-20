import tensorflow as tf
from PIL import Image
import numpy as np
import streamlit as st
import keras

'''
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("converted_savedmodel/")

model = load_model()
'''

layer = keras.layers.TFSMLayer("converted_savedmodel/model.savedmodel", call_endpoint="serving_default")

with open("converted_savedmodel/labels.txt") as f:
    class_names = [line.strip() for line in f.readlines()]

def predict(image):
    img = image.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    outputs = layer(img_array)

    preds = list(outputs.values())[0].numpy()
    raw_label = class_names[np.argmax(preds)]
    # Map to 'Wet' or 'Dry' only
    if "Wet" in raw_label:
        label = "Wet"
    elif "Dry" in raw_label:
        label = "Dry"
    else:
        label = raw_label  # fallback, should not happen
    return label, np.max(preds)