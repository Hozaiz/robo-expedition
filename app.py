import streamlit as st
from frontend.chat_ui import render_chat_ui

st.set_page_config(
    page_title="Unified AI Chat Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal, modern CSS
st.markdown("""
    <style>
        .block-container { padding: 1.5rem 2rem; }
        .stChatMessage { border-radius: 12px; margin: 0.5rem 0; }
        .st-emotion-cache-6qob1r, .st-emotion-cache-1r4qj8v { background: #f0f2f6; }
        footer { display: none; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Robo's Expedition</h1>", unsafe_allow_html=True)

render_chat_ui()
