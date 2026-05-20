from backend.system_prompter import SystemPrompter

def test_prompt_contains_task():
    sp = SystemPrompter()

    result = sp.generate_prompt(user_message = "test-1")

    assert "test-1" in result
    assert "<task>" in result
    assert "</task>" in result

def test_prompt_includes_file_context():
    sp = SystemPrompter()

    file_context = "def foo(): pass"

    result = sp.generate_prompt(
        user_message="Explain function",
        file_context=file_context
    )

    assert "def foo()" in result
    assert "FILE" in result.upper()

def test_prompt_includes_debug_context():
    sp = SystemPrompter()

    debug_context = "Traceback: ValueError"

    result = sp.generate_prompt(
        user_message="Fix error",
        debug_context=debug_context
    )

    assert "ValueError" in result
    assert "DEBUG" in result.upper()