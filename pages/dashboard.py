import streamlit as st
from typing import List, Dict
import requests
from streamlit import cache_data

API_BASE_URL = "http://127.0.0.1:8000"

@cache_data(ttl=30, show_spinner="Loading ideas...")
def load_ideas() -> List[Dict]:
    """Load ideas from API with caching."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/ideas")
        if response.status_code == 200:
            return response.json()
    except Exception:
        st.error("Failed to load ideas")
    return []

@st.fragment
def dashboard_fragment():
    st.title("💡 Idea Tracker Dashboard")
    st.markdown("Local-first idea capture → execution system")

    ideas = load_ideas()

    # Stats
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        st.metric("Total Ideas", len(ideas), help="All ideas across all statuses")
    with col2:
        in_progress = len([i for i in ideas if i["status"] in ["EXPLORING", "BUILDING"]])
        st.metric("In Progress", in_progress, help="Ideas being explored or built")
    with col3:
        st.metric("Status Types", len(set(i["status"] for i in ideas)), help="Unique status categories")
    with col4:
        st.metric("Total Tags", len(set(tag for i in ideas for tag in i.get("tags", []))), help="All unique tags used")

    st.divider()

    # Ideas list
    st.subheader("Your Ideas")
    if ideas:
        for idea in ideas:
            with st.container(border=True, key=f"idea_{idea['id']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(idea["title"])
                    st.write(idea["raw_description"][:200] + "...")
                    if idea.get("tags"):
                        tags_html = " ".join([f":material/label:{tag}:" for tag in idea["tags"]])
                        st.caption(tags_html)
                with col2:
                    status_colors = {
                        "INBOX": "🔵",
                        "EXPLORING": "🟠",
                        "BUILDING": "🟢",
                        "LAUNCHED": "✅"
                    }
                    status_icon = status_colors.get(idea["status"], "⚪")
                    st.write(f"{status_icon} {idea['status']}")
    else:
        st.info("No ideas yet. Create one to get started!")

# Render the fragment
st.fragment(dashboard_fragment)
