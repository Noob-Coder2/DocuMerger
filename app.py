import streamlit as st
import os
import io
import requests
from processor import DocumentProcessor, MODEL_CONFIGS
from github_api import GitHubAPI, FILTER_PRESETS, apply_tree_filters, is_likely_file
from streamlit_sortables import sort_items
from streamlit_tree_select import tree_select
from utils import RateLimiter, validate_filename, sanitize_filename, compute_file_hash, format_file_size

# --- Page Config ---
st.set_page_config(
    page_title="DocuStream Pro",
    page_icon="📄",
    layout="wide",
)

# --- Custom CSS (Professional Theme with Dark Mode Support) ---
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
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
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

# --- Helper Functions ---
def fetch_from_github(url):
    """Fetches raw content from a GitHub URL and returns a BytesIO object."""
    try:
        # Basic URL Validation
        if not url.startswith("http"):
            return None, "Invalid URL format."
        
        # Security: Validate that URL is from GitHub domains only (prevent SSRF)
        from urllib.parse import urlparse
        parsed = urlparse(url)
        allowed_domains = ['github.com', 'raw.githubusercontent.com', 'gist.github.com']
        if not any(parsed.netloc == domain or parsed.netloc.endswith('.' + domain) for domain in allowed_domains):
            return None, "Invalid URL. Only GitHub URLs are allowed (github.com, raw.githubusercontent.com, gist.github.com)."
            
        # Convert 'blob' or 'tree' (if user mistakes folder for file, though tree support needs API) to raw
        # Case 1: Standard Blob URL -> Convert to Raw
        # Ex: https://github.com/user/repo/blob/main/file.txt -> https://raw.githubusercontent.com/user/repo/main/file.txt
        if "github.com" in url and "/blob/" in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            
        # Case 2: User provided a 'tree' URL (Folder) -> Not supported yet, fail gracefully
        if "/tree/" in url:
            return None, "Folder import not supported. Please provide a file URL."

        # Case 3: Raw URL provided directly -> Use as is
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Validation: Check if we got an HTML page (likely an error or wrong URL type for a code file)
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type and not url.endswith('.html'):
            return None, "URL returned a webpage, not a file. Please ensure you are using a direct file link."

        filename = url.split("/")[-1]
        file_obj = io.BytesIO(response.content)
        file_obj.name = filename
        return file_obj, None # Success
        
    except requests.exceptions.HTTPError:
        return None, "File not found (404) or private repo."
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except Exception as e:
        return None, f"Error: {str(e)}"

# --- Main Layout ---
st.title("📄 DocuStream Pro")
st.caption("Advanced Document Consolidation Platform")

