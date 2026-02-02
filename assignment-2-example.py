from __future__ import annotations

from datetime import date
import random
import re
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# TODO for instructor: paste your key here if you want LLM advice.
OPENAI_API_KEY = ""  # e.g., "sk-..."


APP_TITLE = "🧘 Daily Anxiety Tracker Bot"


def today_str() -> str:
    return date.today().isoformat()


def append_history(role: str, content: str) -> None:
    st.session_state.history.append({"role": role, "content": content})


def render_history() -> None:
    for m in st.session_state.history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])


def parse_level(user_text: str) -> int | None:
    """
    Accept:
      - "7"
      - "7/10"
      - "log 7"
      - "anxiety 7"
      - "level 7"
    """
    t = user_text.strip().lower()
    m = re.match(r"^(?:(?:log|anxiety|level)\s*)?(\d{1,2})(?:\s*/\s*10)?\s*$", t)
    if not m:
        return None
    return int(m.group(1))


def valid_level(level: int) -> bool:
    return 1 <= level <= 10


def rule_smalltalk(user_text: str) -> str | None:
    """
    If user greets or expresses general feelings, respond and guide back to logging anxiety.
    This makes the bot feel more natural but stays beginner-friendly.
    """
    t = user_text.strip().lower()

    greetings = {"hi", "hello", "hey", "hi there", "good morning", "good afternoon", "good evening"}
    if t in greetings:
        return random.choice([
            "Hi! Let’s do a quick check-in. What’s your anxiety level today (**1–10**)?",
            "Hello! Please rate your anxiety today from **1 to 10** (just type a number).",
            "Hey there! On a scale of **1–10**, how anxious do you feel today?"
        ])

    # Simple mood phrases (not diagnosing, just acknowledging)
    if any(p in t for p in ["i feel", "i am feeling", "today i feel"]):
        return (
            "Thanks for sharing. I can help you track anxiety with one number.\n\n"
            "Please rate your anxiety today from **1 to 10** (example: `6`)."
        )

    # Workload signals (still guiding back)
    if any(w in t for w in ["deadline", "exam", "assignment", "due", "quiz"]):
        return (
            "Deadlines can definitely raise anxiety.\n\n"
            "To log today’s check-in, please enter your anxiety level **1–10**."
        )

    return None


def rule_feedback(level: int) -> str:
    """
    Rule-based feedback after logging.
    Keep it short, supportive, and non-clinical.
    """
    if 1 <= level <= 3:
        return (
            "You’re doing a good job checking in. Anxiety seems relatively low today.\n\n"
            "Try a tiny maintenance step: take **3 slow breaths**, then pick one small thing you want to keep going."
        )
    if 4 <= level <= 6:
        return (
            "Thanks for logging. Moderate anxiety can feel distracting.\n\n"
            "Try a quick reset: name **5 things you see**, **4 you feel**, **3 you hear**, **2 you smell**, **1 you taste**."
        )
    if 7 <= level <= 8:
        return (
            "That sounds tough. When anxiety is high, lowering the load can help.\n\n"
            "Try: **2 minutes of slow breathing**, then choose **one tiny task** you can finish in 10 minutes."
        )
    # 9–10
    return (
        "I’m sorry you’re feeling this intensely. You deserve support right now.\n\n"
        "Focus on immediate safety and calming (slow breathing, move to a quieter place if possible).\n"
        "If you feel unsafe or at risk of harming yourself, please contact local emergency services or a crisis hotline in your area."
    )


def llm_advice(level: int, note: str | None) -> str:
    """
    LLM advice called AFTER saving the log.
    If OPENAI_API_KEY is empty or OpenAI SDK is missing, return a helpful message.
    """
    if not OPENAI_API_KEY:
        return "LLM advice is unavailable because no API key was provided in the code."
    if OpenAI is None:
        return "LLM advice is unavailable because the `openai` package is not installed."

    client = OpenAI(api_key=OPENAI_API_KEY)

    system = (
        "You are a supportive, non-clinical wellbeing coach. "
        "You do not diagnose. Keep the response concise. "
        "If anxiety is 9-10, include a brief safety note encouraging professional support."
    )

    user = (
        f"User logged anxiety: {level}/10.\n"
        f"Optional note: {note if note else '(none)'}\n\n"
        "Give:\n"
        "1) One-sentence validation\n"
        "2) Three bullet points (quick coping step <=1 min, small next action <=10 min, reflection question)\n"
        "3) End with: This is not medical advice."
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.6,
    )
    return resp.choices[0].message.content


def format_history(log: list[dict], limit: int = 3) -> str:
    if not log:
        return "No history yet. Start by typing a number **1–10**."
    recent = log[-limit:]
    lines = ["Your most recent check-ins:"]
    for item in recent:
        lines.append(f"- {item['date']}: {item['level']}/10")
    return "\n".join(lines)


