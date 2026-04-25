import streamlit as st

def render_uploader():
    """
    Renders an enterprise-grade file ingestion panel.
    Handles the staging of PCB design files and associated metadata 
    required for high-precision physics and compliance validation.
    """
    st.info("🚀 **Get Started:** Upload your PCB design files for multi-agentic AI verification.")
    
    # Use a bordered container for a professional "Cyber-Industrial" look
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📥 Project Ingestion")
            uploaded_file = st.file_uploader(
                "Drag & Drop Gerber (ZIP) or Board Photos (PNG/JPG)", 
                type=['zip', 'png', 'jpg', 'jpeg'],
                help="We support RS-274X Gerber formats and high-resolution industrial AOI imagery."
            )
            
        with col2:
            st.markdown("### 📐 Board Specs")
            # These specs are critical for the Physics Agent calculations
            st.session_state.layer_count = st.selectbox(
                "Layer Count", 
                [2, 4, 6, 8, 10, 12],
                index=1
            )
            st.session_state.copper_weight = st.selectbox(
                "Copper Weight", 
                ["0.5 oz", "1.0 oz", "2.0 oz", "3.0 oz"],
                index=1,
                help="Determines current capacity thresholds (IPC-2152)."
            )
            st.session_state.board_material = st.selectbox(
                "Substrate Material", 
                ["FR-4", "High-Tg FR-4", "Rogers 4350B", "Polyimide"],
                help="Impacts dielectric constant and thermal dissipation rules."
            )

    # Execution logic
    if uploaded_file:
        st.success(f"✅ Document '{uploaded_file.name}' staged for analysis.")
        
        # Action button to trigger the LangGraph orchestration
        if st.button("🚀 EXECUTE AGENTIC REVIEW", use_container_width=True, type="primary"):
            # Update session state for the app.py main loop
            st.session_state.pcb_file = uploaded_file
            st.session_state.analysis_state = 'PROCESSING'
            
            # Prepare metadata for the Orchestrator
            st.session_state.pcb_metadata = {
                "filename": uploaded_file.name,
                "layers": st.session_state.layer_count,
                "copper_weight": float(st.session_state.copper_weight.split()[0]),
                "material": st.session_state.board_material,
                "safety_class": st.session_state.get('safety_class', 'Class 3'),
                "provider": st.session_state.get('ai_provider', 'groq')
            }
            
            st.rerun()
    else:
        # Placeholder view when no file is present
        st.caption("Waiting for project files... Support for ODB++, RS-274X, and IPC-2581 coming soon.")
