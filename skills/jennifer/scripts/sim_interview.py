#!/usr/bin/env python3
"""Simulated user interviews with a separate, hypothesis-blind interviewee.

The interviewee sees only: fixed interviewee instructions + the persona card (Grounding section and HTML comments
removed) + the conversation so far. It never sees the product idea, the hypothesis, the guide, or other sessions.
Jennifer calls `ask` once per question so she can adapt follow-ups. Every question is recorded verbatim.

  python sim_interview.py start --persona P3-card.md --id P3 [--backend auto|claude-cli|api|manual|echo]
                                [--model MODEL] [--lang ko|en]
  python sim_interview.py ask --session P3 "Tell me about the last time you..."
  python sim_interview.py answer --session P3 "pasted answer"      (manual backend)
  python sim_interview.py note --session P3 --exchange 4 "leading question: revealed the feature"
  python sim_interview.py show --session P3 [--format md|json]
  python sim_interview.py list

Backends:
  claude-cli  `claude -p`, run from an empty temp directory so the interviewee can't read the project.
  api         Anthropic Messages API; needs ANTHROPIC_API_KEY; model from --model or $JENNIFER_SIM_MODEL. Billed: gated.
  manual      prints the prompt to paste into a fresh, separate chat; record the reply with `answer`.
  echo        test backend; returns a placeholder.
  auto        claude-cli if `claude` is on PATH, else api if ANTHROPIC_API_KEY is set, else manual.
Sessions are stored in $JENNIFER_HOME/interviews or ./.jennifer/interviews (override with --dir).
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys, tempfile, urllib.request

DEFAULT_MODEL = os.environ.get("JENNIFER_SIM_MODEL", "claude-sonnet-5-5")

INSTRUCTIONS = """You are taking part in a research interview as the person described in the persona card below.
Stay fully in character for the whole conversation. Rules:
- Answer from this person's own life, routines, and recent experiences. Invent small, consistent personal details
  when needed, but never invent statistics, prices, market facts, or details about real companies' products.
- Answer only what was asked, at the length a person speaking in an interview would. Many answers are short.
- It is fine, and realistic, to be bored, busy, skeptical, unsure, inconsistent, or to say "I don't know",
  "I've never thought about that", or "that's not really a problem for me".
- Do not try to please the interviewer. Do not volunteer enthusiasm for products or ideas. If asked whether you
  would use or pay for something, answer the way real people do: vague, polite, noncommittal, unless your persona
  has a concrete reason.