# -------------------- App UI --------------------

st.set_page_config(page_title="Daily Anxiety Tracker", page_icon="🧘")
st.title(APP_TITLE)

if st.button("Clear chat"):
    for k in ["history", "stage", "today_level", "today_note", "anxiety_log"]:
        st.session_state.pop(k, None)
    st.rerun()

# State init
if "history" not in st.session_state:
    st.session_state.history = [
        {
            "role": "assistant",
            "content": (
                "Hi! Let’s do a quick daily check-in.\n\n"
                "**Step 1:** Rate your anxiety today from **1 to 10**.\n"
                "Type a number like `6`."
            ),
        }
    ]

if "stage" not in st.session_state:
    # ASK_LEVEL -> ASK_NOTE -> DONE
    st.session_state.stage = "ASK_LEVEL"

if "today_level" not in st.session_state:
    st.session_state.today_level = None

if "today_note" not in st.session_state:
    st.session_state.today_note = None

if "anxiety_log" not in st.session_state:
    st.session_state.anxiety_log = []  # {"date":..., "level":..., "note":...}

render_history()

user_text = st.chat_input("Type here (try: 6, log 6, help, today, history, advice)")

if user_text:
    append_history("user", user_text)
    with st.chat_message("user"):
        st.markdown(user_text)

    cmd = user_text.strip().lower()

    # Lightweight commands (available anytime)
    if cmd == "help":
        reply = (
            "Commands:\n\n"
            "- Type a number `1–10` (or `log 6`) to start a check-in\n"
            "- `today` show today’s saved check-in\n"
            "- `history` show last 3 check-ins\n"
            "- `advice` regenerate LLM advice (if API key is set)\n"
            "- `help`"
        )
        append_history("assistant", reply)
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.stop()

    if cmd == "today":
        today = today_str()
        todays = [x for x in st.session_state.anxiety_log if x["date"] == today]
        if not todays:
            reply = "No check-in saved for today yet. Type a number **1–10** to start."
        else:
            last = todays[-1]
            reply = f"Today ({today}) you logged **{last['level']}/10**. Note: {last['note'] or '(none)'}"
        append_history("assistant", reply)
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.stop()

    if cmd == "history":
        reply = format_history(st.session_state.anxiety_log, limit=3)
        append_history("assistant", reply)
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.stop()

    # Stage machine
    if st.session_state.stage == "ASK_LEVEL":
        # richer rule-based entry: handle greetings / mood / deadline
        maybe = rule_smalltalk(user_text)
        if maybe is not None:
            reply = maybe
        else:
            level = parse_level(user_text)
            if level is None:
                reply = "Please enter a number from **1 to 10** (example: `7`)."
            elif not valid_level(level):
                reply = "That number is out of range. Please enter **1–10**."
            else:
                st.session_state.today_level = level
                st.session_state.stage = "ASK_NOTE"
                reply = (
                    f"Saved: today’s anxiety level is **{level}/10**.\n\n"
                    "Optional: add one short note about why (or type `skip`)."
                )

        append_history("assistant", reply)
        with st.chat_message("assistant"):
            st.markdown(reply)

    elif st.session_state.stage == "ASK_NOTE":
        note = user_text.strip()
        if note.lower() == "skip":
            st.session_state.today_note = None
        else:
            st.session_state.today_note = note[:200]

        # Save log (end of rule-based stage)
        entry = {"date": today_str(), "level": st.session_state.today_level, "note": st.session_state.today_note}
        st.session_state.anxiety_log.append(entry)

        rb = "### Rule-based feedback\n\n" + rule_feedback(entry["level"])
        llm = "### LLM-based advice\n\n" + llm_advice(entry["level"], entry["note"])

        reply = "✅ Check-in saved.\n\n" + rb + "\n\n" + llm
        st.session_state.stage = "DONE"

        append_history("assistant", reply)
        with st.chat_message("assistant"):
            st.markdown(reply)

    else:
        # DONE stage: allow advice regeneration or restart
        if cmd == "advice":
            if st.session_state.today_level is None:
                reply = "No level found. Type a number **1–10** to start."
                st.session_state.stage = "ASK_LEVEL"
            else:
                reply = "### LLM-based advice\n\n" + llm_advice(st.session_state.today_level, st.session_state.today_note)
        else:
            # If they type a number, restart new check-in
            maybe_level = parse_level(user_text)
            if maybe_level is not None:
                st.session_state.stage = "ASK_LEVEL"
                st.session_state.today_level = None
                st.session_state.today_note = None
                reply = "Starting a new check-in. Please enter today’s anxiety level **1–10**."
            else:
                reply = "Type `help` for commands, or type a number **1–10** to start a new check-in."

        append_history("assistant", reply)
        with st.chat_message("assistant"):
            st.markdown(reply)
