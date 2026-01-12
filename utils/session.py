import streamlit as st
from .helpers import RateLimiter

def init_session_state():
    """Initialize all session state variables."""
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'repo_tree' not in st.session_state:
        st.session_state.repo_tree = None
    if 'repo_info' not in st.session_state:
        st.session_state.repo_info = None
    if 'raw_tree' not in st.session_state:
        st.session_state.raw_tree = None
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "GPT-4o"
    if 'file_search' not in st.session_state:
        st.session_state.file_search = ""
    if 'github_token' not in st.session_state:
        st.session_state.github_token = ""
    if 'rate_limiter' not in st.session_state:
        st.session_state.rate_limiter = RateLimiter(max_calls=60, time_window=3600)  # 60 calls per hour
    if 'file_hashes' not in st.session_state:
        st.session_state.file_hashes = {}  # For deduplication

    # Settings persistence (remember user preferences)
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'output_format': 'TXT',
            'sanitize_keys': False,
            'remove_comments': False,
            'selected_model': 'GPT-4o'
        }
