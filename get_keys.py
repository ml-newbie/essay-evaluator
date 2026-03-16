import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str):

    # Try Streamlit secrets first
    if key in st.secrets:
        return st.secrets[key]

    # Fallback to .env
    return os.getenv(key)