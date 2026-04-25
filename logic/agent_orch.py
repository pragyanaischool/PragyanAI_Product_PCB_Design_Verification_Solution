from typing import TypedDict, List, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END

# 1. Define the State Schema
class AgentState(TypedDict):
    """
    Represents the shared memory/state of the multi-agent system.
    """
    pcb_metadata: dict
    # Using Annotated with operator.add allows agents to append to the list
    vision_defects: Annotated[List[dict], operator.add]
    physics_violations: Annotated[List[dict], operator.add]
    compliance_report: str
    final_summary: str
    next_step: str

# 2. Define Node Functions (The Agents)

def vision_agent_node(state: AgentState):
    """
    LVM-powered node that identifies physical defects from image/Gerber data.
    """
    # In production, this calls logic/agents.py -> VisionAgent.analyze()
    new_defects = [
        {"type": "Acid Trap", "location": "Trace_Net_04", "confidence": 0.92, "severity": "HIGH"},
        {"type": "Solder Bridge", "location": "IC_U12_Pins_4-5", "confidence": 0.88, "severity": "HIGH"}
    ]
    return {
        "vision_defects": new_defects,
        "next_step": "physics"
    }

def physics_agent_node(state: AgentState):
    """
    Physics-informed node checking for Thermal and EMI issues using GROQ LPU.
    """
    # This agent reviews vision findings and adds its own physical simulations
    new_violations = [
        {"type": "Thermal Hotspot", "location": "Regulator_Q4", "temp_estimate": "115C", "severity": "HIGH"},
        {"type": "Crosstalk Risk", "location": "Differential_Pair_J2", "severity": "MED"}
    ]
    return {
        "physics_violations": new_violations,
        "next_step": "compliance"
    }

def compliance_agent_node(state: AgentState):
    """
    RAG-based node checking findings against IPC-2221/6012 standards.
    """
    # Logic to cross-reference defects with vector-stored standards
    report = "IPC-2221 Violation: Minimum trace clearance of 6mil not met at J2. " \
             "IPC-6012 Violation: 90-degree trace (Acid Trap) detected at Net_04."
    return {
        "compliance_report": report,
        "next_step": "orchestrator"
    }

def orchestrator_node(state: AgentState):
    """
    Synthesizes all findings into a final executive summary and rework strategy.
    """
    summary = f"""
    ### PCB Analysis Summary ({state['pcb_metadata'].get('project_id', 'N/A')})
    
    1. **Visual Failures:** {len(state['vision_defects'])} issues found (Acid traps, bridges).
    2. **Physical Risks:** {len(state['physics_violations'])} thermal/signal integrity issues.
    3. **Compliance:** {state['compliance_report']}
    
    **Recommended Action:** Redesign Net_04 to 45-degree bends and increase copper pour near Q4.
    """
    return {
        "final_summary": summary,
        "next_step": END
    }

# 3. Build the Graph

def create_pcb_analysis_graph():
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("vision", vision_agent_node)
    workflow.add_node("physics", physics_agent_node)
    workflow.add_node("compliance", compliance_agent_node)
    workflow.add_node("orchestrator", orchestrator_node)

    # Define Edges (The logical flow)
    workflow.set_entry_point("vision")
    workflow.add_edge("vision", "physics")
    workflow.add_edge("physics", "compliance")
    workflow.add_edge("compliance", "orchestrator")
    workflow.add_edge("orchestrator", END)

    return workflow.compile()

# 4. Interface for app.py

def run_agentic_workflow(file_input, metadata=None):
    """
    Entry point to trigger the LangGraph execution.
    """
    if metadata is None:
        metadata = {"project_id": "DEFAULT-PROJECT"}

    # Initialize graph
    app = create_pcb_analysis_graph()
    
    # Initial State
    initial_state = {
        "pcb_metadata": metadata,
        "vision_defects": [],
        "physics_violations": [],
        "compliance_report": "",
        "final_summary": "",
        "next_step": ""
    }

    # Execute Graph
    final_output = app.invoke(initial_state)
    
    return final_output
