import streamlit as st
import pandas as pd
import io
from PIL import Image
import google.generativeai as genai
from DB_Engine import engine
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

api_key =  os.getenv("google_api_key")
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
st.image(image, use_column_width=True, caption="Uploaded Image") 

# 2. Process Button
submit = st.button("Extract the Data")

# If the button is clicked, fetch data and store in session_state
if submit:
    prompt = """
    Analyze this image of a handwritten table. 
    Extract the data into a clean CSV format.
    Rules:
    1. Output ONLY the raw CSV text. Do not include markdown formatting.
    """
    
    # API CALL
    response = model.generate_content([prompt, image])
    csv_data = response.text.strip()

    # Clean up markdown if present
    if csv_data.startswith("```"):
        csv_data = csv_data.replace("```csv", "").replace("```", "").strip()
    
    # STORE IN SESSION STATE, this ensures the data persists when you click other buttons
    st.session_state['csv_data'] = csv_data

# st.session_state['csv_data'] = 'Prod date,Exp date,Product Name,Batch No.,pH 1% (1g/99ml)\n04.11.23,04.11.24,DB2 Stabiliser,893,7.17\n04.11.23,04.11.24,DB2 Stabiliser,89651654,7.17\n04.11.23,04.11.24,DB2 Stabiliser,895,7.16\n04.11.23,04.11.24,DB2 Stabiliser,896,7.17\n04.11.23,04.11.24,DB2 Stabiliser,897,7.13\n04.11.23,04.11.24,DB2 Stabiliser,898,7.19'

upload_clicked = False

# CHECK IF DATA EXISTS IN SESSION STATE
if 'csv_data' in st.session_state:
    csv_data = st.session_state['csv_data']
    
    st.success("Data Extraction Complete!")
    st.subheader("Preview Data")
    st.text_area("Content", value=csv_data, height=200)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="converted_batch_data.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        # Capture the click event in a variable
        upload_clicked = st.button("Upload to Database", use_container_width=True)

if upload_clicked:
    try:
        df = pd.read_csv(io.StringIO(csv_data))
        st.dataframe(df, use_container_width=True) 

        TABLE_NAME = "people"
        df.to_sql(
            TABLE_NAME,
            engine,
            if_exists="append", # Need to implement safe append
            index=False # Do not write DataFrame index as a column
        )
        st.success(f"Successfully uploaded to table: {TABLE_NAME}")
    except Exception as e:
        st.error(f"Error uploading to database: {e}")
