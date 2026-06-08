from __future__ import annotations

import json
import random
import sqlite3
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
BANK_PATH = APP_DIR / "question_bank.json"
DB_PATH = APP_DIR / "progress.sqlite3"
LETTERS = "abcde"
USER_ID = "local_guest"

st.set_page_config(
    page_title="International Taxation — Exam Practice",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
<style>
:root {
  --bg: #070b10;
  --bg-soft: #0d131c;
  --panel: rgba(14,20,29,0.86);
  --border: #1e2d3d;
  --border-strong: #2a3f55;
  --text: #eef4fb;
  --muted: #7b9ab5;
  --accent: #5bafd6;
  --accent2: #7ecfc0;
  --warn: #e8b84b;
  --ok: #6dc993;
  --fail: #e06060;
}
.stApp {
  background: radial-gradient(circle at 10% 10%, rgba(91,175,214,.13) 0%, transparent 30%),
              linear-gradient(180deg, #0c1520 0%, #070b10 60%);
  color: var(--text);
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#0b1219 0%,#08101a 100%);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
.block-container { max-width: 900px; padding-top: 1.2rem; padding-bottom: 2.5rem; }

.hero {
  background: linear-gradient(135deg, rgba(91,175,214,.14) 0%, rgba(126,207,192,.08) 100%);
  border: 1px solid var(--border-strong);
  border-radius: 18px;
  padding: 1.4rem 1.6rem;
  margin-bottom: 1rem;
}
.hero h1 { margin: 0 0 .4rem; font-size: 1.9rem; color: var(--text); }
.hero p { margin: 0; color: var(--muted); font-size: .95rem; line-height: 1.6; }

.section-head {
  font-size: .78rem; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; color: var(--accent); margin-bottom: .2rem;
}
.section-title { font-size: 1.55rem; font-weight: 700; color: var(--text); margin-bottom: .15rem; }
.section-sub { color: var(--muted); font-size: .9rem; margin-bottom: .8rem; }

.badge {
  display: inline-block; padding: .3rem .6rem;
  border-radius: 999px; border: 1px solid var(--border);
  background: rgba(22,31,44,.8); color: var(--text);
  font-size: .8rem; font-weight: 600; margin: 0 .35rem .35rem 0;
}
.badge.cool { background: rgba(91,175,214,.15); border-color: rgba(91,175,214,.35); color: #a8d8f0; }
.badge.ok { background: rgba(109,201,147,.15); border-color: rgba(109,201,147,.35); color: #a0e0bb; }
.badge.warn { background: rgba(232,184,75,.15); border-color: rgba(232,184,75,.35); color: #f0d080; }
.badge.fail { background: rgba(224,96,96,.15); border-color: rgba(224,96,96,.35); color: #f0a0a0; }

[data-testid="stMetric"] {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 14px; padding: .7rem .9rem;
}
[data-testid="stMetricValue"] { color: var(--text) !important; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; }
[data-testid="stMetricDelta"] { color: var(--ok) !important; }

[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 14px;
}

div[data-baseweb="radio"] > div label {
  background: rgba(17,25,36,.8); border: 1px solid var(--border);
  border-radius: 12px; padding: .65rem .8rem; margin-bottom: .4rem;
}
div[data-baseweb="radio"] > div label:hover {
  border-color: var(--accent); background: rgba(28,43,62,.9);
}
div[data-baseweb="radio"] > div label p { font-size: .95rem; color: var(--text) !important; }

[data-testid="stButton"] button,
[data-testid="stFormSubmitButton"] button {
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
  color: #03111d !important; border: none; border-radius: 12px;
  font-weight: 700; min-height: 2.6rem;
  box-shadow: 0 8px 20px rgba(10,22,34,.25);
}
[data-testid="stButton"] button:hover { background: linear-gradient(135deg,#7ecfe4 0%,#6de4d4 100%); transform: translateY(-1px); }
[data-testid="stButton"] button:disabled { background: rgba(60,80,100,.4); color: rgba(200,220,240,.5) !important; transform: none; }

[data-testid="stSelectbox"] label,
[data-testid="stRadio"] label { color: var(--text) !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background: rgba(14,22,34,.9); border-color: var(--border);
}

.q-card {
  background: rgba(14,20,29,.9); border: 1px solid var(--border-strong);
  border-radius: 16px; padding: 1.2rem 1.4rem; margin-bottom: .8rem;
}
.q-num { color: var(--muted); font-size: .8rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
.q-text { font-size: 1.05rem; line-height: 1.65; color: var(--text); margin-top: .3rem; }

.opt-row {
  padding: .65rem .9rem; border-radius: 11px; border: 1px solid var(--border);
  background: rgba(14,22,34,.8); margin-bottom: .4rem; font-size: .95rem; color: var(--text);
}
.opt-row.correct { border-color: rgba(109,201,147,.55); background: rgba(109,201,147,.12); }
.opt-row.selected { border-color: rgba(232,184,75,.5); background: rgba(232,184,75,.1); }
.opt-row.correct.selected { border-color: rgba(91,175,214,.55); background: rgba(91,175,214,.12); }

.tag { display: inline-block; padding: .14rem .42rem; border-radius: 999px;
  font-size: .72rem; font-weight: 700; border: 1px solid var(--border); color: var(--text); margin-right: .3rem; }
.tag.ok { border-color: rgba(109,201,147,.5); color: #a0e0bb; }
.tag.warn { border-color: rgba(232,184,75,.5); color: #f0d080; }
.tag.fail { border-color: rgba(224,96,96,.5); color: #f0a0a0; }

.expl-box {
  background: rgba(91,175,214,.08); border: 1px solid rgba(91,175,214,.22);
  border-radius: 12px; padding: .8rem 1rem; margin-top: .8rem;
  font-size: .9rem; line-height: 1.65; color: #c4dff0;
}

.prog-bar-bg {
  width: 100%; height: 6px; border-radius: 999px;
  background: rgba(15,25,36,.9); border: 1px solid rgba(30,45,61,.7);
  overflow: hidden; margin: .3rem 0;
}
.prog-bar-fill { height: 100%; border-radius: 999px; transition: width .3s; }
.prog-ok { background: linear-gradient(90deg,var(--ok),var(--accent2)); }
.prog-fail { background: linear-gradient(90deg,var(--fail),#c84040); }

.resume-box {
  border: 1px solid rgba(126,207,192,.3); background: rgba(126,207,192,.08);
  border-radius: 14px; padding: .9rem 1rem; margin-bottom: .8rem;
}

h1,h2,h3,h4,h5,h6 { color: var(--text); }
a { color: #8fcfef !important; }
</style>
        """,
        unsafe_allow_html=True,
    )


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


# ── AUTH ─────────────────────────────────────────────────────────────────────

def auth_configured() -> bool:
    return False

def get_user_id() -> str:
    return "guest"

def render_login_gate() -> None:
    pass


# ── DB ──────────────────────────────────────────────────────────────────────

def init_db() -> None:
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                user_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                correct_count INTEGER NOT NULL DEFAULT 0,
                incorrect_count INTEGER NOT NULL DEFAULT 0,
                last_result INTEGER,
                bookmarked INTEGER NOT NULL DEFAULT 0,
                first_seen_at TEXT,
                last_seen_at TEXT,
                PRIMARY KEY (user_id, question_id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS mcq_session (
                user_id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                mode TEXT NOT NULL,
                queue_json TEXT NOT NULL,
                current_index INTEGER NOT NULL DEFAULT 0,
                answers_json TEXT NOT NULL DEFAULT '{}',
                started_at TEXT NOT NULL
            )
        """)
        # migrate old schema if needed
        try:
            c.execute("SELECT user_id FROM progress LIMIT 1")
        except Exception:
            c.execute("ALTER TABLE progress ADD COLUMN user_id TEXT NOT NULL DEFAULT 'guest'")


def load_progress(uid: str) -> dict[str, dict]:
    with sqlite3.connect(DB_PATH) as c:
        c.row_factory = sqlite3.Row
        rows = c.execute("SELECT * FROM progress WHERE user_id=?", (uid,)).fetchall()
    return {r["question_id"]: dict(r) for r in rows}


def ensure_row(uid: str, qid: str) -> None:
    now = utc_now()
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            INSERT INTO progress (user_id, question_id, first_seen_at, last_seen_at)
            VALUES (?,?,?,?) ON CONFLICT(user_id, question_id) DO NOTHING
        """, (uid, qid, now, now))


def record_attempt(uid: str, qid: str, is_correct: bool) -> None:
    ensure_row(uid, qid)
    now = utc_now()
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            UPDATE progress SET
                attempts = attempts + 1,
                correct_count = correct_count + ?,
                incorrect_count = incorrect_count + ?,
                last_result = ?,
                last_seen_at = ?
            WHERE user_id=? AND question_id = ?
        """, (1 if is_correct else 0, 0 if is_correct else 1,
              1 if is_correct else 0, now, uid, qid))


def toggle_bookmark(uid: str, qid: str, val: bool) -> None:
    ensure_row(uid, qid)
    with sqlite3.connect(DB_PATH) as c:
        c.execute("UPDATE progress SET bookmarked=?, last_seen_at=? WHERE user_id=? AND question_id=?",
                  (1 if val else 0, utc_now(), uid, qid))


def save_session(uid: str, topic: str, mode: str, queue: list, idx: int, answers: dict, started: str) -> None:
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            INSERT INTO mcq_session (user_id, topic, mode, queue_json, current_index, answers_json, started_at)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
                topic=excluded.topic, mode=excluded.mode, queue_json=excluded.queue_json,
                current_index=excluded.current_index, answers_json=excluded.answers_json,
                started_at=excluded.started_at
        """, (uid, topic, mode, json.dumps(queue), idx, json.dumps(answers), started))


def load_session(uid: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as c:
        c.row_factory = sqlite3.Row
        row = c.execute("SELECT * FROM mcq_session WHERE user_id=?", (uid,)).fetchone()
    if not row:
        return None
    s = dict(row)
    s["queue"] = json.loads(s.pop("queue_json") or "[]")
    s["answers"] = json.loads(s.pop("answers_json") or "{}")
    s["current_index"] = max(0, int(s.get("current_index", 0) or 0))
    return s


def clear_session(uid: str) -> None:
    with sqlite3.connect(DB_PATH) as c:
        c.execute("DELETE FROM mcq_session WHERE user_id=?", (uid,))


def reset_topic_progress(uid: str, bank: list, topic: str) -> None:
    ids = [q["id"] for q in bank if q["topic"] == topic]
    if ids:
        with sqlite3.connect(DB_PATH) as c:
            c.execute(f"DELETE FROM progress WHERE user_id=? AND question_id IN ({','.join('?'*len(ids))})", [uid]+ids)


# ── BANK ────────────────────────────────────────────────────────────────────

@st.cache_data
def load_bank() -> list:
    if BANK_PATH.exists():
        return json.loads(BANK_PATH.read_text(encoding="utf-8"))
    return []


def option_letter(i: int) -> str:
    return LETTERS[i] if i < len(LETTERS) else str(i)


def choice_label(item: dict, letter: str) -> str:
    idx = LETTERS.index(letter) if letter in LETTERS else int(letter)
    opts = item.get("options", [])
    if idx < len(opts):
        return f"{letter.upper()}. {opts[idx]}"
    return letter.upper()


def pct(a: int, b: int) -> int:
    return round(100 * a / b) if b else 0


def has_failure(row: dict) -> bool:
    return row.get("incorrect_count", 0) > 0 and row.get("last_result") != 1


# ── TOPIC DASHBOARD ─────────────────────────────────────────────────────────

def render_home(bank: list, progress: dict, uid: str) -> None:
    st.markdown("""
<div class="hero">
  <h1>⚖️ International Taxation</h1>
  <p>156 questions · 5 years of past exams (2017–2025) · 13 topics<br>
  Practice by topic or simulate a full past exam year.</p>
</div>
""", unsafe_allow_html=True)

    # Global stats
    all_ids = {q["id"] for q in bank}
    seen = {qid: r for qid, r in progress.items() if qid in all_ids}
    n_seen = len(seen)
    n_correct = sum(1 for r in seen.values() if r.get("last_result") == 1)
    n_fail = sum(1 for r in seen.values() if has_failure(r))
    n_book = sum(1 for r in seen.values() if r.get("bookmarked"))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Questions seen", n_seen, delta=f"/ {len(bank)}")
    col2.metric("Last attempt ✓", n_correct)
    col3.metric("Outstanding ✗", n_fail)
    col4.metric("Bookmarked", n_book)

    st.markdown("---")

    # Resume active session
    session = load_session(uid)
    if session:
        total = len(session["queue"])
        done = len(session["answers"])
        pct_done = pct(done, total)
        st.markdown(f"""
<div class="resume-box">
<strong>Active session:</strong> {session['topic']} — {done}/{total} answered ({pct_done}%) &nbsp;&nbsp;
Mode: <em>{session['mode']}</em>
</div>
""", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        if r1.button("▶ Resume session", use_container_width=True):
            st.session_state.page = "quiz"
            st.rerun()
        if r2.button("✕ Discard session", use_container_width=True):
            clear_session(uid)
            st.rerun()

    tab_topics, tab_years = st.tabs(["📚 By topic", "📅 By year (exam simulation)"])

    with tab_topics:
        st.markdown('<div class="section-sub">Practise questions grouped by concept.</div>', unsafe_allow_html=True)
        topics = sorted({q["topic"] for q in bank})
        cols = st.columns(2)
        for i, topic in enumerate(topics):
            topic_qs = [q for q in bank if q["topic"] == topic]
            ids = {q["id"] for q in topic_qs}
            t_seen = [progress[qid] for qid in ids if qid in progress]
            n_t_seen = len(t_seen)
            n_t_ok = sum(1 for r in t_seen if r.get("last_result") == 1)
            n_t_fail = sum(1 for r in t_seen if has_failure(r))
            pct_ok = pct(n_t_ok, len(topic_qs))

            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{topic}**")
                    st.markdown(
                        f'<span class="badge cool">{len(topic_qs)} Qs</span>'
                        f'<span class="badge ok">{n_t_ok} ✓</span>'
                        f'<span class="badge fail">{n_t_fail} ✗</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"""
<div class="prog-bar-bg">
  <div class="prog-bar-fill prog-ok" style="width:{pct_ok}%"></div>
</div>
""", unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    if b1.button("Practice", key=f"all_{i}", use_container_width=True):
                        _start_session(bank, topic, "all", uid)
                    if b2.button("Unseen only" if n_t_seen < len(topic_qs) else "Failed only",
                                 key=f"uns_{i}", use_container_width=True):
                        mode = "unseen" if n_t_seen < len(topic_qs) else "failed"
                        _start_session(bank, topic, mode, uid)

    with tab_years:
        st.markdown('<div class="section-sub">Simulate a real past exam in order — questions as they appeared that year.</div>', unsafe_allow_html=True)
        years = sorted({q["year"] for q in bank})
        year_labels = {2017: "June 2017", 2018: "June 2018", 2019: "June 2019", 2024: "June 2024", 2025: "June 2025"}
        year_qs_count = {2017: 30, 2018: 30, 2019: 30, 2024: 30, 2025: 36}

        cols2 = st.columns(2)
        for i, year in enumerate(years):
            yr_qs = [q for q in bank if q["year"] == year]
            yr_seen = [progress[q["id"]] for q in yr_qs if q["id"] in progress]
            n_yr_ok = sum(1 for r in yr_seen if r.get("last_result") == 1)
            n_yr_fail = sum(1 for r in yr_seen if has_failure(r))
            n_yr_seen = len(yr_seen)
            pct_yr = pct(n_yr_ok, len(yr_qs))

            with cols2[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{year_labels.get(year, str(year))}**")
                    st.markdown(
                        f'<span class="badge cool">{len(yr_qs)} questions</span>'
                        f'<span class="badge ok">{n_yr_ok} ✓</span>'
                        f'<span class="badge fail">{n_yr_fail} ✗</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"""
<div class="prog-bar-bg">
  <div class="prog-bar-fill prog-ok" style="width:{pct_yr}%"></div>
</div>
""", unsafe_allow_html=True)
                    ya, yb, yc = st.columns(3)
                    if ya.button("Full exam", key=f"yr_all_{year}", use_container_width=True):
                        _start_session_year(bank, year, "all", uid)
                    if yb.button("Shuffled", key=f"yr_shuf_{year}", use_container_width=True):
                        _start_session_year(bank, year, "shuffle", uid)
                    if yc.button("Unseen", key=f"yr_uns_{year}", use_container_width=True):
                        _start_session_year(bank, year, "unseen", uid)


def _start_session(bank: list, topic: str, mode: str, uid: str = "guest") -> None:
    progress = load_progress(uid)
    topic_qs = [q for q in bank if q["topic"] == topic]

    if mode == "unseen":
        qs = [q for q in topic_qs if q["id"] not in progress]
    elif mode == "failed":
        qs = [q for q in topic_qs if q["id"] in progress and has_failure(progress[q["id"]])]
    elif mode == "bookmarked":
        qs = [q for q in bank if q["id"] in progress and progress[q["id"]].get("bookmarked")]
    else:
        qs = topic_qs

    if not qs:
        st.warning("No questions match that filter.")
        return

    random.shuffle(qs)
    queue = [q["id"] for q in qs]
    started = utc_now()
    save_session(uid, topic, mode, queue, 0, {}, started)
    st.session_state.page = "quiz"
    st.rerun()


def _start_session_year(bank: list, year: int, mode: str, uid: str = "guest") -> None:
    progress = load_progress(uid)
    yr_qs = [q for q in bank if q["year"] == year]

    if mode == "unseen":
        qs = [q for q in yr_qs if q["id"] not in progress]
    elif mode == "failed":
        qs = [q for q in yr_qs if q["id"] in progress and has_failure(progress[q["id"]])]
    elif mode == "shuffle":
        qs = yr_qs[:]
        random.shuffle(qs)
    else:
        qs = yr_qs  # original exam order

    if not qs:
        st.warning("No questions match that filter for this year.")
        return

    label = f"Exam {year}"
    queue = [q["id"] for q in qs]
    save_session(uid, label, mode, queue, 0, {}, utc_now())
    st.session_state.page = "quiz"
    st.rerun()


# ── QUIZ ─────────────────────────────────────────────────────────────────────

def render_quiz(bank: list, uid: str = "guest") -> None:
    bank_map = {q["id"]: q for q in bank}
    session = load_session(uid)

    if not session:
        st.warning("No active session. Return to the dashboard.")
        if st.button("← Home"):
            st.session_state.page = "home"
            st.rerun()
        return

    queue = session["queue"]
    answers = session["answers"]
    idx = session["current_index"]
    total = len(queue)

    if idx >= total:
        _render_session_summary(queue, answers, bank_map, uid)
        return

    qid = queue[idx]
    item = bank_map.get(qid)
    if not item:
        st.error(f"Question {qid} not found.")
        return

    progress = load_progress(uid)

    # ── Header ──
    pct_done = pct(idx, total)
    st.markdown(
        f'<div class="section-head">{item["topic"].upper()}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f"**Question {idx+1} of {total}** — Year: {item['year']}")
    st.progress(pct_done / 100)

    already_answered = qid in answers

    # ── Question card ──
    st.markdown(
        f'<div class="q-card">'
        f'<div class="q-num">Q{idx+1} · {item["year"]}</div>'
        f'<div class="q-text">{item["question"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if already_answered:
        ans = answers[qid]
        selected = set(ans.get("selected_letters", []))
        correct_letters = set(item.get("answer_letters", []))
        is_correct = ans.get("is_correct", False)

        # Show options with colour coding
        for li, opt in enumerate(item.get("options", [])):
            letter = option_letter(li)
            classes = "opt-row"
            tags = ""
            if letter in correct_letters:
                classes += " correct"
                tags += '<span class="tag ok">✓ Correct</span>'
            if letter in selected:
                if letter not in correct_letters:
                    classes += " selected"
                    tags += '<span class="tag fail">✗ Your answer</span>'
                else:
                    tags += '<span class="tag ok">Your answer ✓</span>'
            st.markdown(
                f'<div class="{classes}">{letter.upper()}. {opt} {tags}</div>',
                unsafe_allow_html=True,
            )

        # Result banner
        if is_correct:
            st.success("✓ Correct!")
        else:
            st.error("✗ Incorrect")

        # Explanation
        if item.get("explanation"):
            st.markdown(
                f'<div class="expl-box"><strong>Explanation:</strong> {item["explanation"]}</div>',
                unsafe_allow_html=True,
            )

        # Bookmark
        q_prog = progress.get(qid, {})
        bookmarked = bool(q_prog.get("bookmarked"))
        bm_col, nav_col = st.columns([1, 3])
        with bm_col:
            bm_label = "★ Bookmarked" if bookmarked else "☆ Bookmark"
            if st.button(bm_label, key=f"bm_{qid}", use_container_width=True):
                toggle_bookmark(uid, qid, not bookmarked)
                st.rerun()

        # Navigation
        with nav_col:
            nav1, nav2 = st.columns(2)
            if nav1.button("← Previous", use_container_width=True, disabled=(idx == 0)):
                session["current_index"] = max(0, idx - 1)
                save_session(uid, session["topic"], session["mode"], queue, session["current_index"], answers, session["started_at"])
                st.rerun()
            if idx + 1 < total:
                if nav2.button("Next →", use_container_width=True):
                    session["current_index"] = idx + 1
                    save_session(uid, session["topic"], session["mode"], queue, session["current_index"], answers, session["started_at"])
                    st.rerun()
            else:
                if nav2.button("Finish session ✓", use_container_width=True):
                    session["current_index"] = total
                    save_session(uid, session["topic"], session["mode"], queue, total, answers, session["started_at"])
                    st.rerun()

    else:
        # Answer selection
        options_text = [f"{option_letter(li).upper()}. {opt}" for li, opt in enumerate(item.get("options", []))]
        multi = len(item.get("answer_letters", [])) > 1
        answer_key = f"ans_{qid}"

        if multi:
            st.caption("*Multiple correct answers — select all that apply*")
            selected_opts = []
            for li, opt_text in enumerate(options_text):
                letter = option_letter(li)
                if st.checkbox(opt_text, key=f"chk_{qid}_{letter}"):
                    selected_opts.append(letter)
        else:
            chosen = st.radio("Select your answer:", options_text, key=answer_key, index=None)
            selected_opts = []
            if chosen:
                letter = chosen[0].lower()
                selected_opts = [letter]

        if st.button("Submit answer", key=f"sub_{qid}", use_container_width=True,
                     disabled=(not selected_opts)):
            correct_letters = set(item.get("answer_letters", []))
            sel_set = set(selected_opts)
            is_correct = sel_set == correct_letters
            record_attempt(uid, qid, is_correct)
            answers[qid] = {"selected_letters": list(sel_set), "is_correct": is_correct}
            save_session(uid, session["topic"], session["mode"], queue, idx, answers, session["started_at"])
            st.rerun()

    # Sidebar controls
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**Session progress:** {len(answers)}/{total}")
        correct_in_session = sum(1 for a in answers.values() if a.get("is_correct"))
        if answers:
            st.markdown(f"Score so far: **{correct_in_session}/{len(answers)}** ({pct(correct_in_session, len(answers))}%)")
        if st.button("⏹ End session", use_container_width=True):
            session["current_index"] = total
            save_session(uid, session["topic"], session["mode"], queue, total, answers, session["started_at"])
            st.rerun()
        if st.button("← Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()


def _render_session_summary(queue: list, answers: dict, bank_map: dict, uid: str = "guest") -> None:
    total = len(queue)
    correct = sum(1 for a in answers.values() if a.get("is_correct"))
    score_pct = pct(correct, total)

    st.markdown('<div class="section-head">SESSION COMPLETE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Score: {correct} / {total} ({score_pct}%)</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Correct ✓", correct)
    col2.metric("Incorrect ✗", total - correct)
    col3.metric("Score", f"{score_pct}%")

    if score_pct >= 70:
        st.success(f"{'Great work! You passed with ' + str(score_pct) + '%' if score_pct >= 80 else 'Good job — above 70%!'}")
    else:
        st.warning("Keep practising — aim for 70%+")

    st.markdown("---")
    st.markdown("**Incorrect answers:**")
    for qid in queue:
        ans = answers.get(qid)
        if ans and not ans.get("is_correct"):
            item = bank_map.get(qid)
            if not item:
                continue
            correct_letters = item.get("answer_letters", [])
            correct_text = " / ".join(choice_label(item, l) for l in correct_letters)
            sel_text = " / ".join(choice_label(item, l) for l in ans.get("selected_letters", []))
            st.markdown(f"""
<div class="q-card">
<div class="q-num">{item['year']} · {item['topic']}</div>
<div class="q-text">{item['question']}</div>
<div style="margin-top:.5rem;">
  <span class="tag ok">✓ {correct_text}</span>
  <span class="tag fail">✗ {sel_text}</span>
</div>
</div>
""", unsafe_allow_html=True)

    bc1, bc2 = st.columns(2)
    if bc1.button("← Back to dashboard", use_container_width=True):
        clear_session(uid)
        st.session_state.page = "home"
        st.rerun()
    if bc2.button("Retry session", use_container_width=True):
        session = load_session(uid)
        if session:
            save_session(uid, session["topic"], session["mode"], session["queue"], 0, {}, utc_now())
            st.rerun()


# ── BROWSER ──────────────────────────────────────────────────────────────────

def render_browser(bank: list, progress: dict, uid: str) -> None:
    st.markdown('<div class="section-head">QUESTION BROWSER</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">All Questions</div>', unsafe_allow_html=True)

    topics = sorted({q["topic"] for q in bank})
    years = sorted({q["year"] for q in bank})

    f1, f2, f3 = st.columns(3)
    with f1:
        sel_topic = st.selectbox("Topic", ["All topics"] + topics, key="br_topic")
    with f2:
        sel_year = st.selectbox("Year", ["All years"] + [str(y) for y in years], key="br_year")
    with f3:
        sel_status = st.selectbox("Status", ["All", "Unseen", "Correct", "Incorrect", "Bookmarked"], key="br_status")

    filtered = bank
    if sel_topic != "All topics":
        filtered = [q for q in filtered if q["topic"] == sel_topic]
    if sel_year != "All years":
        filtered = [q for q in filtered if str(q["year"]) == sel_year]
    if sel_status == "Unseen":
        filtered = [q for q in filtered if q["id"] not in progress]
    elif sel_status == "Correct":
        filtered = [q for q in filtered if progress.get(q["id"], {}).get("last_result") == 1]
    elif sel_status == "Incorrect":
        filtered = [q for q in filtered if has_failure(progress.get(q["id"], {}))]
    elif sel_status == "Bookmarked":
        filtered = [q for q in filtered if progress.get(q["id"], {}).get("bookmarked")]

    st.markdown(f"Showing **{len(filtered)}** questions")

    for item in filtered:
        q_prog = progress.get(item["id"], {})
        status_badge = ""
        if q_prog:
            if q_prog.get("last_result") == 1:
                status_badge = '<span class="badge ok">✓</span>'
            elif has_failure(q_prog):
                status_badge = '<span class="badge fail">✗</span>'
        if q_prog.get("bookmarked"):
            status_badge += '<span class="badge warn">★</span>'

        with st.expander(f"{item['year']} · {item['topic']} — {item['question'][:80]}... {status_badge}"):
            st.markdown(f"**{item['question']}**")
            correct_letters = set(item.get("answer_letters", []))
            for li, opt in enumerate(item.get("options", [])):
                letter = option_letter(li)
                if letter in correct_letters:
                    st.markdown(f"✅ **{letter.upper()}. {opt}**")
                else:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;{letter.upper()}. {opt}")
            if item.get("explanation"):
                st.markdown(f"""<div class="expl-box">{item['explanation']}</div>""", unsafe_allow_html=True)
            if q_prog:
                att = q_prog.get("attempts", 0)
                ok = q_prog.get("correct_count", 0)
                st.caption(f"Attempts: {att} | Correct: {ok} | Accuracy: {pct(ok, att)}%")


# ── STATS ────────────────────────────────────────────────────────────────────

def render_stats(bank: list, progress: dict, uid: str) -> None:
    st.markdown('<div class="section-head">STATISTICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your Progress</div>', unsafe_allow_html=True)

    all_ids = {q["id"] for q in bank}
    seen = {qid: r for qid, r in progress.items() if qid in all_ids}

    n_seen = len(seen)
    n_total = len(bank)
    n_correct = sum(1 for r in seen.values() if r.get("last_result") == 1)
    n_fail = sum(1 for r in seen.values() if has_failure(r))
    n_book = sum(1 for r in seen.values() if r.get("bookmarked"))

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Questions seen", n_seen, delta=f"/ {n_total}")
    col2.metric("Correct (last attempt)", n_correct)
    col3.metric("Outstanding failures", n_fail)
    col4.metric("Bookmarked", n_book)

    st.markdown("---")
    st.markdown("**By Topic**")

    topics = sorted({q["topic"] for q in bank})
    for topic in topics:
        topic_qs = [q for q in bank if q["topic"] == topic]
        ids = {q["id"] for q in topic_qs}
        t_seen = [progress.get(qid, {}) for qid in ids if qid in progress]
        n_t_ok = sum(1 for r in t_seen if r.get("last_result") == 1)
        n_t_fail = sum(1 for r in t_seen if has_failure(r))
        n_t_seen = len(t_seen)
        pct_ok = pct(n_t_ok, len(topic_qs))

        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{topic}**")
            st.markdown(f"""
<div class="prog-bar-bg">
  <div class="prog-bar-fill prog-ok" style="width:{pct_ok}%"></div>
</div>
""", unsafe_allow_html=True)
        with c2:
            st.markdown(
                f'<span class="badge ok">{n_t_ok}✓</span>'
                f'<span class="badge fail">{n_t_fail}✗</span>'
                f'<span class="badge">{n_t_seen}/{len(topic_qs)}</span>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("**By Year**")
    for year in sorted({q["year"] for q in bank}):
        yr_qs = [q for q in bank if q["year"] == year]
        yr_ok = sum(1 for q in yr_qs if progress.get(q["id"], {}).get("last_result") == 1)
        yr_seen = sum(1 for q in yr_qs if q["id"] in progress)
        pct_yr = pct(yr_ok, len(yr_qs))
        st.markdown(
            f'**{year}** — {yr_ok}/{len(yr_qs)} correct ({pct_yr}%) &nbsp;'
            f'<span class="badge">{yr_seen} seen</span>',
            unsafe_allow_html=True,
        )


# ── SIDEBAR NAV ──────────────────────────────────────────────────────────────

def sidebar_nav(bank: list, progress: dict, uid: str) -> None:
    with st.sidebar:
        st.markdown("## ⚖️ Intl. Taxation")
        st.markdown("---")
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        if st.button("🔍 Browse all questions", use_container_width=True):
            st.session_state.page = "browser"
            st.rerun()
        if st.button("📊 Statistics", use_container_width=True):
            st.session_state.page = "stats"
            st.rerun()

        st.markdown("---")
        st.markdown("**Quick start by topic:**")
        topics = sorted({q["topic"] for q in bank})
        sel = st.selectbox("Topic", topics, key="sidebar_topic", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        if c1.button("All", key="sb_all", use_container_width=True):
            _start_session(bank, sel, "all", uid)
        if c2.button("Unseen", key="sb_uns", use_container_width=True):
            _start_session(bank, sel, "unseen", uid)

        st.markdown("**Quick start by year:**")
        years = sorted({q["year"] for q in bank})
        sel_yr = st.selectbox("Year", years, key="sidebar_year", label_visibility="collapsed")
        y1, y2 = st.columns(2)
        if y1.button("Full exam", key="sb_yr_all", use_container_width=True):
            _start_session_year(bank, sel_yr, "all", uid)
        if y2.button("Shuffled", key="sb_yr_shuf", use_container_width=True):
            _start_session_year(bank, sel_yr, "shuffle", uid)

        st.markdown("---")
        bookmarked_ids = [qid for qid, r in progress.items() if r.get("bookmarked")]
        if bookmarked_ids and st.button(f"★ Practice bookmarks ({len(bookmarked_ids)})", use_container_width=True):
            qs = [q for q in bank if q["id"] in bookmarked_ids]
            random.shuffle(qs)
            save_session(uid, "Bookmarks", "bookmarked", [q["id"] for q in qs], 0, {}, utc_now())
            st.session_state.page = "quiz"
            st.rerun()

        failed_ids = [qid for qid, r in progress.items() if has_failure(r)]
        if failed_ids and st.button(f"✗ Retry all failures ({len(failed_ids)})", use_container_width=True):
            qs = [q for q in bank if q["id"] in failed_ids]
            random.shuffle(qs)
            save_session(uid, "All failures", "failed", [q["id"] for q in qs], 0, {}, utc_now())
            st.session_state.page = "quiz"
            st.rerun()

        st.markdown("---")
        st.caption(f"Total: {len(bank)} questions · 5 exams")
        st.caption("Pol Martí i Cárdenas — 267790")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main() -> None:
    init_db()
    inject_css()

    uid = get_user_id()

    if "page" not in st.session_state:
        st.session_state.page = "home"

    bank = load_bank()
    if not bank:
        st.error("question_bank.json not found.")
        return

    progress = load_progress(uid)
    sidebar_nav(bank, progress, uid)

    page = st.session_state.page
    if page == "home":
        render_home(bank, progress, uid)
    elif page == "quiz":
        render_quiz(bank, uid)
    elif page == "browser":
        render_browser(bank, progress, uid)
    elif page == "stats":
        render_stats(bank, progress, uid)
    else:
        render_home(bank, progress, uid)


if __name__ == "__main__":
    main()
