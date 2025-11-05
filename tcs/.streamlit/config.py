import streamlit as st

# Read secrets from .streamlit/secrets.toml
DB_HOST = st.secrets["database"]["host"]
DB_PORT = st.secrets["database"]["port"]
DB_USER = st.secrets["database"]["user"]
DB_PASSWORD = st.secrets["database"]["password"]
DB_NAME = st.secrets["database"]["database"]

# API keys for external services
tcs_API_KEY = st.secrets["api_keys"]["tcs"] 
OPENAI_API_KEY = st.secrets["api_keys"]["openai"]
# Other configuration settings
DEBUG_MODE = st.secrets["settings"]["debug_mode"]
LOG_LEVEL = st.secrets["settings"]["log_level"]
# Feature flags
FEATURE_X_ENABLED = st.secrets["features"]["feature_x_enabled"]
FEATURE_Y_ENABLED = st.secrets["features"]["feature_y_enabled"]
