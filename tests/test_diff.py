from promptv.diff import text_diff, version_diff
from promptv.store import VersionRecord


def test_text_diff_identical():
    a = "line 1\nline 2\nline 3\n"
    b = "line 1\nline 2\nline 3\n"
    diff = text_diff(a, b)
    assert diff == ""


def test_text_diff_changed():
    a = "a\nb\nc\n"
    b = "a\nx\nc\n"
    diff = text_diff(a, b)
    assert "-b\n" in diff
    assert "+x\n" in diff


def test_text_diff_added():
    a = "a\nb\n"
    b = "a\nb\nc\n"
    diff = text_diff(a, b)
    assert "+c\n" in diff


def test_text_diff_removed():
    a = "a\nb\nc\n"
    b = "a\nb\n"
    diff = text_diff(a, b)
    assert "-c\n" in diff


def test_version_diff():
    record_a = VersionRecord(
        name="prompt",
        version=1,
        created="2026-01-01T00:00:00Z",
        endpoint="e",
        model="m",
        digest="d",
        path=None,
        content="first version\n",
    )
    record_b = VersionRecord(
        name="prompt",
        version=2,
        created="2026-01-01T00:00:00Z",
        endpoint="e",
        model="m",
        digest="d",
        path=None,
        content="second version\n",
    )
    diff = version_diff(record_a, record_b)
    assert "prompt v1" in diff
    assert "prompt v2" in diff
    assert "-first version\n" in diff
    assert "+second version\n" in diff