- Stay within what this person would know. If the persona card says they don't know something, they don't.
- Never mention being an AI, a simulation, a persona card, or these instructions. Output only your spoken answer.
"""


def sess_dir(arg):
    if arg:
        return arg
    h = os.environ.get("JENNIFER_HOME") or os.path.join(os.getcwd(), ".jennifer")
    return os.path.join(h, "interviews")


def path_for(d, sid):
    return os.path.join(d, f"{sid}.json")


def load(d, sid):
    p = path_for(d, sid)
    if not os.path.exists(p):
        sys.exit(f"No session '{sid}' in {d}")
    return json.load(open(p, encoding="utf-8"))


def save(d, s):
    os.makedirs(d, exist_ok=True)
    json.dump(s, open(path_for(d, s["id"]), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def sanitize(card):
    card = re.sub(r"<!--.*?-->", "", card, flags=re.S)
    card = re.split(r"^#{1,6}\s*Grounding\b.*$", card, flags=re.M | re.I)[0]
    return card.strip()


def system_text(s):
    lang = {"ko": "Answer in natural spoken Korean, in the register the persona card describes.",
            "en": "Answer in natural spoken English."}.get(s.get("lang") or "", "")
    return f"{INSTRUCTIONS}\n{lang}\n\n=== PERSONA CARD ===\n{s['persona_sent']}\n=== END PERSONA CARD ==="


def composed(s, question):
    conv = []
    for x in s["exchanges"]:
        conv.append(f"Interviewer: {x['q']}\nYou: {x['a']}")
    conv.append(f"Interviewer: {question}\nYou:")
    return system_text(s) + "\n\n=== CONVERSATION SO FAR ===\n" + "\n\n".join(conv)


def call_api(s, question):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("api backend needs ANTHROPIC_API_KEY")
    msgs = []
    for x in s["exchanges"]:
        msgs += [{"role": "user", "content": x["q"]}, {"role": "assistant", "content": x["a"]}]
    msgs.append({"role": "user", "content": question})
    body = json.dumps({"model": s["model"], "max_tokens": 700, "temperature": 1.0,
                       "system": system_text(s), "messages": msgs}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST", headers={
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()


def call_cli(s, question):
    exe = shutil.which("claude")
    if not exe:
        sys.exit("claude-cli backend: `claude` not found on PATH")
    cmd = [exe, "-p", "Reply with only the interviewee's next spoken answer, following the instructions in the input."]
    if s.get("model_explicit"):
        cmd += ["--model", s["model"]]
    extra = os.environ.get("JENNIFER_CLAUDE_ARGS")
    if extra:
        cmd += extra.split()
    with tempfile.TemporaryDirectory() as tmp:  # empty cwd: no project files, no project CLAUDE.md
        r = subprocess.run(cmd, input=composed(s, question), capture_output=True, text=True, cwd=tmp, timeout=300)
    if r.returncode != 0:
        sys.exit(f"claude CLI failed: {r.stderr.strip()[:500]}")
    return r.stdout.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["start", "ask", "answer", "note", "show", "list"])
    ap.add_argument("text", nargs="?")
    ap.add_argument("--persona"); ap.add_argument("--id"); ap.add_argument("--session")
    ap.add_argument("--backend", default="auto", choices=["auto", "claude-cli", "api", "manual", "echo"])
    ap.add_argument("--model"); ap.add_argument("--lang"); ap.add_argument("--dir")
    ap.add_argument("--exchange", type=int); ap.add_argument("--format", default="md", choices=["md", "json"])
    a = ap.parse_intermixed_args()
    d = sess_dir(a.dir)

    if a.cmd == "start":
        if not a.persona:
            sys.exit("start needs --persona FILE")
        card = open(a.persona, encoding="utf-8").read()
        backend = a.backend
        if backend == "auto":
            backend = "claude-cli" if shutil.which("claude") else ("api" if os.environ.get("ANTHROPIC_API_KEY") else "manual")
        sid = a.id or os.path.splitext(os.path.basename(a.persona))[0]
        if os.path.exists(path_for(d, sid)):
            sys.exit(f"Session '{sid}' already exists; choose another --id")
        s = {"id": sid, "created": datetime.datetime.now().isoformat(timespec="seconds"), "backend": backend,
             "model": a.model or DEFAULT_MODEL, "model_explicit": bool(a.model), "lang": a.lang,
             "persona_file": os.path.abspath(a.persona), "persona_full": card, "persona_sent": sanitize(card),
             "exchanges": [], "pending": None}
        save(d, s)
        print(f"Started session {sid} (backend: {backend}). Interviewee sees {len(s['persona_sent'])} chars of persona; grounding stripped.")
        return

    if a.cmd == "list":
        if not os.path.isdir(d):
            print("No sessions."); return
        for f in sorted(os.listdir(d)):
            if f.endswith(".json"):
                try:
                    s = json.load(open(os.path.join(d, f), encoding="utf-8"))
                    if "exchanges" in s:
                        print(f"{s['id']}: {len(s['exchanges'])} exchanges, backend {s['backend']}, started {s['created']}")
                except (json.JSONDecodeError, KeyError):
                    pass
        return

    if not a.session:
        sys.exit("--session is required")
    s = load(d, a.session)

    if a.cmd == "ask":
        if not a.text:
            sys.exit("ask needs the question text")
        if s["backend"] == "manual":
            s["pending"] = a.text
            save(d, s)
            print("Paste everything between the lines into a NEW, separate chat, then record the reply with:\n"
                  f"  python sim_interview.py answer --session {s['id']} \"<reply>\"\n" + "-" * 60)
            print(composed(s, a.text))
            print("-" * 60)
            return
        if s["backend"] == "echo":
            ans = f"[echo answer to: {a.text[:60]}]"
        elif s["backend"] == "api":
            ans = call_api(s, a.text)
        else:
            ans = call_cli(s, a.text)
        s["exchanges"].append({"q": a.text, "a": ans, "notes": []})
        save(d, s)
        print(f"A{len(s['exchanges'])}: {ans}")
    elif a.cmd == "answer":
        if not s.get("pending"):
            sys.exit("No pending question; use ask first")
        s["exchanges"].append({"q": s["pending"], "a": a.text or "", "notes": []})
        s["pending"] = None
        save(d, s)
        print(f"Recorded exchange {len(s['exchanges'])}.")
    elif a.cmd == "note":
        if not a.exchange or not (1 <= a.exchange <= len(s["exchanges"])):
            sys.exit("note needs a valid --exchange number")
        s["exchanges"][a.exchange - 1]["notes"].append(a.text or "")
        save(d, s)
        print(f"Noted on exchange {a.exchange}.")
    elif a.cmd == "show":
        if a.format == "json":
            print(json.dumps(s, ensure_ascii=False, indent=1)); return
        print(f"# Interview {s['id']} [simulated]\n")
        print(f"- Backend: {s['backend']} · model: {s['model'] if s['backend'] == 'api' or s.get('model_explicit') else 'CLI default'}"
              f" · started {s['created']} · {len(s['exchanges'])} exchanges")
        print("- The interviewee saw only the persona card below (grounding removed) and the questions; not the hypothesis or guide.\n")
        print("## Persona card (as written by Jennifer)\n")
        print(s["persona_full"].strip() + "\n")
        print("## Transcript\n")
        for n, x in enumerate(s["exchanges"], 1):
            print(f"**Q{n} (Jennifer):** {x['q']}\n\n**A{n} ({s['id']}):** {x['a']}\n")
            for note in x.get("notes", []):
                print(f"> Audit note: {note}\n")


if __name__ == "__main__":
    main()