# Split Screen: Control Panel (Left), Live Preview (Right)
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("🛠️ Control Panel")
    
    # 1. Import Source Tabs
    tab_upload, tab_paste, tab_github = st.tabs(["📂 Upload Files", "📝 Paste/Gist", "☁️ GitHub Import"])
    
    with tab_upload:
        new_files = st.file_uploader(
            "Drag & Drop files", 
            accept_multiple_files=True,
            key="file_uploader"
        )
        if new_files:
            for nf in new_files:
                if not any(existing.name == nf.name for existing in st.session_state.uploaded_files):
                    st.session_state.uploaded_files.append(nf)
    
    with tab_paste:
        st.caption("Paste code/text or import from GitHub Gist")
        
        # Paste text option
        paste_filename = st.text_input("Filename", value="pasted_content.txt", key="paste_filename", help="Name for your pasted content")
        paste_content = st.text_area("Paste your content here", height=200, key="paste_content", placeholder="Paste code, text, or any content...")
        
        if st.button("➕ Add to Queue", key="add_paste_btn", disabled=not paste_content):
            if paste_content and paste_filename:
                # Validate filename
                is_valid, error_msg = validate_filename(paste_filename)
                if not is_valid:
                    st.error(f"Invalid filename: {error_msg}")
                    paste_filename = sanitize_filename(paste_filename)
                    st.info(f"Sanitized to: {paste_filename}")
                
                file_obj = io.BytesIO(paste_content.encode('utf-8'))
                file_obj.name = paste_filename
                
                # Check for duplicate by content hash
                file_hash = compute_file_hash(file_obj)
                
                # Check if file already exists by name
                if not any(existing.name == file_obj.name for existing in st.session_state.uploaded_files):
                    # Check for duplicate content
                    if file_hash in st.session_state.file_hashes:
                        original_name = st.session_state.file_hashes[file_hash]
                        st.warning(f"Duplicate content detected! Same as '{original_name}'")
                    else:
                        st.session_state.uploaded_files.append(file_obj)
                        st.session_state.file_hashes[file_hash] = file_obj.name
                        st.success(f"Added: {paste_filename}")
                        st.rerun()  # Only rerun if file was added
                else:
                    st.warning(f"File '{paste_filename}' already in queue")
                    # No rerun needed - just show warning
        
        st.markdown("---")
        st.markdown("**Or import from Gist:**")
        
        gist_url = st.text_input("Gist URL", placeholder="https://gist.github.com/username/gist_id", key="gist_url_input")
        if st.button("📥 Fetch Gist", key="fetch_gist_btn"):
            if gist_url:
                gist_id = GitHubAPI.parse_gist_url(gist_url)
                if gist_id:
                    with st.spinner("Fetching Gist..."):
                        files, error = GitHubAPI.fetch_gist(gist_id)
                        if files:
                            added_count = 0
                            for file_obj in files:
                                if not any(existing.name == file_obj.name for existing in st.session_state.uploaded_files):
                                    st.session_state.uploaded_files.append(file_obj)
                                    added_count += 1
                            if added_count > 0:
                                st.success(f"Added {added_count} file(s) from Gist")
                                st.rerun()  # Only rerun if files were added
                            else:
                                st.info("All files from Gist already in queue")
                        else:
                            st.error(error or "Failed to fetch Gist")
                else:
                    st.error("Invalid Gist URL")
                    
    with tab_github:
        # Sub-tabs for different GitHub import modes
        github_single, github_explorer = st.tabs(["📄 Single File", "🌳 Repo Explorer"])
        
        with github_single:
            github_url = st.text_input("Enter Public File URL", placeholder="https://github.com/user/repo/blob/main/file.py", help="Paste the URL of the file view on GitHub.")
            if st.button("Fetch from URL"):
                if github_url:
                    with st.spinner("Fetching..."):
                        file_obj, error_msg = fetch_from_github(github_url)
                        if file_obj:
                            st.session_state.uploaded_files.append(file_obj)
                            st.success(f"Added: {file_obj.name}")
                        else:
                            st.error(f"Failed: {error_msg}")
        
        with github_explorer:
            st.caption("Browse & select multiple files from a public repository")
            
            # Repository URL input
            repo_url = st.text_input(
                "Repository URL", 
                placeholder="https://github.com/owner/repo",
                help="Enter the URL of a public GitHub repository",
                key="repo_url_input"
            )
            
            # Optional token for private repos or rate limits
            with st.expander("🔑 Advanced: Add Token (optional)"):
                token_input = st.text_input(
                    "GitHub Personal Access Token",
                    type="password",
                    help="Needed for private repos or to avoid API rate limits (60 req/hr without token)",
                    key="github_token_input"
                )
                if token_input:
                    st.session_state.github_token = token_input
            
            # Smart Folder Filters
            with st.expander("🎯 Smart Filters"):
                filter_col1, filter_col2 = st.columns(2)
                with filter_col1:
                    exclude_common = st.checkbox("Exclude common dirs", value=True, help="node_modules, venv, __pycache__, etc.")
                with filter_col2:
                    source_only = st.checkbox("Source files only", value=False, help="Only code files (.py, .js, .ts, etc.)")
                
                ext_filter = st.text_input("Extension filter", placeholder=".py, .js, .ts", help="Comma-separated extensions to include")
            
            # Load Repository button
            if st.button("🔍 Load Repository", type="primary", key="load_repo_btn"):
                if repo_url:
                    parsed = GitHubAPI.parse_github_url(repo_url)
                    if parsed:
                        with st.spinner(f"Loading {parsed['owner']}/{parsed['repo']}..."):
                            token = st.session_state.github_token or None
                            
                            # Get default branch if not specified
                            if parsed['branch'] == 'main':
                                parsed['branch'] = GitHubAPI.fetch_default_branch(
                                    parsed['owner'], parsed['repo'], token
                                )
                            
                            tree, error = GitHubAPI.fetch_repo_tree(
                                parsed['owner'], parsed['repo'], parsed['branch'], token
                            )
                            
                            if tree:
                                # Store raw tree for filtering
                                st.session_state.raw_tree = tree
                                st.session_state.repo_info = parsed
                                
                                # Apply filters
                                filtered_tree = tree
                                if exclude_common:
                                    filtered_tree = apply_tree_filters(
                                        filtered_tree, 
                                        exclude_dirs=FILTER_PRESETS["exclude_common"]["exclude_dirs"]
                                    )
                                if source_only:
                                    filtered_tree = apply_tree_filters(
                                        filtered_tree,
                                        include_extensions=FILTER_PRESETS["source_only"]["include_extensions"]
                                    )
                                if ext_filter:
                                    exts = [e.strip() for e in ext_filter.split(",") if e.strip()]
                                    exts = [e if e.startswith('.') else f'.{e}' for e in exts]
                                    if exts:
                                        filtered_tree = apply_tree_filters(filtered_tree, include_extensions=exts)
                                
                                # Build hierarchical structure for tree select
                                structured = GitHubAPI.build_tree_structure(filtered_tree)
                                nodes = GitHubAPI.get_tree_select_nodes(structured)
                                st.session_state.repo_tree = nodes
                                
                                if error:  # Warning (e.g., truncated)
                                    st.warning(error)
                                else:
                                    st.success(f"Loaded {len(filtered_tree)} items from {parsed['owner']}/{parsed['repo']}")
                            else:
                                st.error(error or "Failed to load repository")
                                st.session_state.repo_tree = None
                                st.session_state.repo_info = None
                    else:
                        st.error("Invalid GitHub URL. Use format: https://github.com/owner/repo")
                else:
                    st.warning("Please enter a repository URL")
            
            # Display tree selector if repo is loaded
            if st.session_state.repo_tree:
                st.markdown("---")
                st.markdown("### 📁 Select Files to Import")
                
                # Tree selector widget
                selection = tree_select(
                    st.session_state.repo_tree,
                    check_model="leaf",  # Only count leaf nodes (files)
                    expanded=[],  # Start collapsed
                    show_expand_all=True
                )
                
                selected_files = selection.get('checked', [])
                
                # Filter to only files (not folders) - folders don't have extensions typically
                # But we stored all paths, so filter by checking if it's in our flat tree
                file_count = len([f for f in selected_files if '.' in f.split('/')[-1]])
                
                st.caption(f"📊 {file_count} file(s) selected")
                
                # Import button
                col1, col2 = st.columns([2, 1])
                with col1:
                    if st.button("📥 Import Selected Files", type="primary", disabled=file_count == 0, key="import_files_btn"):
                        if selected_files and st.session_state.repo_info:
                            info = st.session_state.repo_info
                            
                            # Filter to only actual files (have extensions)
                            file_paths = [f for f in selected_files if '.' in f.split('/')[-1]]
                            
                            if file_paths:
                                progress_bar = st.progress(0, text="Fetching files...")
                                
                                def update_progress(current, total):
                                    progress_bar.progress(current / total, text=f"Fetching {current}/{total}...")
                                
                                fetched_files, errors = GitHubAPI.fetch_multiple_files(
                                    info['owner'], info['repo'], file_paths, info['branch'],
                                    st.session_state.github_token or None,
                                    progress_callback=update_progress,
                                    repo_prefix=info['repo']
                                )
                                
                                progress_bar.empty()
                                
                                # Add fetched files to the upload list
                                added_count = 0
                                for file_obj in fetched_files:
                                    if not any(existing.name == file_obj.name for existing in st.session_state.uploaded_files):
                                        st.session_state.uploaded_files.append(file_obj)
                                        added_count += 1
                                
                                if added_count > 0:
                                    st.success(f"✅ Imported {added_count} file(s)")
                                elif fetched_files:
                                    st.info(f"All {len(fetched_files)} file(s) already in queue")
                                
                                if errors:
                                    with st.expander(f"⚠️ {len(errors)} error(s)"):
                                        for err in errors:
                                            st.warning(err)
                                
                                if added_count > 0:
                                    st.rerun()  # Only rerun if files were added
                
                with col2:
                    if st.button("🗑️ Clear Tree", key="clear_tree_btn"):
                        st.session_state.repo_tree = None
                        st.session_state.repo_info = None
                        st.rerun()

    # 2. File Organization
    if st.session_state.uploaded_files:
        st.markdown("### 🗂️ File Queue")
        
        # Search filter
        file_search = st.text_input("🔍 Search files", placeholder="Filter by filename...", key="file_search_input")
        
        # Filter files based on search
        all_files = st.session_state.uploaded_files
        if file_search:
            display_files = [f for f in all_files if file_search.lower() in f.name.lower()]
        else:
            display_files = all_files
        
        st.caption(f"Showing {len(display_files)} of {len(all_files)} file(s)")
        
        # Display files with remove buttons and preview
        files_to_remove = []
        for i, f in enumerate(display_files):
            with st.container():
                col_name, col_preview, col_btn = st.columns([4, 1, 1])
                with col_name:
                    # Get file size if available
                    try:
                        f.seek(0, 2)
                        size = f.tell()
                        f.seek(0)
                        size_str = format_file_size(size)
                    except (AttributeError, OSError, IOError):
                        size_str = ""
                    st.markdown(f"📄 **{f.name}** {size_str}")
                
                with col_preview:
                    preview_key = f"preview_{i}_{f.name}"
                    if st.button("👁️", key=preview_key, help=f"Preview {f.name}"):
                        st.session_state[f"show_preview_{f.name}"] = not st.session_state.get(f"show_preview_{f.name}", False)
                
                with col_btn:
                    if st.button("❌", key=f"remove_{i}_{f.name}", help=f"Remove {f.name}"):
                        files_to_remove.append(f.name)
                
                # Show preview if toggled
                if st.session_state.get(f"show_preview_{f.name}", False):
                    try:
                        f.seek(0)
                        content = f.read()
                        if isinstance(content, bytes):
                            content = content.decode('utf-8', errors='replace')
                        
                        # Limit preview to first 50 lines
                        lines = content.split('\n')
                        preview_content = '\n'.join(lines[:50])
                        if len(lines) > 50:
                            preview_content += f"\n\n... [{len(lines) - 50} more lines]"
                        
                        # Detect language for syntax highlighting
                        ext = os.path.splitext(f.name)[1].lower()
                        lang_map = {
                            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                            '.html': 'html', '.css': 'css', '.json': 'json',
                            '.md': 'markdown', '.sql': 'sql', '.sh': 'bash'
                        }
                        lang = lang_map.get(ext, 'text')
                        
                        st.code(preview_content, language=lang)
                        f.seek(0)  # Reset for later use
                    except Exception as e:
                        st.error(f"Cannot preview: {str(e)}")
        
        # Process removals
        if files_to_remove:
            st.session_state.uploaded_files = [f for f in st.session_state.uploaded_files if f.name not in files_to_remove]
            st.rerun()
        
        # Reorder with sortables (only if not searching)
        if not file_search and len(display_files) > 1:
            st.markdown("**Drag to reorder:**")
            filenames = [f.name for f in st.session_state.uploaded_files]
            sorted_filenames = sort_items(filenames)
            
            # Sync sort
            reordered_list = []
            for name in sorted_filenames:
                for f in st.session_state.uploaded_files:
                    if f.name == name:
                        reordered_list.append(f)
                        break
            st.session_state.uploaded_files = reordered_list
        elif file_search:
            st.info("💡 Clear search to reorder files")
        
        if st.button("🗑️ Clear All", type="secondary"):
            st.session_state.uploaded_files = []
            st.session_state.file_hashes = {}  # Clear hashes too
            st.rerun()

    st.divider()

    # 3. Merge Settings
    st.markdown("### ⚙️ Configuration")
    with st.form("settings_form"):
        output_format = st.selectbox(
            "Output Format",
            ["TXT", "PDF", "DOCX"],
            index=["TXT", "PDF", "DOCX"].index(st.session_state.settings.get('output_format', 'TXT')),
            help="Select the final document format."
        )
        
        output_filename = st.text_input("Output Filename", value="consolidated")
        
        # Advanced Options
        st.markdown("**Sanitization & Formatting**")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            sanitize_keys = st.checkbox("Strip API Keys", value=st.session_state.settings.get('sanitize_keys', False), help="Removes API keys")
            if sanitize_keys:
                st.caption("⚠️ Caution: Regex-based removal. Verify output.")
        with col_s2:
            remove_comments = st.checkbox("Remove Comments", value=st.session_state.settings.get('remove_comments', False), help="Removes # and // comments")
            if remove_comments:
                st.caption("⚠️ Caution: May remove partial URLs or text.")
            
        submitted = st.form_submit_button("🚀 Merge Documents", type="primary")
        
    # Save settings after form (outside form context)
    if submitted:
        st.session_state.settings['output_format'] = output_format
        st.session_state.settings['sanitize_keys'] = sanitize_keys
        st.session_state.settings['remove_comments'] = remove_comments

