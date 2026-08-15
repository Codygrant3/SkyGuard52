#!/usr/bin/env python3
"""Bounded local client for the Blender MCP add-on socket protocol.

This adapter exists because routed Codex child sessions can use shell tools but
do not currently receive third-party MCP tools in their direct tool catalog.
It talks only to the already-running Blender MCP add-on on loopback.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9876


def send_command(
    command_type: str,
    params: dict[str, Any] | None = None,
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout_seconds: float = 600.0,
) -> dict[str, Any]:
    payload = json.dumps(
        {"type": command_type, "params": params or {}},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    deadline = time.monotonic() + timeout_seconds
    buffer = bytearray()

    with socket.create_connection((host, port), timeout=min(timeout_seconds, 15.0)) as client:
        client.settimeout(1.0)
        client.sendall(payload)

        while time.monotonic() < deadline:
            try:
                chunk = client.recv(65536)
            except socket.timeout:
                continue
            if not chunk:
                break
            buffer.extend(chunk)
            try:
                response = json.loads(buffer.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(response, dict):
                raise RuntimeError("Blender MCP returned a non-object JSON response")
            return response

    if not buffer:
        raise TimeoutError(
            f"No Blender MCP response from {host}:{port} within {timeout_seconds:.1f}s"
        )
    raise RuntimeError("Blender MCP connection closed with an incomplete JSON response")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout", type=float, default=600.0)

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("scene-info")

    object_parser = subparsers.add_parser("object-info")
    object_parser.add_argument("--name", required=True)

    execute_parser = subparsers.add_parser("execute-file")
    execute_parser.add_argument("--file", required=True, type=Path)

    screenshot_parser = subparsers.add_parser("viewport-screenshot")
    screenshot_parser.add_argument("--file", required=True, type=Path)
    screenshot_parser.add_argument("--max-size", type=int, default=1024)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "scene-info":
        command_type = "get_scene_info"
        params: dict[str, Any] = {}
    elif args.command == "object-info":
        command_type = "get_object_info"
        params = {"name": args.name}
    elif args.command == "execute-file":
        source_path = args.file.resolve()
        if not source_path.is_file():
            raise FileNotFoundError(f"Blender code file does not exist: {source_path}")
        command_type = "execute_code"
        source = source_path.read_text(encoding="utf-8")
        bootstrap = (
            "exec(compile("
            f"{source!r}, {str(source_path)!r}, 'exec'), "
            "{'__name__': '__main__', "
            f"'__file__': {str(source_path)!r}, "
            "'bpy': bpy})"
        )
        params = {"code": bootstrap}
    elif args.command == "viewport-screenshot":
        output_path = args.file.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        command_type = "get_viewport_screenshot"
        params = {
            "max_size": args.max_size,
            "filepath": str(output_path),
            "format": "png",
        }
    else:  # pragma: no cover - argparse makes this unreachable
        raise AssertionError(args.command)

    response = send_command(
        command_type,
        params,
        host=args.host,
        port=args.port,
        timeout_seconds=args.timeout,
    )
    json.dump(response, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if response.get("status") == "success" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        json.dump(
            {"status": "error", "message": f"{type(exc).__name__}: {exc}"},
            sys.stderr,
            ensure_ascii=False,
            indent=2,
        )
        sys.stderr.write("\n")
        raise SystemExit(3)
