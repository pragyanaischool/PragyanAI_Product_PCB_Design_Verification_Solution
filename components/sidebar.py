import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
        st.title("Admin Console")
        view = st.radio("Navigation", ["Project Dashboard", "Agent Reasoning"])
        st.divider()
        st.session_state.ai_provider = st.selectbox("Vision Provider", ["groq", "gemini", "huggingface"])
        st.session_state.layer_count = st.selectbox("Layer Count", [2, 4, 6, 8, 12])
        st.session_state.safety_class = st.selectbox("Standard", ["Class 1", "Class 2", "Class 3 (High Rel)"])
        return view
