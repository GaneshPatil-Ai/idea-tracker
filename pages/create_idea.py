import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

def create_idea():
    st.title(":material/add: Create New Idea")
    st.markdown("Enter your raw idea and our AI will structure it into actionable insights.")

    # Capture raw idea
    with st.form("idea_form"):
        st.markdown("### Your Raw Idea")
        title = st.text_input("Title", placeholder="What is this idea about?", key="title")
        raw_text = st.text_area(
            "Describe your idea in your own words",
            placeholder="I want to build a tool that helps developers track habits...",
            height=200,
            key="raw_text"
        )
        tags_input = st.text_input(
            "Tags (comma-separated)",
            placeholder="habit, tracking, mobile",
            help="Optional tags for organization",
            key="tags"
        )

        submitted = st.form_submit_button("Structure & Analyze", type="primary")

    if submitted:
        if not title or not raw_text:
            st.error("Please provide both a title and description.")
            return

        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

        # Show AI processing state
        with st.spinner("Understanding your idea and extracting key elements..."):
            # Call AI structure endpoint
            try:
                ai_response = requests.post(
                    f"{API_BASE_URL}/structure-idea",
                    json={"raw_text": raw_text},
                    timeout=30
                )
                structure_result = ai_response.json() if ai_response.status_code == 200 else {}
            except Exception as e:
                structure_result = {}
                st.warning(f"AI structuring unavailable: {e}")

            # Create the idea in the backend
            try:
                create_response = requests.post(
                    f"{API_BASE_URL}/api/ideas",
                    json={
                        "title": title,
                        "description": raw_text,
                        "tags": tags
                    }
                )
                idea_data = create_response.json() if create_response.status_code == 200 else {}
            except Exception as e:
                st.error(f"Failed to save idea: {e}")
                idea_data = {}

        if idea_data:
            st.success(f"✅ Idea created: **{title}**")
            idea_id = idea_data.get("id")

            # Display structured analysis (from AI or fallback)
            st.divider()
            st.subheader("📊 AI Analysis")

            # Structured insights section
            problem_statement = structure_result.get("problem_statement", f"The core challenge: {raw_text[:120]}...")
            with st.expander("🎯 Problem Statement", expanded=True):
                st.info(problem_statement)

            risks = structure_result.get("risks", ["Requires consistent user engagement", "Competition exists in tracking space"])
            with st.expander("⚠️ Key Risks & Assumptions"):
                for r in risks:
                    st.write(f"- {r}")

            # Next actions
            st.subheader("📋 Suggested Next Actions")
            with st.spinner("Generating actionable next steps..."):
                try:
                    actions_resp = requests.post(
                        f"{API_BASE_URL}/suggest-actions/{idea_id or 1}",
                        timeout=15
                    )
                    actions = actions_resp.json().get("actions", []) if actions_resp.status_code == 200 else []
                except:
                    actions = [
                        "Define minimum viable feature set",
                        "Identify 3 potential users for validation",
                        "Draft a 1-week experiment plan"
                    ]

            for idx, action in enumerate(actions or ["No actions generated yet"], 1):
                action_text = action.get("description") if isinstance(action, dict) else action
                st.container(border=True)
                col_action, col_done = st.columns([4, 1])
                with col_action:
                    st.write(f"**{idx}.** {action_text}")
                with col_done:
                    st.button("Mark Done", key=f"done_{idx}", help="Track progress")

            st.divider()
            # Show saved metadata
            with st.expander("🔍 Saved Details"):
                st.write(f"**Title:** {idea_data.get('title')}")
                st.write(f"**Status:** {idea_data.get('status', 'INBOX')}")
                st.write(f"**Tags:** {', '.join(tags) if tags else 'None'}")
                st.write(f"**Description:** {idea_data.get('description', raw_text)[:200]}...")
