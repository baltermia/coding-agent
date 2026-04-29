from pathlib import Path
import streamlit as st

from gui.chat import chat, _search_results_dialog
from gui.editor import editor
from gui.explorer import explorer, _new_file_dialog

from backend import (
    ChatManager,
    DebugLogger,
    ExecutionEngine,
    FileManager,
    SearchManager,
    SystemPrompter,
)

def _init_state() -> None:
    if "project_root" not in st.session_state:
        st.session_state.project_root = str(Path(__file__).resolve().parent.parent)

    if "selected_file" not in st.session_state:
        st.session_state.selected_file = ""

    if "editor_content" not in st.session_state:
        st.session_state.editor_content = ""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "execution_output" not in st.session_state:
        st.session_state.execution_output = "No execution yet."

    if "execution_error" not in st.session_state:
        st.session_state.execution_error = ""

    if "last_search_results" not in st.session_state:
        st.session_state.last_search_results = []

    if "last_search_query" not in st.session_state:
        st.session_state.last_search_query = None

    if "active_dialog" not in st.session_state:
        st.session_state.active_dialog = None


def main() -> None:
    st.set_page_config(page_title="AI Code Editor", layout="wide")

    _init_state()

    file_manager = FileManager(st.session_state.project_root)
    system_prompter = SystemPrompter()
    chat_manager = ChatManager(system_prompter)
    search_manager = SearchManager()
    execution_engine = ExecutionEngine()
    debug_logger = DebugLogger()

    explorer(file_manager)

    col_left, col_right = st.columns([2, 1], gap="large")

    with col_left:
        editor(file_manager, execution_engine, debug_logger)

    with col_right:
        chat(chat_manager, search_manager)

    if st.session_state.active_dialog == "search_results":
        _search_results_dialog()
    elif st.session_state.active_dialog == "create_file":
        _new_file_dialog(file_manager)


if __name__ == "__main__":
    main()
