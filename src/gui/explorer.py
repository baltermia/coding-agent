import json
import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import os
from pathlib import Path

def _file_badge(file_path: str) -> str:
    suffix = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
    badges = {
        "py": "PY",
        "js": "JS",
        "ts": "TS",
        "html": "HT",
        "css": "CS",
        "json": "JN",
        "md": "MD",
        "txt": "TX",
    }
    return badges.get(suffix, "FI")

def _file_icon(file_path: str) -> dict[str, str]:
    suffix = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
    icons = {
        "py": {"icon": "filetype-py", "color": "yellow"},
        "js": {"icon": "filetype-js", "color": "orange"},
        "ts": {"icon": "file-earmark-code-fill", "color": "blue"},
        "html": {"icon": "filetype-html", "color": "red"},
        "css": {"icon": "filetype-css", "color": "pink"},
        "json": {"icon": "filetype-json", "color": "grape"},
        "md": {"icon": "filetype-md", "color": "indigo"},
        "txt": {"icon": "filetype-txt", "color": "white"},
    }

    return icons.get(suffix, {"icon": "file", "color": "white"})

def _format_file_label(file_path: str) -> str:
    name = file_path.rsplit("/", 1)[-1]
    return f"[{_file_badge(file_path)}] {name}"

def _extract_selected_row(event) -> int | None:
    if not event:
        return None

    selection = event.selection if hasattr(event, "selection") else event.get("selection", {})
    rows = selection.rows if hasattr(selection, "rows") else selection.get("rows", [])

    if rows:
        row = rows[0]
        return row if isinstance(row, int) else None

    cells = selection.cells if hasattr(selection, "cells") else selection.get("cells", [])
    if not cells:
        return None

    first = cells[0]
    if isinstance(first, dict):
        row = first.get("row")
        return row if isinstance(row, int) else None
    if isinstance(first, (tuple, list)) and first:
        row = first[0]
        return row if isinstance(row, int) else None

    row = getattr(first, "row", None)
    return row if isinstance(row, int) else None

def _new_file_dialog_cleanup() -> None:
    st.session_state.active_dialog = None

@st.dialog("Create New File", on_dismiss=_new_file_dialog_cleanup)
def _new_file_dialog(file_manager):
    new_file_name = st.text_input(
        "File name",
        value="",
        placeholder="e.g., main.py or data.json",
        key="new_file_name_input"
    )

    if new_file_name:
        # Validate file extension
        if "." not in new_file_name:
            st.warning("Please include a file extension (e.g., .py, .js)")
        else:
            suffix = "." + new_file_name.rsplit(".", 1)[-1].lower()
            if suffix not in {".py", ".js", ".ts", ".html", ".css", ".json", ".md", ".txt"}:
                st.warning(f"Unsupported file type: {suffix}")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Create", use_container_width=True, key="create_file_btn"):
                        try:
                            file_manager.save_file(new_file_name, "")
                            st.session_state.selected_file = new_file_name
                            st.session_state.editor_content = ""
                            st.session_state.active_dialog = None
                            st.success(f"File created: {new_file_name}")
                            st.rerun()
                        except Exception as err:
                            st.error(f"Error creating file: {err}")
                with col2:
                    if st.button("Cancel", use_container_width=True, key="cancel_file_btn"):
                        st.session_state.active_dialog = None
                        st.rerun()


def explorer(file_manager):
    st.sidebar.markdown("**Files**")

    new_root = st.sidebar.text_input("Project root", value=st.session_state.project_root)
    if new_root != st.session_state.project_root:
        st.session_state.project_root = new_root
        st.rerun()

    # Add new file button
    if st.sidebar.button("➕ Add New File", use_container_width=True):
        st.session_state.active_dialog = "create_file"

    try:
        files = file_manager.list_files()
    except Exception as err:
        st.sidebar.error(f"Cannot list files: {err}")
        return

    if not files:
        st.sidebar.info("No supported files found.")
        return

    filter_query = st.sidebar.text_input("Filter files", value="", placeholder="type to filter")
    visible_files = [f for f in files if filter_query.lower() in f.lower()]

    if not visible_files:
        st.sidebar.info("No files match your filter.")
        return

    current = st.session_state.selected_file if st.session_state.selected_file in visible_files else visible_files[0]

    table = pd.DataFrame({"File": [_format_file_label(path) for path in visible_files]})

    event = st.sidebar.dataframe(
        table,
        hide_index=True,
        width='stretch',
        height=420,
        on_select="rerun",
        selection_mode="single-cell",
        key="files_table",
    )

    selected = current
    row_idx = _extract_selected_row(event)
    if isinstance(row_idx, int) and 0 <= row_idx < len(visible_files):
        selected = visible_files[row_idx]

    if selected != st.session_state.selected_file:
        content = file_manager.read_file(selected)
        st.session_state.selected_file = selected
        st.session_state.editor_content = content
        st.rerun()

    if not st.session_state.selected_file:
        content = file_manager.read_file(current)
        st.session_state.selected_file = current
        st.session_state.editor_content = content

def explorer_tree(file_manager):
    st.sidebar.markdown("**Files**")

    new_root = st.sidebar.text_input(
        "Project root",
        value=st.session_state.project_root
    )
    if new_root != st.session_state.project_root:
        st.session_state.project_root = new_root
        st.rerun()

    try:
        tree = file_manager.build_tree()
    except Exception as err:
        st.sidebar.error(f"Cannot build file tree: {err}")
        return

    tree_items = [dict_to_sac(tree, st.session_state.project_root)]

    with st.sidebar:
        st.title("Explorer")
        selected = sac.tree(
            items=tree_items,
            show_line=True,
            format_func=lambda path: os.path.basename(path),
            open_all=False,
            checkbox=False
        )

        try:
            if selected != st.session_state.selected_file:
                content = file_manager.read_file_absolute(selected)
                st.session_state.selected_file = selected
                st.session_state.editor_content = content
                st.rerun()
        except Exception as err:
            print(err)


def dict_to_sac(node, current_path=""):
    if current_path.split("/")[-1] != node["name"]:
        full_node_path = os.path.join(current_path, node["name"])
    else:
        full_node_path = current_path

    children = []

    for folder in node.get("children_dirs", []):
        children.append(dict_to_sac(folder, current_path=full_node_path))

    for file in node.get("children_files", []):
        full_file_path = os.path.join(full_node_path, file["name"])
        file_icon = _file_icon(file["name"])
        children.append(
            sac.TreeItem(label=full_file_path, icon=sac.BsIcon(name=file_icon["icon"], size=15, color=file_icon["color"]))
        )

    return sac.TreeItem(
        label=node["name"],
        icon='folder-fill' if node["type"] == "dir" else 'file-earmark',
        children=children if children else None
    )