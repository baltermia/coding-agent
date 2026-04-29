import streamlit as st


@st.dialog("Search Results", width="large")
def _search_results_dialog():
    query = st.session_state.last_search_query or ""

    if query:
        st.caption(f"Results for: {query}")

    results = st.session_state.last_search_results or []
    if not results:
        st.info("No results were found for the last search.")
    else:
        for idx, result in enumerate(results, start=1):
            st.markdown(f"{idx}. **{result['title']}**")
            st.write(result["snippet"])
            if result.get("url"):
                st.markdown(f"[Open source]({result['url']})")

    if st.button("Close", use_container_width=True):
        st.session_state.active_dialog = None
        st.rerun()
def chat(chat_manager, search_manager):
    chat_box = st.container(border=True)
    with chat_box:
        if not st.session_state.chat_history:
            st.write("No messages yet.")
        else:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    user_message = st.chat_input("Ask for code suggestions, debugging, or explanations")
    if user_message:
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        file_context = st.session_state.editor_content if st.session_state.selected_file else ""
        debug_context = (
            f"stdout:\n{st.session_state.execution_output}\n\n"
            f"stderr:\n{st.session_state.execution_error}"
        )
        response = chat_manager.send_message(user_message, file_context=file_context, debug_context=debug_context)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    st.divider()
    query = st.text_input("Search query", placeholder="e.g. streamlit session_state best practices")
    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if st.button("Search Web", use_container_width=True):
            if not query.strip():
                st.error("Please enter a search query.")
            else:
                try:
                    results = search_manager.perform_search(query)
                    st.session_state.last_search_query = query
                    st.session_state.last_search_results = results
                    st.session_state.active_dialog = "search_results"
                except Exception as err:
                    st.session_state.active_dialog = None
                    st.error(f"Search failed: {err}")

    with action_col2:
        if st.button("Show Last Search", use_container_width=True, disabled=st.session_state.last_search_query is None):
            st.session_state.active_dialog = "search_results"
