import streamlit as st
import pandas as pd
import PyPDF2
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from supabase import create_client, Client
import os
from datetime import datetime
import chardet
import uuid
import time

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# Supabase credentials
SUPABASE_URL = "https://fpzjwfrdqmwvpieysvbo.supabase.co"  # Replace with your Supabase URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZwemp3ZnJkcW13dnBpZXlzdmJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk2MjAzMTgsImV4cCI6MjA2NTE5NjMxOH0.oz3mhk_PAWuodODGIHFUEv93quWQRhMwe6agBmDD2vU"  # Replace with your Supabase anon key

# Retry logic for Supabase connection
def connect_to_supabase(retries=3, delay=5):
    for attempt in range(retries):
        try:
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            # Test the connection
            client.table('users').select('user_id').limit(1).execute()
            st.write("Successfully connected to Supabase")
            return client
        except Exception as e:
            st.error(f"Attempt {attempt + 1}/{retries} - Failed to connect to Supabase: {str(e)}")
            if attempt < retries - 1:
                st.write(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                st.error("Could not connect to Supabase after multiple attempts.")
                st.error(f"1. Ensure the Supabase URL ({SUPABASE_URL}) is correct.")
                st.error("2. Verify your internet connection and DNS settings.")
                st.error("3. Check if the Supabase project exists and the anon key is valid.")
                st.error("4. Ensure there are no firewall rules blocking HTTPS traffic to Supabase.")
                st.stop()

try:
    supabase: Client = connect_to_supabase()
except Exception as e:
    st.error(f"Supabase connection failed: {str(e)}")
    st.stop()

# Validate UUID
def is_valid_uuid(val):
    pattern = r'^[0-9a-fA-F\-]{36}$'
    return re.fullmatch(pattern, val) is not None

# Preprocessing steps
def general_preprocessing(text):
    if isinstance(text, bytes):
        encoding = chardet.detect(text)['encoding']
        text = text.decode(encoding, errors='replace')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.]', '', text)
    text = text.lower()
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return ' '.join(tokens)

def preprocess_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = " ".join([page.extract_text() or "" for page in reader.pages])
        return general_preprocessing(text)
    except Exception as e:
        raise ValueError(f"Failed to preprocess PDF: {str(e)}")

def preprocess_excel(file):
    try:
        df = pd.read_excel(file).fillna('').dropna(how='all').dropna(axis=1, how='all')
        df.columns = [c.lower().strip() for c in df.columns]
        return general_preprocessing(df.to_string(index=False))
    except Exception as e:
        raise ValueError(f"Failed to preprocess Excel: {str(e)}")

def preprocess_csv(file):
    try:
        df = pd.read_csv(file).fillna('')
        df.columns = [c.lower().strip() for c in df.columns]
        return general_preprocessing(df.to_string(index=False))
    except Exception as e:
        raise ValueError(f"Failed to preprocess CSV: {str(e)}")

def preprocess_text(file):
    try:
        text = file.read().decode('utf-8', errors='replace')
        return general_preprocessing(text)
    except Exception as e:
        raise ValueError(f"Failed to preprocess Text: {str(e)}")

# --- Streamlit UI ---
st.title("File Upload Interface")

# Extract user_id from query
query_params = st.query_params
user_id = query_params.get("user_id", "")
if isinstance(user_id, list):
    user_id = user_id[0] if user_id else ""

if not user_id or not is_valid_uuid(user_id):
    st.error("Invalid or missing User ID.")
    st.markdown("[Go to Login/Register](http://localhost:5000)", unsafe_allow_html=True)
    st.stop()

uploaded_file = st.file_uploader("Upload your file (CSV, Excel, PDF, Text)", type=["csv", "xlsx", "xls", "pdf", "txt"])

if uploaded_file:
    try:
        file_id = str(uuid.uuid4())
        file_type = uploaded_file.type
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{uploaded_file.name}"
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Preprocess based on file type
        if file_type == "application/pdf":
            preprocessed_data = preprocess_pdf(uploaded_file)
        elif file_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            preprocessed_data = preprocess_excel(uploaded_file)
        elif file_type == "text/csv":
            preprocessed_data = preprocess_csv(uploaded_file)
        elif file_type == "text/plain":
            preprocessed_data = preprocess_text(uploaded_file)
        else:
            st.error("Unsupported file type!")
            st.stop()

        # Save preprocessed data
        os.makedirs("preprocessed", exist_ok=True)
        cleaned_filename = uploaded_file.name.rsplit('.', 1)[0] + "_preprocessed.csv"
        storage_path = f"preprocessed/{cleaned_filename}"
        df_clean = pd.DataFrame({"cleaned_text": [preprocessed_data]})
        df_clean.to_csv(storage_path, index=False)

        # Store in Supabase
        timestamp = datetime.utcnow().isoformat()

        # Insert into file_uploads
        try:
            supabase.table("file_uploads").insert({
                "file_id": file_id,
                "user_id": user_id,
                "file_name": uploaded_file.name,
                "file_path": file_path,
                "upload_time": timestamp
            }).execute()
        except Exception as e:
            st.error(f"Failed to store file metadata in Supabase: {str(e)}")
            st.stop()

        # Insert into data_preprocessing_logs
        try:
            supabase.table("data_preprocessing_logs").insert({
                "preprocess_id": str(uuid.uuid4()),
                "file_id": file_id,
                "user_id": user_id,
                "status": "completed",
                "preprocess_time": timestamp
            }).execute()
        except Exception as e:
            st.error(f"Failed to log preprocessing in Supabase: {str(e)}")
            st.stop()

        # Insert into datasets
        try:
            supabase.table("datasets").insert({
                "dataset_id": str(uuid.uuid4()),
                "file_id": file_id,
                "user_id": user_id,
                "dataset_name": cleaned_filename,
                "storage_path": storage_path,
                "created_at": timestamp
            }).execute()
        except Exception as e:
            st.error(f"Failed to store dataset in Supabase: {str(e)}")
            st.stop()

        # Success Message
        st.success("✅ File uploaded successfully!")

    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        st.stop()

# --- Minimal message box ---
user_message = st.text_input("Your Message:")
if user_message:
    st.write("📩 Message received.")