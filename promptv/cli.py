import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from promptv import config
from promptv.client import ClientError, OpenAIClient
from promptv.diff import text_diff, version_diff
from promptv.store import StoreError, VersionStore


def build_parser():
    parser = argparse.ArgumentParser(
        prog="promptv",
        description="Save, diff, and compare system-prompt versions across OpenAI-compatible endpoints (default Ollama).",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    sub_init = sub.add_parser("init", help="Create default config and data directories")
    sub_init.add_argument("--config-dir", help="Override config directory")

    # config
    sub_config = sub.add_parser("config", help="View or modify configuration")
    sub_config.add_argument("--endpoint", help="Set default endpoint")
    sub_config.add_argument("--model", help="Set default model")
    sub_config.add_argument("--data-dir", help="Set data directory")
    sub_config.add_argument("--show", action="store_true", help="Show current configuration")

    # save
    sub_save = sub.add_parser("save", help="Save a new prompt version")
    sub_save.add_argument("name", help="Prompt name")
    sub_save.add_argument("--file", help="Read prompt from file (default stdin)")
    sub_save.add_argument("--prompt", help="Prompt text directly")
    sub_save.add_argument("--endpoint", help="Override endpoint")
    sub_save.add_argument("--model", help="Override model")

    # list
    sub_list = sub.add_parser("list", help="List saved prompt versions")
    sub_list.add_argument("name", nargs="?", help="Filter by prompt name")

    # show
    sub_show = sub.add_parser("show", help="Show a prompt version")
    sub_show.add_argument("name", help="Prompt name (or name@vN)")
    sub_show.add_argument("--version", type=int, help="Specific version number")

    # diff
    sub_diff = sub.add_parser("diff", help="Diff two prompt versions")
    sub_diff.add_argument("a", help="First prompt (name or name@vN)")
    sub_diff.add_argument("b", help="Second prompt (name or name@vN)")

    # compare
    sub_compare = sub.add_parser("compare", help="Compare two prompts by calling an endpoint")
    sub_compare.add_argument("a", help="First prompt (name or name@vN)")
    sub_compare.add_argument("b", help="Second prompt (name or name@vN)")
    sub_compare.add_argument("--endpoint", required=True, help="Endpoint URL")
    sub_compare.add_argument("--model", required=True, help="Model name")
    sub_compare.add_argument("--message", default="Hello, can you introduce yourself?", help="User message to send")

    return parser


def parse_name_version(arg):
    if "@v" in arg:
        name, version_str = arg.split("@v", 1)
        try:
            version = int(version_str)
        except ValueError:
            raise SystemExit(f"invalid version in {arg!r}")
        return name, version
    return arg, None


def get_store(cfg):
    return VersionStore(cfg.get("data_dir"))


def cmd_init(args):
    cfg = config.default_config()
    if args.config_dir:
        cfg["data_dir"] = str(Path(args.config_dir) / "data")
    config.save_config(cfg)
    print(f"Initialized config at {config.config_dir() / 'config.json'}")
    print(f"Data directory: {cfg['data_dir']}")


def cmd_config(args):
    cfg = config.load_config()
    if args.endpoint:
        cfg["default_endpoint"] = args.endpoint
    if args.model:
        cfg["default_model"] = args.model
    if args.data_dir:
        cfg["data_dir"] = args.data_dir
    if args.endpoint or args.model or args.data_dir:
        config.save_config(cfg)
    if args.show or not (args.endpoint or args.model or args.data_dir):
        print(json.dumps(cfg, indent=2))
    return 0


def cmd_save(args):
    cfg = config.load_config()
    store = get_store(cfg)
    if args.file:
        prompt = open(args.file, encoding="utf-8").read()
    elif args.prompt is not None:
        prompt = args.prompt
    else:
        prompt = sys.stdin.read()
    prompt = prompt.rstrip("\n")
    if not prompt:
        raise SystemExit("prompt is empty")
    endpoint = args.endpoint or cfg.get("default_endpoint", "")
    model = args.model or cfg.get("default_model", "")
    record = store.save(args.name, prompt, endpoint, model)
    print(f"Saved {record.name} v{record.version} to {record.path}")
    return 0


def cmd_list(args):
    cfg = config.load_config()
    store = get_store(cfg)
    records = store.list_versions(args.name)
    if not records:
        return 0
    current_name = None
    for record in records:
        if record.name != current_name:
            if current_name is not None:
                print()
            print(f"{record.name}:")
            current_name = record.name
        model_part = f" [{record.model}]" if record.model else ""
        print(f"  v{record.version:03d}  {record.created}  {record.endpoint}{model_part}")
    return 0


def cmd_show(args):
    cfg = config.load_config()
    store = get_store(cfg)
    name, version = parse_name_version(args.name)
    if args.version is not None:
        version = args.version
    record = store.get(name, version)
    print(record.content, end="")
    return 0


def cmd_diff(args):
    cfg = config.load_config()
    store = get_store(cfg)
    name_a, version_a = parse_name_version(args.a)
    name_b, version_b = parse_name_version(args.b)
    record_a = store.get(name_a, version_a)
    record_b = store.get(name_b, version_b)
    diff = version_diff(record_a, record_b)
    if diff:
        sys.stdout.write(diff)
    else:
        print("(no differences)")
    return 0


def cmd_compare(args):
    cfg = config.load_config()
    store = get_store(cfg)
    name_a, version_a = parse_name_version(args.a)
    name_b, version_b = parse_name_version(args.b)
    record_a = store.get(name_a, version_a)
    record_b = store.get(name_b, version_b)
    client = OpenAIClient()
    try:
        response_a = client.chat(args.endpoint, args.model, record_a.content, args.message)
        response_b = client.chat(args.endpoint, args.model, record_b.content, args.message)
    except ClientError as exc:
        raise SystemExit(str(exc))
    print(f"=== {record_a.name} v{record_a.version} ===")
    print(response_a)
    print()
    print(f"=== {record_b.name} v{record_b.version} ===")
    print(response_b)
    print()
    diff = text_diff(response_a, response_b, fromfile=f"{record_a.name} v{record_a.version}", tofile=f"{record_b.name} v{record_b.version}")
    if diff:
        print("--- response diff ---")
        sys.stdout.write(diff)
    else:
        print("(responses are identical)")
    return 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            cmd_init(args)
        elif args.command == "config":
            cmd_config(args)
        elif args.command == "save":
            cmd_save(args)
        elif args.command == "list":
            cmd_list(args)
        elif args.command == "show":
            cmd_show(args)
        elif args.command == "diff":
            cmd_diff(args)
        elif args.command == "compare":
            cmd_compare(args)
        else:
            parser.print_help()
            return 1
    except (StoreError, ClientError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    return 0