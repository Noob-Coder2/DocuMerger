import streamlit as st
import time
from processor import DocumentProcessor, MODEL_CONFIGS
from utils import format_file_size

def render_preview(submitted, output_format, output_filename, sanitize_keys, remove_comments):
    """Renders the Live Preview section."""
    st.subheader("👁️ Live Preview")
    
    if not st.session_state.get("uploaded_files"):
        st.info("Upload files to see a preview.")

    else:
        # Generate Preview (Text Lane only for speed)
        preview_text = DocumentProcessor.merge_as_text(
            st.session_state.uploaded_files, 
            sanitize=sanitize_keys, 
            remove_comments=remove_comments
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
            # Color & Risk Badge
            percent = token_info["percentage"]
            if percent < 40:
                color = "#27ae60"
                risk_badge = "🟢 Safe"
            elif percent < 80:
                color = "#f39c12"
                risk_badge = "🟠 High Usage"
            else:
                color = "#e74c3c"
                risk_badge = "🔴 Risk (Truncation)"
            
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {color}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b>{token_info['icon']} {selected_model}</b>
                    <span style="background: {color}20; color: {color}; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold;">{risk_badge}</span>
                </div>
                <h3 style="margin: 5px 0;">{token_info['tokens']:,} <span style="font-size: 0.6em; font-weight: 400; opacity: 0.7;">tokens</span></h3>
                <small style="opacity: 0.8;">Limit: {token_info['limit']:,}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bar for context usage
        st.progress(token_info["percentage"] / 100, text=f"Context Usage: {token_info['percentage']:.1f}%")
        
        # Consolated Preview
        total_size = len(preview_text.encode('utf-8'))
        size_label = format_file_size(total_size)
        
        with st.expander(f"📄 Consolidated Preview ({size_label})", expanded=True):
             display_text = preview_text
             if len(display_text) > 10000:
                 display_text = display_text[:10000] + "\n\n... [Preview Truncated due to size] ..."
                 st.warning(f"Preview truncated for display. Total size: {size_label}")
             
             st.code(display_text, language="markdown")

    # --- Result Handling (Outside Form) ---
    if submitted:
        if not st.session_state.uploaded_files:
            st.error("No files to merge!")
        else:
            try:
                progress_container = st.empty()
                with progress_container.container():
                    st.write("Initializing...")
                    progress = st.progress(0)
                
                # 1. Validation
                progress.progress(20, text="Validating inputs...")
                time.sleep(0.3)
                
                # 2. Processing
                progress.progress(50, text="Merging documents...")
                
                # Call Processor
                result_data, mime_type = DocumentProcessor.merge_files(
                    st.session_state.uploaded_files, 
                    output_format,
                    sanitize=sanitize_keys,
                    remove_comments=remove_comments
                )
                
                # 3. Finalizing
                progress.progress(90, text="Finalizing output...")
                time.sleep(0.2)
                
                progress.progress(100, text="Done!")
                time.sleep(0.5)
                progress_container.empty()
                
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
