import streamlit as st
import pandas as pd

def render_workspace():
    """
    Renders the Digital Twin workspace.
    Provides interactive visualization of the PCB layout, thermal simulations, 
    and detailed technical reporting based on agent results.
    """
    st.subheader("🛠️ PCB Digital Twin")
    
    # Retrieve data from session state
    results = st.session_state.get('agent_results')
    metadata = st.session_state.get('pcb_metadata', {})
    
    # Define Tabs for different engineering views
    tabs = st.tabs(["🔍 Visual Inspection", "🌡️ Thermal Mapping", "📊 DRC & IPC Reports", "📁 Layer Explorer"])
    
    # --- TAB 1: VISUAL INSPECTION ---
    with tabs[0]:
        col_img, col_info = st.columns([3, 1])
        
        with col_img:
            # Main PCB Visualization (Simulated Overlay)
            st.image(
                "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200", 
                caption=f"Project: {metadata.get('filename', 'Unknown_Design.zip')} | Layer: Top Copper",
                use_container_width=True
            )
        
        with col_info:
            st.markdown("### 👁️ Vision Insights")
            if results and results.get('vision_findings'):
                for finding in results.get('vision_findings'):
                    with st.container(border=True):
                        st.caption(f"ID: {finding.get('id', 'N/A')}")
                        st.markdown(f"**{finding.get('class', 'Defect').replace('_', ' ').title()}**")
                        st.write(f"Net: `{finding.get('net_id', 'N/A')}`")
            else:
                st.write("Upload a design to see visual analysis.")

    # --- TAB 2: THERMAL MAPPING ---
    with tabs[1]:
        st.markdown("### 🌡️ Thermal Distribution Simulation")
        st.caption("Based on IPC-2152 Current Capacity & Copper Weight Analysis")
        
        # Simulated Thermal Heatmap based on Copper Weight metadata
        cu_weight = metadata.get('copper_weight', 1.0)
        temp_delta = "15°C" if cu_weight < 1.0 else "8°C"
        
        c1, c2 = st.columns([2, 1])
        with c1:
            # Placeholder for a generated heatmap image
            st.image(
                "https://images.unsplash.com/photo-1610444391913-90977286395b?w=800", 
                caption="Simulated IR Heatmap: Peak current density on VCC_3V3",
                use_container_width=True
            )
        with c2:
            st.metric("Peak Temp Rise", temp_delta, delta="Above Ambient")
            st.metric("Current Density", "1.4A/mm²", delta="Limit 2.0A", delta_color="normal")
            st.warning("**Thermal Agent:** High current density on Net_VCC may require wider traces or thermal vias.")

    # --- TAB 3: DRC & IPC REPORTS ---
    with tabs[2]:
        st.markdown("### 📜 Automated Design Rule Check (DRC)")
        
        if results and results.get('physics_violations'):
            # Convert list of dicts to DataFrame for clear reporting
            df = pd.DataFrame(results.get('physics_violations'))
            if not df.empty:
                # Clean up display columns
                display_cols = ['class', 'net_id', 'layer', 'severity']
                existing_cols = [c for c in display_cols if c in df.columns]
                st.table(df[existing_cols])
                
                if st.button("Download IPC Compliance CSV"):
                    st.toast("Exporting technical report...")
            else:
                st.success("No DRC violations detected.")
        else:
            st.info("Run analysis to generate the compliance report.")

    # --- TAB 4: LAYER EXPLORER ---
    with tabs[3]:
        st.markdown("### 📁 Multilayer Stackup Explorer")
        layers = metadata.get('layers', 4)
        
        # Interactive slider to 'peel' through layers
        selected_layer = st.select_slider(
            "View Depth",
            options=[f"Layer {i+1}" for i in range(layers)],
            value="Layer 1"
        )
        
        # Mock stackup visualization
        st.write(f"Showing stackup data for **{selected_layer}**")
        stack_cols = st.columns(layers)
        for i, col in enumerate(stack_cols):
            with col:
                color = "#4FB3FF" if f"Layer {i+1}" == selected_layer else "#30363D"
                st.markdown(f"""
                    <div style="background-color: {color}; height: 40px; border-radius: 4px; border: 1px solid white; display: flex; align-items: center; justify-content: center; font-size: 10px;">
                        L{i+1}
                    </div>
                """, unsafe_content_safe=True)
        
        st.divider()
        st.markdown(f"""
            <div class="insight-box">
                <strong>Lead Architect Orchestrator:</strong> Viewing cross-section of {selected_layer}. 
                Ensure dielectric spacing between L{layers//2} and L{layers//2 + 1} complies with impedance requirements for {metadata.get('material', 'FR-4')}.
            </div>
        """, unsafe_content_safe=True)

def render_empty_workspace():
    """Fallback for when no data is loaded."""
    st.image("https://images.unsplash.com/photo-1558494949-ef010cbdcc4b?w=800", use_container_width=True)
    st.info("Awaiting hardware layout ingestion...")
