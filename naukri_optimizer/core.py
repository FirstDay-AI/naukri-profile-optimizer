"""Rule-based Naukri profile scorer.

No API key and no network needed. The same rules are ported to JavaScript in
js/scorer.js; tests/test_parity.py checks both give identical results.
"""

import json
import math
import re
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "roles.json"

FLUFF = [
    "hardworking", "hard working", "hard-working", "seeking a challenging",
    "challenging position", "challenging role", "dynamic organization",
    "dynamic organisation", "team player", "self motivated", "self-motivated",
    "looking for an opportunity", "looking for a job", "result oriented",
    "result-oriented", "go-getter", "quick learner", "passionate", "dedicated",
]

GENERIC_SKILLS = {
    "communication", "communication skills", "teamwork", "team work",
    "leadership", "ms office", "microsoft office", "time management",
    "hard working", "hardworking", "problem solving", "interpersonal skills",
    "english", "typing", "internet", "multitasking", "team player",
}


def load_roles(path=DATA_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["roles"]


def norm(text):
    """Lowercase, keep letters/digits/+/#/., drop sentence-ending dots."""
    t = (text or "").lower()
    t = re.sub(r"[^a-z0-9+#.]+", " ", t)
    t = re.sub(r"\.(?=\s|$)", " ", t)
    return " " + re.sub(r"\s+", " ", t).strip() + " "


def kw_parts(kw):
    return [p.strip() for p in kw.split("|") if p.strip()]


def kw_display(kw):
    return kw_parts(kw)[0]


def has_kw(normed_text, kw):
    return any(norm(p) in normed_text for p in kw_parts(kw))


def round_half_up(x):
    return int(math.floor(x + 0.5))


def as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        items = value
    else:
        items = re.split(r"[,\n;|]", str(value))
    out, seen = [], set()
    for item in items:
        s = str(item).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out


def find_role(profile, roles):
    target = (profile.get("target_role") or "").strip()
    if target:
        for r in roles:
            if target.lower() == r["id"] or target.lower() == r["name"].lower():
                return r
        t = norm(target)
        for r in roles:
            if any(norm(title) in t or t.strip() in norm(title) for title in r["titles"]):
                return r
    probe = norm(" ".join([profile.get("headline") or "", profile.get("current_designation") or ""]))
    for r in roles:
        if any(norm(title) in probe for title in r["titles"]):
            return r
    return None


def _num(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def analyze(profile, roles=None):
    roles = roles or load_roles()
    role = find_role(profile, roles)
    if role is None:
        raise ValueError(
            "Could not tell the target role. Set target_role to one of: "
            + ", ".join(r["id"] for r in roles)
        )

    headline = profile.get("headline") or ""
    summary = profile.get("summary") or ""
    designation = profile.get("current_designation") or ""
    skills = as_list(profile.get("key_skills"))
    locations = as_list(profile.get("preferred_locations"))
    years = _num(profile.get("years_experience"))
    updated = _num(profile.get("last_updated_days"))
    notice = _num(profile.get("notice_period_days"))

    n_head, n_sum, n_des = norm(headline), norm(summary), norm(designation)
    n_skills = norm(" , ".join(skills))
    all_kw = role["core"] + role["extra"]
    is_title = lambda nt: any(norm(t) in nt for t in role["titles"])

    checks = []

    def add(cid, section, pts, mx, message, fix):
        checks.append({"id": cid, "section": section, "points": pts, "max": mx,
                       "ok": pts == mx, "message": message, "fix": fix})

    # Headline (25)
    hl = len(headline.strip())
    pts = 5 if 60 <= hl <= 250 else (2 if 30 <= hl < 60 else 0)
    add("headline_length", "Headline", pts, 5,
        f"Headline is {hl} characters.",
        "Aim for 60–250 characters: role, years, top skills and one result.")
    pts = 6 if is_title(n_head) else 0
    add("headline_role", "Headline", pts, 6,
        "Headline names your target role." if pts else "Headline doesn't name your target role.",
        f"Start the headline with \"{role.get('headline_name', role['name'])}\" so recruiter searches match it.")
    hk = sum(1 for k in all_kw if has_kw(n_head, k))
    pts = 7 if hk >= 3 else 5 if hk == 2 else 2 if hk == 1 else 0
    add("headline_keywords", "Headline", pts, 7,
        f"Headline has {hk} role keyword(s).",
        "Put 3–5 of your strongest skills in the headline.")
    pts = 4 if re.search(r"\d", headline) else 0
    add("headline_number", "Headline", pts, 4,
        "Headline has a number." if pts else "Headline has no numbers.",
        "Add years of experience or a result, e.g. \"3+ years\" or \"cut costs 20%\".")
    hf = [p for p in FLUFF if p in headline.lower()]
    pts = 3 if not hf else 0
    add("headline_fluff", "Headline", pts, 3,
        "No filler words in the headline." if pts else "Filler words: " + ", ".join(hf) + ".",
        "Replace filler with skills or results recruiters search for.")

    # Key skills (25)
    n = len(skills)
    pts = 5 if 12 <= n <= 25 else (3 if 8 <= n <= 11 or 26 <= n <= 40 else 0)
    add("skills_count", "Key skills", pts, 5,
        f"{n} key skill(s) listed.",
        "List 12–25 specific skills. Too few limits search matches; too many dilutes them.")
    matched_core = [k for k in role["core"] if has_kw(n_skills, k)]
    target = min(8, len(role["core"]))
    pts = round_half_up(15 * min(len(matched_core), target) / target)
    add("skills_core", "Key skills", pts, 15,
        f"{len(matched_core)} of {len(role['core'])} core {role['name']} skills listed.",
        "Add the missing core skills you genuinely have (see the list below).")
    generic = [s for s in skills if s.lower() in GENERIC_SKILLS]
    share = (len(generic) / n) if n else 0
    pts = 5 if n and share <= 0.2 else (2 if n else 0)
    add("skills_generic", "Key skills", pts, 5,
        f"{len(generic)} generic skill(s) like communication or MS Office.",
        "Recruiters rarely search soft skills. Swap them for tools and methods.")

    # Profile summary (20)
    sl = len(summary.strip())
    pts = 5 if 300 <= sl <= 1000 else (3 if 150 <= sl < 300 or 1000 < sl <= 1500 else 0)
    add("summary_length", "Profile summary", pts, 5,
        f"Summary is {sl} characters.",
        "Aim for 300–1000 characters: 3–5 short sentences.")
    sk = sum(1 for k in all_kw if has_kw(n_sum, k))
    pts = 5 if sk >= 6 else 3 if sk >= 3 else 1 if sk >= 1 else 0
    add("summary_keywords", "Profile summary", pts, 5,
        f"Summary has {sk} role keyword(s).",
        "Mention at least 6 role skills naturally in the summary.")
    pts = 5 if re.search(r"\d", summary) else 0
    add("summary_metrics", "Profile summary", pts, 5,
        "Summary includes numbers." if pts else "Summary has no numbers.",
        "Add results: team size, % improvement, revenue, tickets per day, projects shipped.")
    sf = [p for p in FLUFF if p in summary.lower()]
    pts = 5 if not sf else (2 if len(sf) == 1 else 0)
    add("summary_fluff", "Profile summary", pts, 5,
        "No filler phrases in the summary." if not sf else "Filler phrases: " + ", ".join(sf) + ".",
        "Cut filler; every sentence should show a skill or a result.")

    # Employment (10)
    pts = 5 if (is_title(n_des) or any(has_kw(n_des, k) for k in role["core"])) else 0
    add("designation_match", "Employment", pts, 5,
        "Current designation matches the target role." if pts else "Current designation doesn't match the target role.",
        "If your work matches the target role, describe it with the target role's words in your employment details.")
    pts = 5 if profile.get("resume_attached") else 0
    add("resume_attached", "Employment", pts, 5,
        "Resume attached." if pts else "No resume attached.",
        "Attach an up-to-date PDF resume; many recruiters download it before calling.")

    # Activity and career profile (20)
    if updated is None:
        pts, msg = 0, "Last update date not given."
    else:
        pts = 10 if updated <= 7 else (5 if updated <= 30 else 0)
        msg = f"Profile last updated {int(updated)} day(s) ago."
    add("freshness", "Activity", pts, 10, msg,
        "Update something on your profile every week; recruiters often filter for recently active profiles.")
    nl = len(locations)
    pts = 4 if 1 <= nl <= 5 else (2 if nl > 5 else 0)
    add("locations", "Career profile", pts, 4,
        f"{nl} preferred location(s).",
        "Pick 1–5 cities you'd really move to, plus remote if you want it.")
    if notice is None:
        pts, msg = 0, "Notice period not given."
    else:
        pts = 3 if notice <= 30 else 1
        msg = f"Notice period is {int(notice)} day(s)."
    add("notice", "Career profile", pts, 3, msg,
        "Short notice periods get more calls. If yours is long, mention buyout or your last working day.")
    pts = 3 if profile.get("expected_salary") else 0
    add("salary", "Career profile", pts, 3,
        "Expected salary filled in." if pts else "Expected salary is empty.",
        "Fill in expected salary; recruiters filter on it.")

    score = sum(c["points"] for c in checks)
    sections = {}
    for c in checks:
        s = sections.setdefault(c["section"], {"score": 0, "max": 0})
        s["score"] += c["points"]
        s["max"] += c["max"]

    profile_text = norm(" ".join([headline, summary, designation, ", ".join(skills)]))
    missing_core = [kw_display(k) for k in role["core"] if not has_kw(profile_text, k)]
    missing_extra = [kw_display(k) for k in role["extra"] if not has_kw(profile_text, k)]

    return {
        "role": {"id": role["id"], "name": role["name"]},
        "score": score,
        "grade": "Strong" if score >= 80 else "Average" if score >= 60 else "Needs work",
        "sections": sections,
        "checks": checks,
        "missing_core": missing_core,
        "missing_extra": missing_extra,
        "suggested_skills": suggest_skills(skills, role, profile_text),
        "headline_template": headline_template(role, skills, years, notice, n_skills),
    }


def suggest_skills(skills, role, profile_text):
    keep = [s for s in skills if s.lower() not in GENERIC_SKILLS]
    have = norm(", ".join(keep))
    for k in role["core"]:
        if len(keep) >= 25:
            break
        if not has_kw(have, k):
            keep.append(kw_display(k))
            have = norm(", ".join(keep))
    return keep


def headline_template(role, skills, years, notice, n_skills):
    top = [kw_display(k) for k in role["core"] if has_kw(n_skills, k)][:4]
    if len(top) < 4:
        top += [kw_display(k) for k in role["core"] if kw_display(k) not in top][: 4 - len(top)]
    exp = "Fresher" if not years else f"{int(years)}+ Years"
    parts = [role.get("headline_name", role["name"]), exp, ", ".join(top), "[one result with a number]"]
    if notice is not None and notice <= 15:
        parts.append("Immediate Joiner")
    return " | ".join(parts)
