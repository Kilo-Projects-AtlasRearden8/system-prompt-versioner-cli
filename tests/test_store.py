import pytest
from promptv.store import VersionStore, StoreError


def test_save_creates_versioned_file(temp_dir):
    store = VersionStore(temp_dir / "data")
    record = store.save("test-prompt", "You are helpful.", "http://localhost:11434/v1", "llama3")
    assert record.name == "test-prompt"
    assert record.version == 1
    assert record.endpoint == "http://localhost:11434/v1"
    assert record.model == "llama3"
    assert record.digest.startswith("sha256:")
    assert record.path.exists()


def test_save_multiple_versions_increments(temp_dir):
    store = VersionStore(temp_dir / "data")
    store.save("bot", "v1", "endpoint", "model")
    store.save("bot", "v2", "endpoint", "model")
    record = store.save("bot", "v3", "endpoint", "model")
    assert record.version == 3
    records = store.list_versions("bot")
    assert len(records) == 3
    assert [r.version for r in records] == [1, 2, 3]


def test_list_versions_filter_by_name(temp_dir):
    store = VersionStore(temp_dir / "data")
    store.save("alpha", "a1", "e", "m")
    store.save("alpha", "a2", "e", "m")
    store.save("beta", "b1", "e", "m")
    alphas = store.list_versions("alpha")
    assert len(alphas) == 2
    assert all(r.name == "alpha" for r in alphas)
    all_records = store.list_versions()
    assert len(all_records) == 3


def test_get_latest_and_specific(temp_dir):
    store = VersionStore(temp_dir / "data")
    store.save("bot", "first", "e", "m")
    store.save("bot", "second", "e", "m")
    latest = store.get("bot")
    assert latest.version == 2
    assert latest.content == "second\n"
    specific = store.get("bot", version=1)
    assert specific.version == 1
    assert specific.content == "first\n"


def test_get_missing_raises(temp_dir):
    store = VersionStore(temp_dir / "data")
    with pytest.raises(StoreError):
        store.get("nonexistent")
    store.save("bot", "content", "e", "m")
    with pytest.raises(StoreError):
        store.get("bot", version=99)


def test_frontmatter_roundtrip(temp_dir):
    store = VersionStore(temp_dir / "data")
    record = store.save("bot", "hello world", "http://example.com/v1", "test-model")
    text = record.path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "name: bot" in text
    assert "version: 1" in text
    assert "endpoint: http://example.com/v1" in text
    assert "model: test-model" in text
    assert "digest: sha256:" in text
    assert text.endswith("hello world\n")


def test_invalid_name_raises(temp_dir):
    store = VersionStore(temp_dir / "data")
    with pytest.raises(StoreError):
        store.save("../bad", "x", "e", "m")
    with pytest.raises(StoreError):
        store.save("bad/name", "x", "e", "m")
    with pytest.raises(StoreError):
        store.save("", "x", "e", "m")


def test_delete_removes_file_and_cleans_empty_dir(temp_dir):
    store = VersionStore(temp_dir / "data")
    record = store.save("bot", "v1", "e", "m")
    store.save("bot", "v2", "e", "m")
    deleted = store.delete("bot", version=1)
    assert deleted.version == 1
    assert not deleted.path.exists()
    remaining = store.list_versions("bot")
    assert len(remaining) == 1
    assert remaining[0].version == 2
    store.delete("bot", version=2)
    assert not (temp_dir / "data" / "versions" / "bot").exists()


def test_digest_matches_content(temp_dir):
    store = VersionStore(temp_dir / "data")
    record = store.save("bot", "exact content", "e", "m")
    import hashlib
    expected = "sha256:" + hashlib.sha256(b"exact content").hexdigest()
    assert record.digest == expected