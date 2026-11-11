"""Local backend simulation for the Research Agent.

Wraps the same model -> tool loop as chat.py behind a small JSON HTTP API so a CLI
(cli_client.py) or a UI (Streamlit / Vercel) can talk to it like a real backend.
Standard library only - no extra dependency.

Run:
    python server.py --provider gemini --version v3 --port 8000

Endpoints:
    GET  /health                 -> status, artifact_version, provider, model, tool names
    GET  /tools                  -> declared tools (name + description)
    POST /chat   {"message": "...", "session_id": "optional"}
                                 -> {"session_id", "status", "reply", "tool_calls", "tool_results", ...}
    POST /reset  {"session_id": "..."}
    GET  /sessions/<session_id>  -> full transcript of that session

Every session writes a transcript in the same format as chat.py to transcripts/,
so backend conversations count as transcript evidence too.
"""
from __future__ import annotations

import argparse
import json
import threading
import uuid
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from chat import ARTIFACTS_DIR, ROOT, now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


class AgentBackend:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        base_prompt = args.system_prompt.read_text(encoding="utf-8")
        self.prompt_suffix = ""
        if args.today_hint:
            # Lets the model turn "tuần này" / "năm nay" into date_from / created_after values.
            self.prompt_suffix = f"\n\nToday's date is {date.today().isoformat()}."
        self.system_prompt = base_prompt + self.prompt_suffix
        self.declarations = load_tool_declarations(args.tools)
        self.openai_tools = to_openai_tools(self.declarations)
        self.provider = make_provider(args.provider)
        self.model = args.model or getattr(self.provider, "default_model", None)
        self.artifact_version = build_artifact_version(args.version, args.system_prompt, args.tools)
        self.sessions: dict[str, dict[str, Any]] = {}
        self.lock = threading.Lock()

    # ---------------- sessions ----------------
    def _new_session(self, session_id: str | None = None) -> dict[str, Any]:
        session_id = session_id or uuid.uuid4().hex[:12]
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([safe_slug(self.args.version), safe_slug(self.args.provider), "backend", timestamp])
        session = {
            "id": session_id,
            "history": [],
            "lock": threading.Lock(),
            "path": self.args.transcripts_dir / f"{transcript_id}.transcript.json",
            "transcript": {
                "transcript_id": transcript_id,
                "session_id": session_id,
                "channel": "backend",
                **artifact_version_dict(self.artifact_version),
                "provider": self.args.provider,
                "model": self.model,
                "system_prompt": str(self.args.system_prompt),
                "system_prompt_suffix": self.prompt_suffix,
                "tools": str(self.args.tools),
                "history_window": self.args.history_window,
                "max_tool_rounds": self.args.max_tool_rounds,
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "turns": [],
            },
        }
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str | None) -> dict[str, Any]:
        with self.lock:
            if session_id and session_id in self.sessions:
                return self.sessions[session_id]
            return self._new_session(session_id)

    def reset(self, session_id: str) -> bool:
        with self.lock:
            return self.sessions.pop(session_id, None) is not None

    # ---------------- chat ----------------
    def chat(self, message: str, session_id: str | None) -> dict[str, Any]:
        session = self.get_session(session_id)
        with session["lock"]:  # one turn at a time per session
            history = session["history"]
            transcript = session["transcript"]
            turn_index = len(transcript["turns"]) + 1
            messages = [
                {"role": "system", "content": self.system_prompt},
                *trim_history(history, self.args.history_window),
                {"role": "user", "content": message},
            ]
            turn: dict[str, Any] = {
                "turn_index": turn_index,
                "started_at": now_iso(),
                "user": message,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }
            try:
                result = run_model_tool_loop(
                    provider=self.provider,
                    messages=messages,
                    tools=self.openai_tools,
                    model=self.args.model,
                    max_tool_rounds=self.args.max_tool_rounds,
                )
                turn.update(result)
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": result["assistant_text"]})
            except Exception as exc:  # provider/network errors are returned, not raised
                turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
            turn["ended_at"] = now_iso()
            transcript["turns"].append(turn)
            write_transcript(session["path"], transcript)

        return {
            "session_id": session["id"],
            "turn_index": turn_index,
            "status": turn["status"],
            "reply": turn.get("assistant_text") or turn.get("error", ""),
            "tool_calls": [call for rnd in turn.get("rounds", []) for call in rnd.get("tool_calls", [])],
            "tool_results": turn.get("tool_events", []),
            "rounds": len(turn.get("rounds", [])),
            "artifact_version": self.artifact_version.artifact_version,
            "transcript": str(session["path"]),
        }


def make_handler(backend: AgentBackend) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, payload: Any) -> None:
            body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        def _body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length") or 0)
            if not length:
                return {}
            return json.loads(self.rfile.read(length).decode("utf-8"))

        def do_OPTIONS(self) -> None:  # CORS preflight for a browser UI
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self) -> None:
            if self.path == "/health":
                return self._send(200, {
                    "status": "ok",
                    "artifact_version": backend.artifact_version.artifact_version,
                    "provider": backend.args.provider,
                    "model": backend.model,
                    "tools": [item["name"] for item in backend.declarations],
                    "sessions": len(backend.sessions),
                })
            if self.path == "/tools":
                return self._send(200, [
                    {"name": item["name"], "description": item.get("description", "")} for item in backend.declarations
                ])
            if self.path.startswith("/sessions/"):
                session = backend.sessions.get(self.path.split("/", 2)[2])
                if not session:
                    return self._send(404, {"error": "session not found"})
                return self._send(200, session["transcript"])
            return self._send(404, {"error": f"unknown path {self.path}"})

        def do_POST(self) -> None:
            try:
                body = self._body()
            except json.JSONDecodeError:
                return self._send(400, {"error": "body must be JSON"})
            if self.path == "/chat":
                message = str(body.get("message") or "").strip()
                if not message:
                    return self._send(400, {"error": "'message' is required"})
                return self._send(200, backend.chat(message, body.get("session_id")))
            if self.path == "/reset":
                return self._send(200, {"reset": backend.reset(str(body.get("session_id") or ""))})
            return self._send(404, {"error": f"unknown path {self.path}"})

        def log_message(self, fmt: str, *args: Any) -> None:
            print(f"[{now_iso()}] {self.address_string()} {fmt % args}")

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Local JSON backend for the Research Agent.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini", "ollama"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True, help="Artifact version label, e.g. v3.")
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-today-hint", dest="today_hint", action="store_false",
                        help="Do not append today's date to the system prompt.")
    args = parser.parse_args()

    backend = AgentBackend(args)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(backend))
    print(f"Research Agent backend on http://{args.host}:{args.port}")
    print(f"artifact_version={backend.artifact_version.artifact_version} provider={args.provider} model={backend.model}")
    print(f"tools={[item['name'] for item in backend.declarations]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
