import streamlit as st
import io
from utils import validate_filename, sanitize_filename, compute_file_hash, fetch_from_github
from github_api import GitHubAPI, FILTER_PRESETS, apply_tree_filters

def render_sidebar():
    """Renders the sidebar (Control Panel) with import tabs."""
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
                        st.toast(f"Added: {paste_filename}", icon="✅")
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
                                st.toast(f"Added {added_count} file(s) from Gist", icon="✅")
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
                            st.toast(f"Added: {file_obj.name}", icon="✅")
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
