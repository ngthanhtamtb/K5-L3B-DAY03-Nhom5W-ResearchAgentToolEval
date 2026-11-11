"""Streamlit UI for the Research Agent.

Run:
    streamlit run app.py
Deploy (Streamlit Community Cloud): put the keys from .env into the app's Secrets;
they are copied into environment variables at start-up.

The agent runs in-process with the same model -> tool loop as chat.py / server.py,
and every conversation is saved as a transcript in transcripts/ (channel = "streamlit").
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import ARTIFACTS_DIR, ROOT, now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
PROVIDERS = ["gemini", "openrouter", "openai", "anthropic", "ollama"]
EXAMPLES = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Trên Hacker News dân dev đang bàn gì về LLM?",
    "Tìm 5 repo GitHub về agentic AI viết bằng Python nhiều sao nhất",
    "Tìm paper arXiv mới về AI agent evaluation",
    "Theo policy công ty, tweet viral có được coi là fact đã xác nhận không?",
    "Tóm tắt bài này giúp mình: https://www.anthropic.com/research",
]
TOOL_ICONS = {
    "clarify": "❓", "timeline": "🐦", "social_search": "🐦", "lookup": "🌐", "fetch": "📄", "format": "📝",
    "send": "📤", "policy": "📘", "papers": "📚", "paper_text": "📚", "hackernews_search": "🟧", "github_search": "🐙",
}


# ---------------- setup ----------------
def copy_streamlit_secrets_to_env() -> None:
    """On Streamlit Cloud there is no .env file; keys live in st.secrets."""
    try:
        for key, value in st.secrets.items():
            if isinstance(value, str) and key not in os.environ:
                os.environ[key] = value
    except Exception:  # no secrets.toml locally - .env was already loaded by chat.py
        pass


@st.cache_resource(show_spinner=False)
def get_provider(name: str) -> Any:
    return make_provider(name)


def load_artifacts(today_hint: bool) -> tuple[str, list[dict[str, Any]], str]:
    """Read prompt + tools on every run so edits to the artifacts show up without restarting."""
    suffix = f"\n\nToday's date is {date.today().isoformat()}." if today_hint else ""
    prompt = PROMPT_PATH.read_text(encoding="utf-8") + suffix
    declarations = load_tool_declarations(TOOLS_PATH)
    return prompt, declarations, suffix


def init_state() -> None:
    st.session_state.setdefault("messages", [])      # what the UI renders
    st.session_state.setdefault("history", [])       # what the model sees (user/assistant text)
    st.session_state.setdefault("transcript", None)
    st.session_state.setdefault("transcript_path", None)
    st.session_state.setdefault("pending", None)     # text queued by an example / yes-no button


def reset_conversation() -> None:
    for key in ("messages", "history", "transcript", "transcript_path", "pending"):
        st.session_state.pop(key, None)
    init_state()


def ensure_transcript(config: dict[str, Any], artifact_version: Any, suffix: str) -> None:
    current = st.session_state.transcript
    signature = [config["provider"], config["model"], artifact_version.artifact_version]
    if current and current.get("_signature") == signature:
        return
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(config["version"]), safe_slug(config["provider"]), "streamlit", timestamp])
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        "channel": "streamlit",
        **artifact_version_dict(artifact_version),
        "provider": config["provider"],
        "model": config["model"],
        "system_prompt": str(PROMPT_PATH),
        "system_prompt_suffix": suffix,
        "tools": str(TOOLS_PATH),
        "history_window": config["history_window"],
        "max_tool_rounds": config["max_tool_rounds"],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
        "_signature": signature,
    }
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"


def save_transcript() -> None:
    transcript = {k: v for k, v in st.session_state.transcript.items() if not k.startswith("_")}
    write_transcript(Path(st.session_state.transcript_path), transcript)


# ---------------- rendering ----------------
def render_tool_events(events: list[dict[str, Any]]) -> None:
    for event in events:
        name = event.get("tool", "?")
        result = event.get("result") or {}
        if isinstance(result, dict) and result.get("awaiting_user"):
            continue  # the question itself is shown as the assistant reply
        args = json.dumps(event.get("args", {}), ensure_ascii=False, sort_keys=True)
        has_error = isinstance(result, dict) and result.get("error")
        label = f"{TOOL_ICONS.get(name, '🔧')} {name}({args})"
        with st.expander(("⚠️ " if has_error else "") + label, expanded=False):
            if has_error:
                st.error(f"{result.get('error')}: {result.get('message')}")
                continue
            items = result.get("items") if isinstance(result, dict) else None
            if items:
                for item in items:
                    title = item.get("title") or item.get("text") or "(không có tiêu đề)"
                    url = item.get("url") or ""
                    head = f"**[{title}]({url})**" if url else f"**{title}**"
                    summary = str(item.get("summary") or item.get("description") or "")[:300]
                    st.markdown(f"- {head}  \n  {summary}" if summary else f"- {head}")
            elif isinstance(result, dict) and result.get("markdown"):
                st.markdown(result["markdown"])
            else:
                st.json(result, expanded=False)


def render_message(message: dict[str, Any], show_tools: bool) -> None:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🔎"):
        if message["role"] == "assistant" and show_tools and message.get("tool_events"):
            render_tool_events(message["tool_events"])
        status = message.get("status")
        if status == "provider_error":
            st.error(message["content"])
        elif status == "waiting_for_user":
            st.info(f"❓ {message['content']}")
        elif status == "max_tool_rounds":
            st.warning(message["content"])
        else:
            st.markdown(message["content"])


def pending_clarify() -> dict[str, Any] | None:
    """If the last assistant turn is a clarify question, return its result (response_type/options)."""
    if not st.session_state.messages:
        return None
    last = st.session_state.messages[-1]
    if last["role"] != "assistant" or last.get("status") != "waiting_for_user":
        return None
    for event in reversed(last.get("tool_events", [])):
        result = event.get("result") or {}
        if isinstance(result, dict) and result.get("awaiting_user"):
            return result
    return None


def render_quick_replies() -> None:
    clarify = pending_clarify()
    if not clarify:
        return
    if clarify.get("response_type") == "yes_no":
        col_yes, col_no, _ = st.columns([1, 1, 4])
        if col_yes.button("✅ Có, đồng ý", use_container_width=True):
            st.session_state.pending = "Có, mình xác nhận."
            st.rerun()
        if col_no.button("❌ Không", use_container_width=True):
            st.session_state.pending = "Không, đừng gửi."
            st.rerun()
    elif clarify.get("response_type") == "choice" and clarify.get("options"):
        cols = st.columns(len(clarify["options"]))
        for col, option in zip(cols, clarify["options"]):
            if col.button(option, use_container_width=True):
                st.session_state.pending = option
                st.rerun()


# ---------------- agent turn ----------------
def run_turn(user_text: str, config: dict[str, Any], system_prompt: str, openai_tools: list[dict[str, Any]]) -> None:
    st.session_state.messages.append({"role": "user", "content": user_text})
    render_message(st.session_state.messages[-1], config["show_tools"])

    transcript = st.session_state.transcript
    turn: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, config["history_window"]),
        {"role": "user", "content": user_text},
    ]
    with st.chat_message("assistant", avatar="🔎"):
        with st.spinner("Agent đang chọn tool và tra cứu..."):
            try:
                result = run_model_tool_loop(
                    provider=get_provider(config["provider"]),
                    messages=messages,
                    tools=openai_tools,
                    model=config["model"] or None,
                    max_tool_rounds=config["max_tool_rounds"],
                )
                turn.update(result)
                reply, status = result["assistant_text"], result["status"]
                st.session_state.history += [
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": reply},
                ]
            except Exception as exc:
                reply, status = f"{type(exc).__name__}: {exc}", "provider_error"
                turn.update({"status": status, "error": reply})

    turn["ended_at"] = now_iso()
    transcript["turns"].append(turn)
    save_transcript()
    st.session_state.messages.append({
        "role": "assistant", "content": reply, "status": status, "tool_events": turn.get("tool_events", []),
    })
    st.rerun()


# ---------------- page ----------------
def main() -> None:
    st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")
    copy_streamlit_secrets_to_env()
    init_state()

    with st.sidebar:
        st.header("⚙️ Cấu hình")
        provider = st.selectbox("Provider", PROVIDERS, index=0)
        model = st.text_input("Model (để trống = mặc định)", value="")
        version = st.text_input("Version label", value="v5")
        today_hint = st.toggle("Cho model biết ngày hôm nay", value=True,
                               help="Thêm 'Today's date is …' vào cuối system prompt để điền date_from / created_after.")
        show_tools = st.toggle("Hiện tool call & kết quả", value=True)
        history_window = st.slider("Số lượt nhớ (history window)", 0, 10, 5)
        max_tool_rounds = st.slider("Số vòng tool tối đa / lượt", 1, 6, 4)
        if st.button("🗑️ Cuộc trò chuyện mới", use_container_width=True):
            reset_conversation()
            st.rerun()

    config = {
        "provider": provider, "model": model.strip(), "version": version.strip() or "ui",
        "show_tools": show_tools, "history_window": history_window, "max_tool_rounds": max_tool_rounds,
    }

    try:
        system_prompt, declarations, suffix = load_artifacts(today_hint)
        openai_tools = to_openai_tools(declarations)
        artifact_version = build_artifact_version(config["version"], PROMPT_PATH, TOOLS_PATH)
    except Exception as exc:
        st.error(f"Không đọc được artifacts: {exc}")
        st.stop()

    try:
        provider_obj = get_provider(provider)
        config["model"] = config["model"] or getattr(provider_obj, "default_model", "") or ""
    except Exception as exc:
        st.error(f"Không khởi tạo được provider '{provider}': {exc}")
        st.stop()
    ensure_transcript(config, artifact_version, suffix)

    with st.sidebar:
        st.divider()
        st.caption(f"**artifact_version**: `{artifact_version.artifact_version}`")
        st.caption(f"**model**: `{config['model']}`")
        if st.session_state.transcript_path:
            st.caption(f"**transcript**: `{Path(st.session_state.transcript_path).name}`")
        with st.expander(f"🧰 {len(declarations)} tools"):
            for item in declarations:
                desc = " ".join(item.get("description", "").split())
                st.markdown(f"{TOOL_ICONS.get(item['name'], '🔧')} **{item['name']}** — {desc[:140]}…")

    st.title("🔎 Research Agent")
    st.caption("Tin tức AI/tech · Twitter/X · Hacker News · GitHub · arXiv · Policy nội bộ — mọi tool call đều được log vào transcript.")

    if not st.session_state.messages:
        st.markdown("**Thử một câu hỏi mẫu:**")
        cols = st.columns(3)
        for index, example in enumerate(EXAMPLES):
            if cols[index % 3].button(example, key=f"example_{index}", use_container_width=True):
                st.session_state.pending = example
                st.rerun()

    for message in st.session_state.messages:
        render_message(message, show_tools)
    render_quick_replies()

    typed = st.chat_input("Hỏi agent… (ví dụ: 10 tweet mới nhất của Elon Musk)")
    user_text = typed or st.session_state.pending
    st.session_state.pending = None
    if user_text:
        run_turn(user_text.strip(), config, system_prompt, openai_tools)


main()
