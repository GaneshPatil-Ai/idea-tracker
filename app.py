import streamlit as st
from pages.dashboard import dashboard
from pages.create_idea import create_idea
from pages.search_ideas import search_ideas
from pages.statistics import statistics

# Configure page
st.set_page_config(
    page_title="Idea Tracker",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page(dashboard, title="Dashboard", icon=":material/dashboard:"),
    st.Page(create_idea, title="Create Idea", icon=":material/add:"),
    st.Page(search_ideas, title="Search", icon=":material/search:"),
    st.Page(statistics, title="Statistics", icon=":material/insights:"),
]

st.navigation(pages).run()