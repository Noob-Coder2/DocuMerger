import streamlit as st
import os
from streamlit_sortables import sort_items
from utils import format_file_size

def render_file_queue():
    """Renders the file queue with expanders and reordering logic."""
    st.subheader("2. File Organization")
    
    all_files = st.session_state.uploaded_files
    
    if not all_files:
        st.info("Files you upload will appear here.")
    else:
        # File Search
        col_search, _ = st.columns([2, 1])
        with col_search:
            file_search = st.text_input("🔍 Filter files", placeholder="Search by name...", key="file_queue_search")
            st.session_state.file_search = file_search
        
        # Filter files if search is active
        if file_search:
            display_files = [f for f in all_files if file_search.lower() in f.name.lower()]
        else:
            display_files = all_files
        
        st.caption(f"Showing {len(display_files)} of {len(all_files)} file(s)")
        
        # Display files with expanders
        files_to_remove = []
        for i, f in enumerate(display_files):
            # Determine Icon & Type logic
            ext = os.path.splitext(f.name)[1].lower()
            icon_map = {
                '.py': '🐍', '.js': '📜', '.ts': '📜', '.html': '🌐', '.css': '🎨', 
                '.json': '📦', '.md': '📝', '.txt': '📄', '.sql': '🗄️',
                '.pdf': '📕', '.docx': '📘', '.sh': '💻', '.yml': '⚙️', '.yaml': '⚙️'
            }
            icon = icon_map.get(ext, '📄')
            
            # Get size
            try:
                f.seek(0, 2)
                size = f.tell()
                f.seek(0)
                size_str = format_file_size(size)
            except:
                size_str = ""
            
            # Use expander for item
            with st.expander(f"{icon} {f.name}   `{size_str}`"):
                # Preview logic
                try:
                    f.seek(0)
                    content = f.read()
                    if isinstance(content, bytes):
                        try:
                            content_str = content.decode('utf-8')
                        except UnicodeDecodeError:
                             content_str = content.decode('latin-1', errors='replace')
                    else:
                        content_str = content
                    
                    # Limit preview
                    lines = content_str.split('\n')
                    preview_lines = lines[:20] 
                    preview_content = '\n'.join(preview_lines)
                    if len(lines) > 20:
                        preview_content += f"\n... [{len(lines) - 20} more lines]"
                        
                    # Language map
                    lang_map = {
                        '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                        '.html': 'html', '.css': 'css', '.json': 'json',
                        '.md': 'markdown', '.sql': 'sql', '.sh': 'bash'
                    }
                    lang = lang_map.get(ext, 'text')
                    
                    st.code(preview_content, language=lang)
                    f.seek(0)
                except Exception as e:
                    st.warning(f"Preview unavailable: {str(e)}")
                
                # Remove button
                col1, col2 = st.columns([4, 1])
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_{i}_{f.name}_{hash(f.name)}", type="secondary"):
                        files_to_remove.append(f.name)
        
        # Process removals
        if files_to_remove:
            st.session_state.uploaded_files = [f for f in st.session_state.uploaded_files if f.name not in files_to_remove]
            st.rerun()
        
        # Reorder Section
        if not file_search and len(display_files) > 1:
            with st.expander("🔁 Reorder Files", expanded=False):
                st.caption("Drag items to change merge order")
                filenames = [f.name for f in st.session_state.uploaded_files]
                sorted_filenames = sort_items(filenames)
                
                # Sync sort
                if sorted_filenames != filenames:
                    reordered_list = []
                    for name in sorted_filenames:
                        for f in st.session_state.uploaded_files:
                            if f.name == name:
                                reordered_list.append(f)
                                break
                    st.session_state.uploaded_files = reordered_list
                    st.rerun()
        elif file_search:
             st.caption("🔒 Reordering disabled while searching")
        
        if st.button("🗑️ Clear All", type="secondary"):
            st.session_state.uploaded_files = []
            st.rerun()
