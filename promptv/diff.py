import difflib


def text_diff(before, after, fromfile="before", tofile="after"):
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(before_lines, after_lines, fromfile=fromfile, tofile=tofile, lineterm="")
    )


def version_diff(record_a, record_b):
    return text_diff(record_a.content, record_b.content, fromfile=f"{record_a.name} v{record_a.version}", tofile=f"{record_b.name} v{record_b.version}")
