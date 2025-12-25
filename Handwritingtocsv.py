import streamlit as st
from PIL import Image
import google.generativeai as genai
import io
import pandas as pd

api_key = 'AIzaSyBFKAQnqBGiaNc79Veh9U7V7IAKwZTuHa0' 

genai.configure(api_key=api_key)

model = genai.GenerativeModel('models/gemini-2.5-flash')

# --- UI LAYOUT ---
st.title("📝 Handwritten Table to CSV Converter")

uploaded_file = st.file_uploader(
    "Upload Handwritten Table Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is None:
    st.info("Please upload an image to continue.")
    st.stop()

# 1. Display the image
image = Image.open(uploaded_file)
st.image(image, use_column_width=True,caption="Uploaded Image") 

# 2. Process Button
submit = st.button("Convert to CSV")
if not submit:
    st.stop()

prompt = """
Analyze this image of a handwritten table. 
Extract the data into a clean CSV format.

Rules:
1. Output ONLY the raw CSV text. Do not include markdown formatting (like ```csv).
"""

# --- API CALL ---
response = model.generate_content([prompt, image])
csv_data = response.text.strip()

# Clean up if the model adds markdown ticks despite instructions
if csv_data.startswith("```"):
    csv_data = csv_data.replace("```csv", "").replace("```", "").strip()

# --- RESULT DISPLAY ---
st.success("Conversion Complete!")

st.subheader("Preview Data")
st.text_area("CSV Content", value=csv_data, height=200)

# --- DOWNLOAD BUTTON ---
st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="converted_batch_data.csv",
    mime="text/csv"
)

