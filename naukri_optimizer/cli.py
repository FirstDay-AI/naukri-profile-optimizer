import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import analyze, load_roles

TEMPLATE = {
    "target_role": "data-analyst",
    "headline": "",
    "key_skills": [],
    "summary": "",
    "current_designation": "",
    "current_company": "",
    "years_experience": 0,
    "last_updated_days": 30,
    "notice_period_days": 30,
    "preferred_locations": ["Chennai", "Bengaluru"],
    "expected_salary": "",
    "resume_attached": True,
}

CTA = ("Want a team to rewrite your profile and apply to jobs for you? "
       "https://firstdayai.in/tools/naukri-profile-optimiser?utm_source=github&utm_medium=cli&utm_campaign=naukri_optimizer")


def bar(score, mx, width=20):
    filled = round(width * score / mx) if mx else 0
    return "#" * filled + "-" * (width - filled)


def print_report(result):
    print(f"\nNaukri profile score: {result['score']}/100  ({result['grade']})")
    print(f"Target role: {result['role']['name']}\n")
    for name, s in result["sections"].items():
        print(f"  {name:<16} [{bar(s['score'], s['max'])}] {s['score']}/{s['max']}")
    fixes = [c for c in result["checks"] if not c["ok"]]
    fixes.sort(key=lambda c: c["max"] - c["points"], reverse=True)
    if fixes:
        print("\nFix these first:")
        for c in fixes:
            print(f"  -{c['max'] - c['points']:>2} pts  {c['message']} {c['fix']}")
    if result["missing_core"]:
        print("\nMissing core skills (add only the ones you really have):")
        print("  " + ", ".join(result["missing_core"]))
    print("\nHeadline template:")
    print("  " + result["headline_template"])
    print("\nTip: run `naukri-optimizer rewrite` with your own API key for an AI rewrite.")
    print(CTA + "\n")


def print_rewrite(r):
    print("\nAI rewrite (check every line; fill the [placeholders] with your real numbers)\n")
    print("Headline:\n  " + r["headline"] + "\n")
    print("Profile summary:\n  " + r["summary"] + "\n")
    print("Key skills:\n  " + ", ".join(r["key_skills"]) + "\n")
    if r["improvements"]:
        print("Next steps:")
        for i in r["improvements"]:
            print("  - " + i)
    print("\n" + CTA + "\n")


def load_profile(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"No file at {path}. Create one with: naukri-optimizer init {path}")
    except json.JSONDecodeError as e:
        sys.exit(f"{path} is not valid JSON: {e}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="naukri-optimizer",
                                description="Score and rewrite your Naukri profile.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="write a blank profile file to fill in")
    s.add_argument("path", nargs="?", default="profile.json")

    s = sub.add_parser("roles", help="list supported target roles")

    s = sub.add_parser("check", help="score a profile (free, no API key)")
    s.add_argument("path")
    s.add_argument("--json", action="store_true", help="print raw JSON")

    s = sub.add_parser("rewrite", help="AI rewrite with your own API key")
    s.add_argument("path")
    s.add_argument("--provider", default="openai", choices=["openai", "anthropic", "ollama"])
    s.add_argument("--model", help="model name (or set NAUKRI_AI_MODEL)")
    s.add_argument("--base-url", help="OpenAI-compatible base URL, e.g. Groq or OpenRouter")
    s.add_argument("--json", action="store_true", help="print raw JSON")

    a = p.parse_args(argv)

    if a.cmd == "init":
        if Path(a.path).exists():
            sys.exit(f"{a.path} already exists.")
        Path(a.path).write_text(json.dumps(TEMPLATE, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {a.path}. Fill it in from your Naukri profile, then run: naukri-optimizer check {a.path}")
        return 0

    if a.cmd == "roles":
        for r in load_roles():
            print(f"  {r['id']:<22} {r['name']}")
        return 0

    profile = load_profile(a.path)
    try:
        result = analyze(profile)
    except ValueError as e:
        sys.exit(str(e))

    if a.cmd == "check":
        print(json.dumps(result, indent=2, ensure_ascii=False) if a.json else "", end="")
        if not a.json:
            print_report(result)
        return 0

    from .ai import AIError, rewrite
    try:
        r = rewrite(profile, result, provider=a.provider, model=a.model, base_url=a.base_url)
    except AIError as e:
        sys.exit(f"AI rewrite failed: {e}")
    if a.json:
        print(json.dumps({"analysis": result, "rewrite": r}, indent=2, ensure_ascii=False))
    else:
        print_report(result)
        print_rewrite(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
