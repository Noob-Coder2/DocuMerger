import streamlit as st
from components.styles import apply_custom_styles
from utils.session import init_session_state
from components.sidebar import render_sidebar
from components.file_manager import render_file_queue
from components.settings import render_settings
from components.preview import render_preview

# --- Page Config ---
st.set_page_config(
    page_title="DocuStream Pro",
    page_icon="📄",
    layout="wide",
)

# Initialize
apply_custom_styles()
init_session_state()

# --- Main Layout ---
st.title("📄 DocuStream Pro")
st.caption("Advanced Document Consolidation Platform")

# Split Screen: Control Panel (Left), Live Preview (Right)
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    # 1. Input Tab
    render_sidebar()
    
    # 2. File Organization
    render_file_queue()

    # 3. Settings & Form
    submitted, output_format, output_filename, sanitize_keys, remove_comments = render_settings()

with right_col:
    # 4. Live Preview & Result
    render_preview(submitted, output_format, output_filename, sanitize_keys, remove_comments)