with right_col:
    st.subheader("👁️ Live Preview")
    
    if not st.session_state.uploaded_files:
        st.info("Upload files to see a preview of the consolidated structure.")
        st.markdown("""
        <div class="waiting-placeholder">
            📁 Waiting for content...
        </div>
        """, unsafe_allow_html=True)
    else:
        # Generate Preview (Text Lane only for speed)
        preview_text = DocumentProcessor.merge_as_text(
            st.session_state.uploaded_files, 
            sanitize=sanitize_keys if 'sanitize_keys' in locals() else False, 
            remove_comments=remove_comments if 'remove_comments' in locals() else False
        )
        
        # Multi-Model Token Counter
        model_col, info_col = st.columns([2, 3])
        with model_col:
            selected_model = st.selectbox(
                "Model",
                list(MODEL_CONFIGS.keys()),
                index=list(MODEL_CONFIGS.keys()).index(st.session_state.selected_model),
                key="model_selector"
            )
            st.session_state.selected_model = selected_model
        
        # Get token info for selected model
        token_info = DocumentProcessor.get_model_token_info(preview_text, selected_model)
        
        with info_col:
            # Determine color based on percentage
            if token_info["percentage"] < 50:
                color = "#27ae60"  # Green
            elif token_info["percentage"] < 80:
                color = "#f39c12"  # Orange
            else:
                color = "#e74c3c"  # Red
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>{token_info['icon']} Tokens: <b>{token_info['tokens']:,}</b></h4>
                <small>{selected_model} context: {token_info['limit']:,} tokens</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bar for context usage
        st.progress(token_info["percentage"] / 100, text=f"Context Usage: {token_info['percentage']:.1f}%")
        
        # Preview Box
        display_text = preview_text
        if len(display_text) > 5000:
            display_text = display_text[:5000] + "\n\n... [Preview Truncated] ..."
            
        st.code(display_text, language="markdown")

    # --- Result Handling (Outside Form) ---
    if submitted:
        if not st.session_state.uploaded_files:
            st.error("No files to merge!")
        else:
            try:
                with st.spinner("Processing..."):
                     # Call Processor
                    result_data, mime_type = DocumentProcessor.merge_files(
                        st.session_state.uploaded_files, 
                        output_format,
                        sanitize=sanitize_keys,
                        remove_comments=remove_comments
                    )
                    
                    st.toast("Merge Successful!", icon="✅")
                    
                    # Download Button Logic
                    file_ext = output_format.lower()
                    full_filename = f"{output_filename}.{file_ext}"
                    
                    if output_format == "TXT" and isinstance(result_data, str):
                        data_to_download = result_data.encode('utf-8')
                        result_preview = result_data
                    else:
                        data_to_download = result_data.getvalue()
                        result_preview = None

                    # Use a specialized container for the download to make it pop
                    st.balloons()
                    st.download_button(
                        label=f"📥 Download {full_filename}",
                        data=data_to_download,
                        file_name=full_filename,
                        mime=mime_type,
                        type="primary",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
