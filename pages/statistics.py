import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

@st.cache_data(ttl=30)
def load_ideas():
    """Load ideas from API with caching."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/ideas")
        if response.status_code == 200:
            return response.json()
    except Exception:
        st.error("Failed to load ideas")
    return []

def statistics():
    st.title(":material/insights: Statistics")
    ideas = load_ideas()

    if not ideas:
        st.info("No ideas to analyze")
        return

    # Status distribution
    status_counts = {}
    for idea in ideas:
        status = idea["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ideas by Status")
        st.bar_chart(status_counts, alt="Bar chart showing distribution of ideas by status")

    # Tag distribution
    tag_counts = {}
    for idea in ideas:
        for tag in idea.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    with col2:
        st.subheader("Top Tags")
        if tag_counts:
            st.bar_chart(tag_counts, alt="Bar chart showing top tags used across ideas")
        else:
            st.info("No tags yet")