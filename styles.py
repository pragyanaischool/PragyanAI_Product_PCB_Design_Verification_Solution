import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        /* Main Theme Overrides */
        .stApp {
            background-color: #0E1117;
            color: #E0E0E0;
        }
        
        /* Custom Header Colors */
        h1, h2, h3 {
            color: #4FB3FF !important;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }

        /* Defect Cards */
        .defect-card {
            background-color: #1A1C23;
            border-left: 5px solid #FF4B4B;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        
        .severity-high { border-left-color: #FF4B4B; }
        .severity-med { border-left-color: #FFA500; }
        .severity-low { border-left-color: #4FB3FF; }

        /* Metric Styling */
        [data-testid="stMetricValue"] {
            color: #4FB3FF;
            font-family: 'JetBrains Mono', monospace;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #161B22;
            border-right: 1px solid #30363D;
        }
        
        /* Tooltip-like Info */
        .stAlert {
            background-color: #0D1117;
            border: 1px solid #30363D;
        }
        </style>
    """, unsafe_content_safe=True)
