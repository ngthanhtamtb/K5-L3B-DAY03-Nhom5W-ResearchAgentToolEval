"""CLI client that chats with the local backend (server.py) over HTTP.

Run the backend first:
    python server.py --provider gemini --version v3
Then in another terminal:
    python cli_client.py                 # default http://127.0.0.1:8000
    python cli_client.py --debug         # also print tool args + short tool results

Commands inside the chat:
    /tools   list tools the backend exposes
    /debug   toggle printing tool results
    /reset   start a new session (clears conversation memory)
    /session show the current session id and transcript path
    /exit    quit
"""
from __future__ import annotations

import argparse
import json
from typing import Any

import requests


def short(value: Any, limit: int = 300) -> str:
    text = json.dumps(value, ensure_ascii=False, default=str)
    return text if len(text) <= limit else text[:limit] + "…"


def print_tool_results(results: list[dict[str, Any]]) -> None:
    for event in results:
        result = event.get("result") or {}
        if isinstance(result, dict) and result.get("error"):
            print(f"   ✗ {event.get('tool')}: {result.get('error')} - {str(result.get('message'))[:200]}")
            continue
        items = result.get("items") if isinstance(result, dict) else None
        if items is not None:
            print(f"   ✓ {event.get('tool')}: {len(items)} item(s)")
            for item in items[:5]:
                title = item.get("title") or item.get("text") or ""
                print(f"     - {str(title)[:90]}  {item.get('url') or ''}")
        else:
            print(f"   ✓ {event.get('tool')}: {short(result)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the Research Agent backend.")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    base = args.url.rstrip("/")
    debug = args.debug

    try:
        health = requests.get(f"{base}/health", timeout=10).json()
    except requests.RequestException as exc:
        raise SystemExit(f"Cannot reach backend at {base}: {exc}\nStart it with: python server.py --provider gemini --version v3")
    print(f"Connected to {base}  artifact_version={health['artifact_version']}  model={health['model']}")
    print("Type /tools, /debug, /reset, /session or /exit.")

    session_id: str | None = None
    transcript_path = ""
    while True:
        try:
            text = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text in {"/exit", "/quit"}:
            break
        if text == "/debug":
            debug = not debug
            print(f"debug = {debug}")
            continue
        if text == "/tools":
            for tool in requests.get(f"{base}/tools", timeout=10).json():
                print(f" • {tool['name']}: {' '.join(tool['description'].split())[:110]}")
            continue
        if text == "/session":
            print(f"session_id={session_id}  transcript={transcript_path or '-'}")
            continue
        if text == "/reset":
            if session_id:
                requests.post(f"{base}/reset", json={"session_id": session_id}, timeout=10)
            session_id, transcript_path = None, ""
            print("New session.")
            continue

        try:
            response = requests.post(
                f"{base}/chat", json={"message": text, "session_id": session_id}, timeout=args.timeout,
            )
            data = response.json()
        except requests.RequestException as exc:
            print(f"ERROR> {exc}")
            continue
        if response.status_code != 200:
            print(f"ERROR> {data}")
            continue

        session_id = data["session_id"]
        transcript_path = data.get("transcript", "")
        for call in data.get("tool_calls", []):
            print(f"🔧 {call['name']}({json.dumps(call['args'], ensure_ascii=False, sort_keys=True)})")
        if debug:
            print_tool_results(data.get("tool_results", []))
        marker = {"waiting_for_user": "❓", "provider_error": "⚠️", "max_tool_rounds": "⏹"}.get(data["status"], "")
        print(f"\nAgent> {marker + ' ' if marker else ''}{data['reply']}")


if __name__ == "__main__":
    main()
