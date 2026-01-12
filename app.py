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

if not st.session_state.uploaded_files:
        st.markdown("### 👋 Welcome to DocuStream")
        st.markdown("To get started, add files using one of the methods below:")
        
        # Add interactive onboarding cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="onboarding-card">
                <div class="onboarding-icon">📂</div>
                <h4 class="onboarding-title">Upload</h4>
                <p class="onboarding-desc">Drag & drop files or browse your local storage</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="onboarding-card">
                <div class="onboarding-icon">☁️</div>
                <h4 class="onboarding-title">GitHub</h4>
                <p class="onboarding-desc">Import directly from public repositories</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="onboarding-card">
                <div class="onboarding-icon">📝</div>
                <h4 class="onboarding-title">Paste</h4>
                <p class="onboarding-desc">Quickly add text content or Gist URLs</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Quick Tips Section
        st.markdown("""
        <div class="quick-tip">
            <div class="tip-icon">💡</div>
            <div class="tip-content">
                <strong>Pro Tip: Smart Filtering</strong>
                <p>When importing from GitHub, you can filter valid source files automatically to skip configs and documentation.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    


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
