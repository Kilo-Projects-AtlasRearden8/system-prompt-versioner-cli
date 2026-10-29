import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class StoreError(Exception):
    pass


@dataclass
class VersionRecord:
    name: str
    version: int
    created: str
    endpoint: str
    model: str
    digest: str
    path: Path
    content: str


def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _digest(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _validate_name(name):
    if not SAFE_NAME.match(name):
        raise StoreError(f"invalid prompt name: {name!r}")


def format_frontmatter(meta):
    lines = ["---"]
    for key in ["name", "version", "created", "endpoint", "model", "digest"]:
        if key in meta:
            lines.append(f"{key}: {meta[key]}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def parse_frontmatter(text):
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        return {}, text
    end = None
    for index in range(1, len(lines)):
        if lines[index] == "---":
            end = index
            break
    if end is None:
        return {}, text
    meta = {}
    for line in lines[1:end]:
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    body = "\n".join(lines[end + 1 :])
    if body.startswith("\n"):
        body = body[1:]
    return meta, body


class VersionStore:
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else data_dir()
        self.versions_dir = self.data_dir / "versions"

    def _name_dir(self, name):
        return self.versions_dir / name

    def _next_version(self, name_dir):
        existing = []
        if name_dir.is_dir():
            for path in name_dir.glob("v*.md"):
                try:
                    existing.append(int(path.stem[1:]))
                except ValueError:
                    continue
        return max(existing, default=0) + 1

    def save(self, name, prompt, endpoint, model):
        _validate_name(name)
        name_dir = self._name_dir(name)
        name_dir.mkdir(parents=True, exist_ok=True)
        version = self._next_version(name_dir)
        meta = {
            "name": name,
            "version": str(version),
            "created": _now_iso(),
            "endpoint": endpoint,
            "model": model,
            "digest": _digest(prompt),
        }
        content = format_frontmatter(meta) + prompt
        if not content.endswith("\n"):
            content += "\n"
        path = name_dir / f"v{version:03d}.md"
        with path.open("w", encoding="utf-8") as handle:
            handle.write(content)
        return VersionRecord(
            name=name,
            version=version,
            created=meta["created"],
            endpoint=endpoint,
            model=model,
            digest=meta["digest"],
            path=path,
            content=prompt,
        )

    def _iter_records(self, name=None):
        records = []
        if not self.versions_dir.is_dir():
            return records
        name_dirs = [self._name_dir(name)] if name else sorted(self.versions_dir.iterdir())
        for name_dir in name_dirs:
            if not name_dir.is_dir():
                continue
            for path in sorted(name_dir.glob("v*.md")):
                try:
                    text = path.read_text(encoding="utf-8")
                except OSError:
                    continue
                meta, body = parse_frontmatter(text)
                try:
                    version = int(meta.get("version", "0"))
                except ValueError:
                    version = 0
                records.append(
                    VersionRecord(
                        name=meta.get("name", name_dir.name),
                        version=version,
                        created=meta.get("created", ""),
                        endpoint=meta.get("endpoint", ""),
                        model=meta.get("model", ""),
                        digest=meta.get("digest", ""),
                        path=path,
                        content=body,
                    )
                )
        records.sort(key=lambda record: (record.name, record.version))
        return records

    def list_versions(self, name=None):
        if name:
            _validate_name(name)
        return self._iter_records(name)

    def get(self, name, version=None):
        _validate_name(name)
        records = [r for r in self._iter_records(name) if r.name == name]
        if not records:
            raise StoreError(f"no saved versions for prompt: {name}")
        if version is None:
            return records[-1]
        for record in records:
            if record.version == version:
                return record
        raise StoreError(f"version {version} not found for prompt: {name}")

    def delete(self, name, version=None):
        record = self.get(name, version)
        record.path.unlink()
        name_dir = self._name_dir(name)
        remaining = list(name_dir.glob("v*.md"))
        if not remaining:
            try:
                name_dir.rmdir()
            except OSError:
                pass
        return record
