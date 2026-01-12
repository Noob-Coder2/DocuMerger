import streamlit as st

def apply_custom_styles():
    st.markdown("""
<style>
    /* ==================== CSS Variables for Theme Adaptation ==================== */
    :root {
        --glass-bg-light: rgba(255, 255, 255, 0.7);
        --glass-bg-dark: rgba(30, 30, 40, 0.7);
        --glass-border-light: rgba(255, 255, 255, 0.3);
        --glass-border-dark: rgba(255, 255, 255, 0.1);
        --shadow-light: rgba(0, 0, 0, 0.08);
        --shadow-dark: rgba(0, 0, 0, 0.3);
        --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --accent-gradient-hover: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
    }

    /* ==================== Global Styles ==================== */
    /* Let Streamlit handle background colors natively - only add enhancements */
    .stApp {
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    }
    
    /* ==================== Typography ==================== */
    h1 {
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    
    h2, h3 {
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    
    /* ==================== Glassmorphism Cards ==================== */
    .metric-card {
        background: rgba(102, 126, 234, 0.1);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--accent-gradient);
        border-radius: 4px 0 0 4px;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
    }
    
    .metric-card h4 {
        margin: 0 0 4px 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .metric-card small {
        opacity: 0.7;
    }
    
    /* ==================== File Upload Dropzone ==================== */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(102, 126, 234, 0.4);
        border-radius: 16px;
        padding: 24px;
        background: rgba(102, 126, 234, 0.05);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(102, 126, 234, 0.8);
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* ==================== Buttons ==================== */
    .stButton > button {
        border-radius: 12px;
        height: auto;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button[kind="primary"] {
        background: var(--accent-gradient);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px var(--shadow-light);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* ==================== Tabs Styling ==================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        padding: 4px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-gradient);
        color: white !important;
    }
    
    /* ==================== Form & Input Styling ==================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }
    
    /* ==================== Expander Styling ==================== */
    .streamlit-expanderHeader {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* ==================== Progress Bar ==================== */
    .stProgress > div > div > div {
        background: var(--accent-gradient);
        border-radius: 10px;
    }
    
    /* ==================== Code Block Styling ==================== */
    .stCodeBlock {
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* ==================== Waiting Placeholder ==================== */
    .waiting-placeholder {
        height: 400px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        background: rgba(102, 126, 234, 0.05);
        backdrop-filter: blur(8px);
        color: rgba(102, 126, 234, 0.7);
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* ==================== Container Alignment ==================== */
    [data-testid="stVerticalBlock"] > div {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    
    /* Column alignment */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
    }
    
    [data-testid="column"] > div {
        flex: 1;
    }
    
    /* File queue items alignment */
    [data-testid="stHorizontalBlock"] {
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Consistent spacing for form elements */
    .stForm [data-testid="stVerticalBlock"] {
        gap: 1rem;
    }
    
    /* ==================== Divider Styling ==================== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 1.5rem 0;
    }
    
    /* ==================== Toast/Alert Styling ==================== */
    .stAlert {
        border-radius: 12px;
        border: none;
        backdrop-filter: blur(8px);
    }
    
    /* ==================== Scrollbar Styling ==================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
    }
    
    /* ==================== Animation Keyframes ==================== */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    /* Loading state */
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
            
    /* Add to your existing CSS block */
    /* Better focus states */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div:focus {
        outline: 2px solid #667eea !important;
        outline-offset: 2px !important;
    }

    /* Loading spinner enhancement */
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .stSpinner > div {
        border: 3px solid rgba(102, 126, 234, 0.2) !important;
        border-top-color: #667eea !important;
        animation: spin 1s linear infinite !important;
    }

    /* Better button hover effects */
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }

    /* Smooth transitions for all interactive elements */
    button, input, select, textarea, .stExpander {
        transition: all 0.2s ease !important;
    }

    /* Enhanced file uploader dropzone */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(102, 126, 234, 0.4) !important;
        border-radius: 16px !important;
        padding: 32px !important;
        background: rgba(102, 126, 234, 0.05) !important;
        backdrop-filter: blur(8px) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #667eea !important;
        background: rgba(102, 126, 234, 0.1) !important;
        transform: scale(1.01) !important;
    }

    /* Progress bar animation */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        animation: shimmer 2s infinite !important;
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* Toast notification styling */
    [data-testid="stToast"] {
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(12px) !important;
    }

    /* Better expander styling */
    .streamlit-expanderHeader {
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(102, 126, 234, 0.1) !important;
        border-color: #667eea !important;
    }

    /* Column alignment improvements */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 0.5rem !important;
    }

    /* Form spacing */
    .stForm {
        padding: 1rem !important;
        border-radius: 12px !important;
        background: rgba(102, 126, 234, 0.03) !important;
        border: 1px solid rgba(102, 126, 234, 0.1) !important;
    }

    /* Alert styling enhancement */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }

    /* Code block improvements */
    .stCodeBlock {
        border-radius: 12px !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        background: rgba(0, 0, 0, 0.05) !important;
        max-height: 400px !important;
        overflow-y: auto !important;
    }

    /* Scrollbar styling for code blocks */
    .stCodeBlock::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }

    .stCodeBlock::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.05) !important;
        border-radius: 4px !important;
    }

    .stCodeBlock::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5) !important;
        border-radius: 4px !important;
    }

    .stCodeBlock::-webkit-scrollbar-thumb:hover {
        background: #667eea !important;
    }

    /* Button kind variations */
    .stButton > button[kind="secondary"] {
        background: rgba(102, 126, 234, 0.1) !important;
        color: #667eea !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(102, 126, 234, 0.2) !important;
        border-color: #667eea !important;
    }

    /* Disabled state styling */
    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }

    /* Tab hover effects */
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1) !important;
        border-radius: 10px !important;
    }

    /* File uploader file list styling */
    [data-testid="stFileUploader"] ul {
        border-radius: 8px !important;
        background: rgba(102, 126, 234, 0.05) !important;
    }

    [data-testid="stFileUploader"] li {
        border-radius: 6px !important;
        margin: 4px 0 !important;
        padding: 8px !important;
        background: rgba(255, 255, 255, 0.5) !important;
    }

    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: rgba(30, 30, 40, 0.8) !important;
            color: #e0e0e0 !important;
            border-color: rgba(102, 126, 234, 0.3) !important;
        }
        
        .stSelectbox > div > div {
            background: rgba(30, 30, 40, 0.8) !important;
            color: #e0e0e0 !important;
            border-color: rgba(102, 126, 234, 0.3) !important;
        }
        
        .stCodeBlock {
            background: rgba(0, 0, 0, 0.2) !important;
        }
        
        .onboarding-title {
            color: #e0e0e0 !important;
        }
        
        .onboarding-desc {
            color: #b0b0b0 !important;
        }
    }

    /* ==================== Onboarding Cards ==================== */
    .onboarding-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        cursor: default;
    }
    
    .onboarding-card:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: #667eea;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .onboarding-icon {
        font-size: 2.5rem;
        margin-bottom: 8px;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .onboarding-title {
        font-weight: 700;
        font-size: 1.1rem;
        margin: 0;
        color: inherit;
    }
    
    .onboarding-desc {
        font-size: 0.9rem;
        opacity: 0.7;
        margin: 0;
        line-height: 1.4;
    }
    
    /* ==================== Quick Tips ==================== */
    .quick-tip {
        display: flex;
        align-items: start;
        gap: 12px;
        background: rgba(102, 126, 234, 0.05);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 16px;
        margin-top: 24px;
    }
    
    .tip-icon {
        color: #667eea;
        font-size: 1.2rem;
    }
    
    .tip-content strong {
        display: block;
        margin-bottom: 4px;
        color: #667eea;
    }
    
    .tip-content p {
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.8;
    }
            
</style>
""", unsafe_allow_html=True)
