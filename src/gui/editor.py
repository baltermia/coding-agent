import streamlit as st
import ast
from streamlit_ace import st_ace


def _language_from_file(file_path: str) -> str:
    suffix = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
    mapping = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "html": "html",
        "css": "css",
        "json": "json",
        "md": "markdown",
        "txt": "plain_text",
    }
    return mapping.get(suffix, "plain_text")


def editor(file_manager, execution_engine, debug_logger):
    if not st.session_state.selected_file:
        st.info("Select and open a file in the sidebar to start editing.")
        return

    st.text(st.session_state.selected_file)

    language = _language_from_file(st.session_state.selected_file)
    ace_value = st_ace(
        value=st.session_state.editor_content,
        language=language,
        height=520,
        theme="tomorrow_night",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        wrap=False,
        show_gutter=True,
        show_print_margin=False,
        auto_update=True,
        key=f"editor_ace_{st.session_state.selected_file}",
    )
    if ace_value is not None:
        st.session_state.editor_content = ace_value

    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        if st.button("Save", width='stretch'):
            file_manager.save_file(st.session_state.selected_file, st.session_state.editor_content)
            st.success("File saved")

    with action_col2:
        if st.button("Check Syntax", width='stretch'):
            try:
                ast.parse(st.session_state.editor_content)
                st.success("Syntax looks valid")
            except SyntaxError as err:
                st.error(f"SyntaxError: {err.msg} (line {err.lineno})")

    with action_col3:
        if st.button("Run Code", width='stretch'):
            try:
                ast.parse(st.session_state.editor_content)
            except SyntaxError as err:
                st.error(f"SyntaxError: {err.msg} (line {err.lineno})")
            else:
                result = execution_engine.run_code(st.session_state.editor_content)
                out, err = debug_logger.format_debug_output(result)
                st.session_state.execution_output = out
                st.session_state.execution_error = err

    out_tab, err_tab = st.tabs(["Execution Output", "Debug / Errors"])

    with out_tab:
        if st.session_state.execution_error.strip():
            st.warning("⚠️ Errors occurred during execution. Check the **Debug / Errors** tab for details.")
        st.code(st.session_state.execution_output, language="text")

    with err_tab:
        st.code(st.session_state.execution_error, language="text")
