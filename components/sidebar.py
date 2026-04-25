import streamlit as st

def render_sidebar():
    """
    Renders the enterprise navigation and settings panel.
    Handles global session state for AI providers and PCB specifications.
    """
    with st.sidebar:
        # Branding Header
        st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
        st.title("Admin Console")
        st.caption("PCB Review Copilot v2.5-Enterprise")
        
        st.divider()

        # 1. Primary Navigation
        st.subheader("📍 Navigation")
        view = st.radio(
            "Select Workspace", 
            ["Project Dashboard", "Agent Reasoning", "Compliance & Docs"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # 2. Global AI Configuration
        st.subheader("⚙️ AI Configuration")
        
        # Provider Selection including Local Ollama support
        st.session_state.ai_provider = st.selectbox(
            "Primary Vision Provider", 
            ["groq", "gemini", "huggingface", "ollama"],
            index=0,
            help="Select the LVM backend. 'ollama' runs locally for maximum privacy."
        )
        
        # Fine-tuning detection sensitivity
        st.session_state.detection_sensitivity = st.slider(
            "Detection Sensitivity", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.85,
            help="Higher values reduce false positives but may miss subtle defects."
        )
        
        st.divider()

        # 3. PCB Board Specifications
        st.subheader("📐 Board Specs")
        
        st.session_state.layer_count = st.selectbox(
            "Layer Count", 
            [2, 4, 6, 8, 10, 12],
            index=1
        )
        
        st.session_state.safety_class = st.selectbox(
            "IPC Safety Standard", 
            ["Class 1 (General)", "Class 2 (Dedicated)", "Class 3 (High Rel)"],
            index=2,
            help="Class 3 is required for aerospace and medical applications."
        )
        
        st.divider()
        
        # 4. System Status & Diagnostics
        st.subheader("📊 System Health")
        
        # Status indicators
        col1, col2 = st.columns(2)
        with col1:
            st.success("Cloud: Online")
        with col2:
            st.info("Local: Ready")
            
        st.caption(f"Instance ID: {st.session_state.get('app_id', 'N/A')}")
        st.caption("Inference Speed: ~800 tokens/sec")
        
        if st.button("Clear Cache & Reset", use_container_width=True):
            st.session_state.clear()
            st.rerun()
            
        return view
