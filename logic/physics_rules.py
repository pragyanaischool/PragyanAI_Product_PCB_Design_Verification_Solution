import math
from typing import List, Dict, Any

class PCBPhysicsRules:
    """
    Deterministic Physics & IPC Compliance Engine.
    Used to validate AI predictions against industry standards (IPC-2221/2152).
    """

    @staticmethod
    def check_clearance(width_mil: float, voltage: float, is_internal: bool = False) -> Dict[str, Any]:
        """
        Validates electrical clearance based on IPC-2221B Table 6-1.
        
        Args:
            width_mil: The measured clearance between conductors.
            voltage: The peak voltage between conductors.
            is_internal: Whether the conductors are on an internal layer.
        """
        # Simplified IPC-2221 lookup for uncoated conductors
        if voltage < 15:
            required = 4.0 if not is_internal else 2.0
        elif voltage < 30:
            required = 4.0
        elif voltage < 50:
            required = 24.0
        else:
            # High voltage creepage/clearance scaling
            required = 40.0 + (voltage - 50) * 0.2

        is_valid = width_mil >= required
        return {
            "is_valid": is_valid,
            "required_mil": required,
            "actual_mil": width_mil,
            "violation_delta": max(0, required - width_mil),
            "standard_ref": "IPC-2221B Table 6-1"
        }

    @staticmethod
    def calculate_current_capacity(width_mil: float, temp_rise: float = 10.0, copper_oz: float = 1.0, is_internal: bool = False) -> float:
        """
        Estimates max current capacity (Amps) using IPC-2152 simplified curve fitting.
        Formula approximation: I = k * (dT^b) * (A^c)
        """
        # Cross-sectional area in sq mils (1 oz copper = ~1.37 mil thickness)
        thickness = copper_oz * 1.37
        area = width_mil * thickness
        
        # IPC coefficients for layers
        if is_internal:
            # Internal layers dissipate heat less effectively
            k, b, c = 0.024, 0.44, 0.725
        else:
            # External layers
            k, b, c = 0.048, 0.44, 0.725
        
        current = k * (temp_rise**b) * (area**c)
        return round(current, 3)

    def validate_ai_findings(self, detections: List[Dict[str, Any]], board_specs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filters and augments AI detections with hard physics validation.
        
        Args:
            detections: Raw detections from the ViT engine.
            board_specs: Dictionary containing board parameters like max_voltage, copper_weight.
        """
        validated_findings = []
        max_v = board_specs.get('max_voltage', 5.0)
        cu_weight = board_specs.get('copper_weight', 1.0)
        
        for det in detections:
            # Logic to enhance specific AI classes with physics data
            if det['class'] == 'clearance_violation':
                # In production, 'width_mil' would be extracted from the bbox or vision engine
                measured_clearance = 6.0 
                is_internal = "Inner" in det.get('layer', '')
                
                phys_check = self.check_clearance(
                    width_mil=measured_clearance,
                    voltage=max_v,
                    is_internal=is_internal
                )
                
                det['physics_confirmed'] = not phys_check['is_valid']
                det['compliance_data'] = phys_check
                det['severity'] = "HIGH" if not phys_check['is_valid'] else "LOW"
            
            elif det['class'] == 'trace_necking':
                # Check if necking causes the trace to exceed its current limit
                current_limit = self.calculate_current_capacity(
                    width_mil=3.0, # Necked width
                    copper_oz=cu_weight
                )
                det['thermal_current_limit_amps'] = current_limit
                det['description'] = f"Necking reduces current limit to {current_limit}A."

            validated_findings.append(det)
            
        return validated_findings

def get_physics_engine():
    """Singleton-style accessor for the Physics Engine."""
    return PCBPhysicsRules()
