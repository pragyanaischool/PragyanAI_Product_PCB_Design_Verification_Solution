import json
import re
from typing import List, Dict, Any
from logic.llm_config import (
    get_visual_analysis, 
    get_groq_chat_completion, 
    get_visual_analysis
)

class PCBVisionAgent:
    """
    The Vision Agent uses Large Vision Models (LVMs) to analyze PCB layouts.
    It identifies physical manufacturing defects like acid traps and solder bridges.
    """
    def __init__(self, provider: str = "groq"):
        self.provider = provider

    def _extract_json(self, text: str) -> List[Dict[str, Any]]:
        """Helper to extract JSON from LLM responses that might contain markdown blocks."""
        try:
            # Look for JSON array pattern in the response
            match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            # Fallback if no array brackets found, try to find any curly brace structure
            match = re.search(r'{.*}', text, re.DOTALL)
            if match:
                return [json.loads(match.group())]
            return []
        except Exception:
            return []

    def analyze_layout(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Scans the PCB image for physical defects.
        """
        prompt = """
        ACT AS: Senior PCB Optical Inspection (AOI) Engineer.
        TASK: Analyze the provided PCB layout image for defects.
        
        DETECT THE FOLLOWING:
        1. Acid Traps: Traces with 90-degree or acute angle bends.
        2. Solder Bridges: Unintended copper connections between pads/traces.
        3. Trace Necking: Areas where trace width significantly narrows.
        4. Clearance Issues: Traces too close to vias or other nets.

        FORMAT: Return a JSON array of objects. 
        Example: [{"type": "Acid Trap", "location": "Net_05", "severity": "HIGH", "description": "90-degree bend detected"}]
        """
        
        response = get_visual_analysis(image_bytes, prompt, provider=self.provider)
        defects = self._extract_json(response)
        
        # Ensure we return a list even if empty
        return defects if isinstance(defects, list) else []

class PCBPhysicsAgent:
    """
    The Physics Agent analyzes signal and power integrity, 
    thermal hotspots, and electromagnetic interference (EMI) risks.
    """
    def __init__(self, provider: str = "groq"):
        self.provider = provider

    def analyze_physics(self, metadata: dict, vision_findings: list) -> List[Dict[str, Any]]:
        """
        Reasons about thermal and signal integrity based on metadata and vision findings.
        """
        prompt = f"""
        ACT AS: Signal Integrity & Thermal Engineer.
        CONTEXT:
        - Board Stackup: {metadata.get('layers', 'Unknown')} layers
        - Material: {metadata.get('material', 'FR-4')}
        - Vision Defects Found: {json.dumps(vision_findings)}

        TASK:
        Identify potential Physics Violations (Thermal hotspots, Crosstalk, Impedance).
        Return a JSON array of objects.
        Example: [{"type": "Thermal Risk", "location": "U12 Regulator", "severity": "HIGH", "impact": "Overheating"}]
        """
        
        response = get_groq_chat_completion(prompt, system_role="PHYSICS_AGENT")
        # Reuse extraction logic or similar for physics
        try:
            match = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
            return json.loads(match.group()) if match else []
        except:
            return []

class ComplianceAgent:
    """
    The Compliance Agent validates findings against industry standards (IPC-2221, IPC-6012).
    """
    def check_compliance(self, findings: list, standard: str = "IPC-A-610 Class 3") -> str:
        """
        Cross-references findings with a knowledge base of standards.
        """
        prompt = f"""
        ACT AS: IPC Compliance Auditor.
        FINDINGS TO AUDIT: {json.dumps(findings)}
        STANDARD: {standard}

        TASK: 
        Provide a concise audit report. List specific violations and 
        assign a 'GO/NO-GO' status for manufacturing.
        """
        
        return get_groq_chat_completion(prompt, system_role="ORCHESTRATOR")

class ReworkAgent:
    """
    Agent focused on generating physical fix instructions for detected defects.
    """
    def generate_fix(self, defect: dict) -> str:
        prompt = f"""
        ACT AS: Senior PCB Rework Specialist.
        DEFECT: {json.dumps(defect)}

        TASK:
        Provide detailed, step-by-step rework instructions to fix this issue 
        without a full board re-spin if possible. Reference IPC-7711/7721 tools.
        """
        return get_groq_chat_completion(prompt, system_role="REWORK_AGENT")
