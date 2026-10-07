import streamlit as st
from typing import Optional, List

def dashboard():
    st.title("💡 Idea Tracker")
    st.markdown("Local-first idea capture → execution system")

    # Add your dashboard components here
    st.write("Welcome to the Idea Tracker!")

if __name__ == "__main__":
    dashboard()