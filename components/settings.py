import streamlit as st

def render_settings():
    """Renders the settings and configuration section."""
    # 3. Merge Settings
    st.markdown("### ⚙️ Configuration")
    
    # --- Presets ---
    st.caption("⚡ Quick Presets")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    
    def set_preset(fmt, sanitize, comments):
        st.session_state.settings.update({
            'output_format': fmt,
            'sanitize_keys': sanitize,
            'remove_comments': comments
        })
        st.rerun()

    if col_p1.button("✨ Standard", use_container_width=True, help="Text output, minimal changes"):
        set_preset("TXT", False, False)
    
    if col_p2.button("🛡️ Secure", use_container_width=True, help="Text output, strips API keys"):
        set_preset("TXT", True, False)
        
    if col_p3.button("🧹 Clean", use_container_width=True, help="Text output, removes comments"):
        set_preset("TXT", False, True)
        
    if col_p4.button("📄 PDF", use_container_width=True, help="PDF output"):
        set_preset("PDF", False, False)

    with st.form("settings_form"):
        with st.expander("🛠️ Output Settings", expanded=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                output_format = st.selectbox(
                    "Output Format",
                    ["TXT", "PDF", "DOCX"],
                    index=["TXT", "PDF", "DOCX"].index(st.session_state.settings.get('output_format', 'TXT')),
                    help="Select the final document format."
                )
            with col_f2:
                output_filename = st.text_input("Output Filename", value="consolidated")
            
            st.divider()
            
            # Advanced Options
            st.markdown("**Sanitization & Formatting**")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                sanitize_keys = st.checkbox("Strip API Keys", value=st.session_state.settings.get('sanitize_keys', False), help="Removes API keys")
                if sanitize_keys:
                    st.caption("⚠️ Caution: Regex-based removal.")
            with col_s2:
                remove_comments = st.checkbox("Remove Comments", value=st.session_state.settings.get('remove_comments', False), help="Removes # and // comments")
                if remove_comments:
                    st.caption("⚠️ Caution: May remove partial URLs.")
            
        submitted = st.form_submit_button("🚀 Merge Documents", type="primary")
        
    # Save settings after form (outside form context)
    if submitted:
        st.session_state.settings['output_format'] = output_format
        st.session_state.settings['sanitize_keys'] = sanitize_keys
        st.session_state.settings['remove_comments'] = remove_comments
        
    return submitted, output_format, output_filename, sanitize_keys, remove_comments
