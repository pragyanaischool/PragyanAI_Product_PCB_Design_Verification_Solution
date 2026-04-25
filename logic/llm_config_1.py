import json
from logic.llm_config import get_visual_analysis, get_groq_chat_completion

class PCBVisionAgent:
    """
    Leverages LVMs to perform Optical Inspection reasoning.
    """
    def __init__(self, provider="groq"):
        self.provider = provider

    def scan_for_defects(self, image_bytes: bytes):
        prompt = """
        Perform a comprehensive scan of this PCB layer. 
        Identify specific manufacturing defects:
        - Acid Traps (90-degree trace bends)
        - Solder Bridges (short circuits)
        - Trace Necking (width violations)
        - Missing Thermal Reliefs
        
        Return results as a JSON list of objects: 
        [{"type": str, "location": str, "severity": "HIGH"|"MED"|"LOW", "description": str}]
        """
        response = get_visual_analysis(image_bytes, prompt, provider=self.provider)
        try:
            # Attempt to parse JSON from the LLM response
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1
            return json.loads(response[start_idx:end_idx])
        except:
            return []

class PCBPhysicsAgent:
    """
    Analyzes signal integrity and thermal risks.
    """
    def check_thermal_integrity(self, stackup_info: dict):
        prompt = f"""
        Analyze the following PCB stackup for thermal hotspots:
        {json.dumps(stackup_info)}
        
        Predict junction temperatures and identify components at risk of overheating.
        """
        return get_groq_chat_completion(prompt, system_role="PHYSICS_AGENT")

class ComplianceAgent:
    """
    RAG-based agent for IPC standard validation.
    """
    def validate_ipc_6012(self, findings: list):
        prompt = f"Cross-reference these findings with IPC-6012 Class 3 standards: {json.dumps(findings)}"
        return get_groq_chat_completion(prompt, system_role="ORCHESTRATOR")
