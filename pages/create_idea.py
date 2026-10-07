import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

def create_idea():
    st.title(":material/add: Create New Idea")

    with st.form("idea_form"):
        st.markdown("## Add New Idea")
        title = st.text_input("Title", placeholder="Enter idea title", key="title")
        description = st.text_area("Description", placeholder="Describe your idea", height=200, key="description")
        tags_input = st.text_input("Tags", placeholder="Comma-separated tags (e.g., ai, web, mobile)", help="Press Enter to submit after adding tags", key="tags")

        submitted = st.form_submit_button("Create Idea", type="primary")

        if submitted:
            if not title or not description:
                st.error("Please fill in both title and description")
                return

            tags = [t.strip() for t in tags_input.split(",") if t.strip()]

            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/ideas",
                    json={
                        "title": title,
                        "raw_description": description,
                        "tags": tags
                    }
                )
                if response.status_code == 200:
                    st.success("Idea created successfully!")
                    # Clear form after submission
                    st.session_state.clear()
                else:
                    st.error(f"Failed to create idea: {response.text}")
            except Exception as e:
                st.error(f"Error creating idea: {e}")
