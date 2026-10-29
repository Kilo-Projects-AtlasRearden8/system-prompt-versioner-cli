import pytest
from promptv.cli import main


def test_init_creates_config(run_cli, temp_dir):
    code, out, err = run_cli(["init"])
    assert code == 0
    assert "Initialized config" in out


def test_config_show(run_cli, temp_dir):
    code, out, err = run_cli(["config", "--show"])
    assert code == 0
    assert "default_endpoint" in out


def test_config_set_endpoint(run_cli, temp_dir):
    code, out, err = run_cli(["config", "--endpoint", "http://custom:1234/v1"])
    assert code == 0
    code, out, err = run_cli(["config", "--show"])
    assert "http://custom:1234/v1" in out


def test_save_from_prompt_arg(run_cli, temp_dir):
    code, out, err = run_cli(["save", "test-prompt", "--prompt", "You are a bot."])
    assert code == 0
    assert "Saved test-prompt v1" in out


def test_save_from_file(run_cli, temp_dir):
    prompt_file = temp_dir / "prompt.txt"
    prompt_file.write_text("File prompt content")
    code, out, err = run_cli(["save", "file-prompt", "--file", str(prompt_file)])
    assert code == 0
    assert "Saved file-prompt v1" in out


def test_list_empty(run_cli, temp_dir):
    code, out, err = run_cli(["list"])
    assert code == 0
    assert out.strip() == ""


def test_list_after_save(run_cli, temp_dir):
    run_cli(["save", "alpha", "--prompt", "a1"])
    run_cli(["save", "alpha", "--prompt", "a2"])
    run_cli(["save", "beta", "--prompt", "b1"])
    code, out, err = run_cli(["list"])
    assert code == 0
    assert "alpha:" in out
    assert "beta:" in out
    assert "v001" in out
    assert "v002" in out


def test_show_latest(run_cli, temp_dir):
    run_cli(["save", "bot", "--prompt", "first"])
    run_cli(["save", "bot", "--prompt", "second"])
    code, out, err = run_cli(["show", "bot"])
    assert code == 0
    assert out == "second\n"


def test_show_specific_version(run_cli, temp_dir):
    run_cli(["save", "bot", "--prompt", "first"])
    run_cli(["save", "bot", "--prompt", "second"])
    code, out, err = run_cli(["show", "bot", "--version", "1"])
    assert code == 0
    assert out == "first\n"


def test_show_name_at_version(run_cli, temp_dir):
    run_cli(["save", "bot", "--prompt", "first"])
    run_cli(["save", "bot", "--prompt", "second"])
    code, out, err = run_cli(["show", "bot@v2"])
    assert code == 0
    assert out == "second\n"


def test_show_missing(run_cli, temp_dir):
    code, out, err = run_cli(["show", "nonexistent"])
    assert code != 0


def test_diff_two_versions(run_cli, temp_dir):
    run_cli(["save", "prompt", "--prompt", "line 1\nline 2\n"])
    run_cli(["save", "prompt", "--prompt", "line 1\nline X\n"])
    code, out, err = run_cli(["diff", "prompt@v1", "prompt@v2"])
    assert code == 0
    assert "-line 2" in out
    assert "+line X" in out


def test_diff_same_content(run_cli, temp_dir):
    run_cli(["save", "a", "--prompt", "same"])
    run_cli(["save", "b", "--prompt", "same"])
    code, out, err = run_cli(["diff", "a", "b"])
    assert code == 0
    assert "(no differences)" in out


def test_compare_calls_endpoint(run_cli, mock_endpoint, temp_dir):
    run_cli(["save", "prompt-a", "--prompt", "System A"])
    run_cli(["save", "prompt-b", "--prompt", "System B"])
    code, out, err = run_cli(["compare", "prompt-a", "prompt-b", "--endpoint", mock_endpoint, "--model", "mock-model"])
    assert code == 0
    assert "prompt-a v1" in out
    assert "prompt-b v1" in out
    assert "mock response to: System A" in out
    assert "mock response to: System B" in out
    assert "--- response diff ---" in out


def test_compare_missing_args(run_cli, temp_dir):
    code, out, err = run_cli(["compare", "a", "b"])
    assert code != 0


def test_save_empty_prompt_fails(run_cli, temp_dir):
    code, out, err = run_cli(["save", "empty", "--prompt", ""])
    assert code != 0


def test_save_invalid_name_fails(run_cli, temp_dir):
    code, out, err = run_cli(["save", "../bad", "--prompt", "x"])
    assert code != 0


def test_help(run_cli):
    code, out, err = run_cli(["--help"])
    assert code == 0
    assert "promptv" in out


def test_version(run_cli):
    code, out, err = run_cli(["--version"])
    assert code == 0
    assert "1.0.0" in out