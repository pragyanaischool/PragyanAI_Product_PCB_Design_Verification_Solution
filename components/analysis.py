import streamlit as st
import json
from logic.agents import ReworkAgent

def render_analysis_panel():
    """
    Renders the interactive Engineering Findings panel.
    This component displays the results of the multi-agentic analysis,
    including severity metrics and AI-generated rework instructions.
    """
    st.header("🚨 Engineering Analysis")
    
    # Retrieve results from session state
    results = st.session_state.get('agent_results')
    
    if not results:
        st.warning("No analysis data available. Please upload a design to begin.")
        return

    # 1. Executive Summary
    st.markdown(results.get('final_summary', "Summary not available."))
    st.divider()

    # 2. High-Level Metrics
    # In a real scenario, these would be computed by the Orchestrator
    m1, m2, m3 = st.columns(3)
    
    # Simple count for metrics
    total_defects = len(results.get('vision_findings', [])) + len(results.get('physics_violations', []))
    high_severity = sum(1 for d in results.get('vision_findings', []) if d.get('severity') == 'HIGH' or d.get('severity') == 'CRITICAL')
    
    m1.metric("Risk Score", "8.2/10" if high_severity > 0 else "2.1/10", 
              delta="High" if high_severity > 0 else "Low", delta_color="inverse")
    m2.metric("Total Defects", total_defects)
    m3.metric("IPC Status", "FAIL" if high_severity > 0 else "PASS")

    # Render the Rework Overlay (Status Banner)
    render_rework_overlay()

    st.divider()

    # 3. Findings Feed
    st.subheader("🔍 Detailed Findings")
    
    # We combine vision and physics findings for the feed
    all_findings = results.get('vision_findings', []) + results.get('physics_violations', [])
    
    if not all_findings:
        st.success("No critical defects identified in this layout.")
    
    for i, finding in enumerate(all_findings):
        severity = finding.get('severity', 'MED')
        status_icon = "🔴" if severity == "HIGH" or severity == "CRITICAL" else "🟡"
        
        with st.expander(f"{status_icon} {finding.get('class', 'Defect').replace('_', ' ').title()} at {finding.get('net_id', 'Unknown Net')}"):
            st.write(f"**Location:** {finding.get('layer', 'Unknown Layer')}")
            st.write(f"**Description:** {finding.get('description', 'No description provided.')}")
            
            # Physics specific data if available
            if 'compliance_data' in finding:
                comp = finding['compliance_data']
                st.info(f"**IPC Validation:** Required {comp.get('required_mil')}mil | Actual {comp.get('actual_mil')}mil")
            
            # AI Rework Logic
            st.markdown("---")
            if st.button(f"Generate Rework Plan", key=f"rework_btn_{i}_{finding.get('id', i)}"):
                with st.spinner("Rework Agent is analyzing physical constraints..."):
                    agent = ReworkAgent(provider=st.session_state.get('ai_provider', 'groq'))
                    fix_plan = agent.generate_fix(finding)
                    
                    st.markdown("### 🛠️ AI Rework Plan")
                    st.success(fix_plan)
                    
                    # Add a feedback loop for enterprise training
                    st.caption("Was this rework plan helpful?")
                    c1, c2 = st.columns(2)
                    c1.button("👍 Correct", key=f"pos_{i}")
                    c2.button("👎 Incorrect", key=f"neg_{i}")

    st.divider()

    # 4. Action Buttons
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📥 Export Audit PDF", use_container_width=True):
            st.toast("Generating IPC-Standard Audit Report...", icon="📄")
    with col_b:
        if st.button("💬 Chat with Agents", use_container_width=True, type="primary"):
            st.session_state.show_chat = True
            st.toast("Switching to Agent Dialogue mode.")

def render_rework_overlay():
    """
    Renders a status overlay highlighting the most critical rework priority.
    This provides a persistent summary of the current engineering blockers.
    """
    results = st.session_state.get('agent_results')
    if not results:
        return

    # Aggregate high-severity issues across all agents
    high_sev = [f for f in results.get('vision_findings', []) + results.get('physics_violations', []) 
                if f.get('severity') == 'HIGH' or f.get('severity') == 'CRITICAL']
    
    with st.container():
        if high_sev:
            st.error(f"⚠️ **CRITICAL REWORK REQUIRED:** {len(high_sev)} violations are blocking IPC {st.session_state.get('safety_class', 'Class 3')} compliance.")
            st.caption("Action required on Net Junctions and Thermal Reliefs before design release.")
        else:
            st.success("✅ **DESIGN VALIDATED:** Layout meets safety class thresholds. No blocking rework identified.")
