import streamlit as st
import base64
import requests
import json
from typing import Optional, Dict, Any, List

# =================================================================
# 1. API CONFIGURATIONS & SECRETS
# =================================================================
# Keys are retrieved from Streamlit secrets (local .streamlit/secrets.toml)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_TOKEN = st.secrets.get("HUGGINGFACE_TOKEN", "")
GEMINI_API_KEY = "" # Environment-provided runtime key for Gemini

# =================================================================
# 2. MODEL REGISTRY
# =================================================================
# Text/Reasoning Models
TEXT_MODEL_GROQ = "llama3-70b-8192"

# Vision (LVM) Models - Cloud
VISION_MODEL_GEMINI = "gemini-2.5-flash-preview-09-2025"
VISION_MODEL_GROQ = "llama-3.2-11b-vision-preview"
VISION_MODEL_HF = "meta-llama/Llama-3.2-11B-Vision-Instruct"

# Vision (LVM) Models - Local (Ollama)
OLLAMA_VISION_MODEL = "llama3.2-vision" # Alternatives: "llava" or "moondream"
OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"

# =================================================================
# 3. AGENTIC SYSTEM PROMPTS
# =================================================================
SYSTEM_PROMPTS = {
    "ORCHESTRATOR": """
        You are the Lead PCB Systems Architect. Your role is to synthesize findings from 
        Vision, Physics, and Compliance agents into a cohesive executive summary. 
        Prioritize manufacturing yield and long-term reliability.
    """,
    "VISION_AGENT": """
        You are an expert Optical Inspection (AOI) AI. Analyze the provided PCB image or 
        Gerber rendering. Identify acid traps (90-degree traces), solder bridges, 
        drilling offsets, and copper slivers. Return findings in structured JSON format.
    """,
    "PHYSICS_AGENT": """
        You are a Senior Signal Integrity (SI) and Thermal Engineer. Analyze board 
        stackups for potential crosstalk, impedance violations, and thermal hotspots.
    """,
    "REWORK_AGENT": """
        You are a Senior PCB Rework Specialist. For a given defect, provide highly technical, 
        step-by-step physical rework instructions. Reference IPC-7711/7721 standards.
    """
}

# =================================================================
# 4. CLOUD INFERENCE: GROQ (TEXT & VISION)
# =================================================================
def get_groq_chat_completion(prompt: str, system_role: str = "ORCHESTRATOR") -> str:
    """Ultra-fast text reasoning using Groq's LPU."""
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not configured."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": TEXT_MODEL_GROQ,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPTS.get(system_role, "")},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1 
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Groq Text Error: {str(e)}"

def get_groq_vision_analysis(image_bytes: bytes, prompt: str) -> str:
    """Llama-3.2-11b Vision inference via Groq Cloud."""
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY required for vision."

    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": VISION_MODEL_GROQ,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{SYSTEM_PROMPTS['VISION_AGENT']}\n\nTask: {prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Groq Vision Error: {str(e)}"

# =================================================================
# 5. CLOUD INFERENCE: HUGGING FACE
# =================================================================
def get_huggingface_vision_analysis(image_bytes: bytes, prompt: str) -> str:
    """Llama-3.2 Vision inference via Hugging Face Serverless API."""
    if not HF_TOKEN:
        return "Error: HUGGINGFACE_TOKEN required."

    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    url = f"https://api-inference.huggingface.co/models/{VISION_MODEL_HF}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    
    payload = {
        "model": VISION_MODEL_HF,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{SYSTEM_PROMPTS['VISION_AGENT']}\n\nTask: {prompt}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ],
        "parameters": {"max_new_tokens": 1024}
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list): return result[0].get('generated_text', str(result))
        return result.get('choices', [{}])[0].get('message', {}).get('content', str(result))
    except Exception as e:
        return f"Hugging Face Vision Error: {str(e)}"

# =================================================================
# 6. LOCAL INFERENCE: OLLAMA (PRIVATE DEPLOYMENT)
# =================================================================
def get_ollama_vision_analysis(image_bytes: bytes, prompt: str) -> str:
    """Local inference for privacy-conscious enterprise setups."""
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        "model": OLLAMA_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"{SYSTEM_PROMPTS['VISION_AGENT']}\n\nTask: {prompt}",
                "images": [base64_image]
            }
        ],
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['message']['content']
    except Exception as e:
        return f"Ollama Local Error: {str(e)}. Ensure Ollama is running locally."

# =================================================================
# 7. UNIFIED AGENT INTERFACE (LANGGRAPH READY)
# =================================================================
def get_visual_analysis(image_bytes: bytes, prompt: str, provider: str = "groq") -> str:
    """
    Primary interface for the Vision Agent node in LangGraph.
    Routing based on the 'provider' parameter.
    """
    if provider == "ollama":
        return get_ollama_vision_analysis(image_bytes, prompt)
    elif provider == "huggingface":
        return get_huggingface_vision_analysis(image_bytes, prompt)
    elif provider == "groq" and GROQ_API_KEY:
        return get_groq_vision_analysis(image_bytes, prompt)
    
    # Final Fallback to Gemini 2.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{VISION_MODEL_GEMINI}:generateContent?key={GEMINI_API_KEY}"
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": "image/png", "data": base64_image}}
            ]
        }],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPTS["VISION_AGENT"]}]}
    }
    try:
        response = requests.post(url, json=payload, timeout=20)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Gemini Fallback Error: {str(e)}"

# =================================================================
# 8. UTILITIES
# =================================================================
def generate_rework_suggestion(defect_type: str, location: str) -> str:
    """Invokes the Rework Agent to provide IPC-standard physical fixes."""
    context = f"Defect: {defect_type} detected at location {location}."
    prompt = f"Provide a technical rework plan for: {context}"
    return get_groq_chat_completion(prompt, system_role="REWORK_AGENT")
