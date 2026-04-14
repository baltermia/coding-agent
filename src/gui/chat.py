import streamlit as st


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
    if st.button("Search Web", width='stretch'):
        try:
            st.session_state.last_search_results = search_manager.perform_search(query)
        except Exception as err:
            st.error(f"Search failed: {err}")

    if st.session_state.last_search_results:
        for idx, result in enumerate(st.session_state.last_search_results, start=1):
            st.markdown(f"{idx}. **{result['title']}**")
            st.write(result["snippet"])
            if result.get("url"):
                st.markdown(f"[Open source]({result['url']})")
