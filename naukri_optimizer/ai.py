"""AI rewrites with your own API key (BYOK). Standard library only.

Providers:
  openai     OPENAI_API_KEY. Also any OpenAI-compatible API via --base-url
             (Groq, OpenRouter, Together, DeepSeek, a local Ollama server).
  anthropic  ANTHROPIC_API_KEY.
  ollama     Local models, no key. Shortcut for the OpenAI-compatible
             endpoint at http://localhost:11434/v1.
"""

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

PROMPT_FILE = Path(__file__).parent / "data" / "rewrite_prompt.txt"

DEFAULTS = {
    "openai": {"base_url": "https://api.openai.com/v1", "key_env": "OPENAI_API_KEY"},
    "anthropic": {"base_url": "https://api.anthropic.com/v1", "key_env": "ANTHROPIC_API_KEY"},
    "ollama": {"base_url": "http://localhost:11434/v1", "key_env": None},
}


class AIError(RuntimeError):
    pass


def system_prompt():
    return PROMPT_FILE.read_text(encoding="utf-8")


def user_message(profile, analysis):
    failed = [
        {"section": c["section"], "problem": c["message"], "fix": c["fix"]}
        for c in analysis["checks"] if not c["ok"]
    ]
    payload = {
        "target_role": analysis["role"]["name"],
        "profile": {
            k: profile.get(k)
            for k in ("headline", "key_skills", "summary", "current_designation",
                      "current_company", "years_experience", "notice_period_days",
                      "preferred_locations")
        },
        "rule_score": analysis["score"],
        "failed_checks": failed,
        "missing_core": analysis["missing_core"],
    }
    return json.dumps(payload, ensure_ascii=False)


def _post(url, headers, body, timeout=90):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise AIError(f"API returned {e.code}: {detail}") from None
    except urllib.error.URLError as e:
        raise AIError(f"Could not reach {url}: {e.reason}") from None


def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise AIError("The model did not return JSON.")
    data = json.loads(text[start:end + 1])
    out = {
        "headline": str(data.get("headline", "")).strip()[:250],
        "summary": str(data.get("summary", "")).strip(),
        "key_skills": [str(s).strip() for s in data.get("key_skills", []) if str(s).strip()][:25],
        "improvements": [str(s).strip() for s in data.get("improvements", []) if str(s).strip()][:5],
    }
    if not out["headline"] or not out["summary"]:
        raise AIError("The model's answer was missing the headline or summary.")
    return out


def rewrite(profile, analysis, provider="openai", model=None, api_key=None, base_url=None):
    provider = provider.lower()
    if provider not in DEFAULTS:
        raise AIError(f"Unknown provider '{provider}'. Use openai, anthropic or ollama.")
    cfg = DEFAULTS[provider]
    base = (base_url or os.environ.get("NAUKRI_AI_BASE_URL") or cfg["base_url"]).rstrip("/")
    model = model or os.environ.get("NAUKRI_AI_MODEL")
    if not model:
        raise AIError("Choose a model with --model or the NAUKRI_AI_MODEL variable.")
    key = api_key or (os.environ.get(cfg["key_env"]) if cfg["key_env"] else None)
    if cfg["key_env"] and not key:
        raise AIError(f"Set {cfg['key_env']} to your own API key (it never leaves your machine except to that provider).")

    system, user = system_prompt(), user_message(profile, analysis)

    if provider == "anthropic":
        resp = _post(f"{base}/messages",
                     {"x-api-key": key, "anthropic-version": "2023-06-01"},
                     {"model": model, "max_tokens": 1500, "system": system,
                      "messages": [{"role": "user", "content": user}]})
        text = "".join(b.get("text", "") for b in resp.get("content", []))
    else:
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        resp = _post(f"{base}/chat/completions", headers,
                     {"model": model, "temperature": 0.3,
                      "messages": [{"role": "system", "content": system},
                                   {"role": "user", "content": user}]})
        text = resp["choices"][0]["message"]["content"]
    return parse_json(text)
