import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

def search_ideas():
    st.title(":material/search: Search Ideas")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search ideas by keyword", placeholder="Enter search term", key="search_query")
    with col2:
        search_type = st.selectbox("Search type", ["hybrid", "keyword", "full_text"], index=0, key="search_type")

    if search_query:
        with st.spinner("Searching ideas..."):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/search/ideas",
                    params={"q": search_query, "search_type": search_type}
                )
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results:
                        st.subheader(f"Found {len(results)} results")
                        for result in results:
                            with st.container(border=True):
                                st.subheader(result["title"])
                                st.write(result["raw_description"][:200] + "...")
                                st.caption(f":material/label: {', '.join(result.get('tags', []))}")
                    else:
                        st.info("No results found")
                else:
                    st.error("Search failed")
            except Exception as e:
                st.error(f"Search error: {e}")