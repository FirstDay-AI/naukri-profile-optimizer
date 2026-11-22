# Naukri Profile Optimiser

**Free, open-source Naukri profile checker for Indian job seekers.** Get a 0–100 score in seconds, see exactly which keywords recruiters search for that your profile is missing, and get an AI rewrite of your headline, summary and key skills using your own API key.

No sign-up. No data collection. Your profile never leaves your machine unless you choose an AI provider.

```text
$ naukri-optimizer check profile.json

Naukri profile score: 17/100  (Needs work)
Target role: Data Analyst

  Headline         [####----------------] 5/25
  Key skills       [#####---------------] 6/25
  Profile summary  [#-------------------] 1/20
  Employment       [--------------------] 0/10
  Activity         [--------------------] 0/10
  Career profile   [##########----------] 5/10

Fix these first:
  -11 pts  2 of 10 core Data Analyst skills listed. Add the missing core skills you genuinely have.
  -10 pts  Profile last updated 64 day(s) ago. Update something every week.
  - 7 pts  Headline has 0 role keyword(s). Put 3–5 of your strongest skills in the headline.
  ...
```

> Prefer not to use the terminal? Use the hosted version at **[firstdayai.in/tools/naukri-profile-optimiser](https://firstdayai.in/tools/naukri-profile-optimiser?utm_source=github&utm_medium=readme&utm_campaign=naukri_optimizer)**. It includes the AI rewrite with no API key needed.

## Why this exists

Recruiters on Naukri find candidates by searching keywords and filtering by role, location, notice period and how recently a profile was updated. A good profile with the wrong words never shows up. This tool checks your profile against what recruiters search for in your target role and tells you what to fix, in order of impact.

| | **Naukri Profile Optimiser** | Paid resume-writing services | Generic ATS checkers |
| --- | --- | --- | --- |
| Price | Free | Paid per rewrite | Usually freemium |
| Built for Naukri profiles | Yes | Sometimes | No, built for resumes |
| India-specific roles and keywords | 15 roles, open data | Varies | Rarely |
| Runs on your machine | Yes | No | No |
| AI rewrite | Bring your own key, or local Ollama | Human writer | Paid tier |
| Open source | MIT | No | No |

## Quick start

Needs Python 3.9 or newer. No other dependencies.

```bash
pip install git+https://github.com/FirstDay-AI/naukri-profile-optimizer
naukri-optimizer init profile.json      # creates a blank profile file
# open profile.json and copy in your Naukri headline, key skills, summary and details
naukri-optimizer check profile.json     # free score, no API key
```

See every supported target role:

```bash
naukri-optimizer roles
```

## AI rewrite with your own API key

The rewrite sends your profile and the score report to the AI provider you choose. It never invents employers, numbers or skills. Where a number would help, it leaves a `[placeholder]` for you to fill in.

```bash
# OpenAI
export OPENAI_API_KEY=sk-...
naukri-optimizer rewrite profile.json --provider openai --model <model-name>

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
naukri-optimizer rewrite profile.json --provider anthropic --model <model-name>

# Any OpenAI-compatible API (Groq, OpenRouter, Together, DeepSeek...)
export OPENAI_API_KEY=<that provider's key>
naukri-optimizer rewrite profile.json --provider openai --base-url https://api.groq.com/openai/v1 --model <model-name>

# Fully local and free with Ollama
naukri-optimizer rewrite profile.json --provider ollama --model llama3.1
```

You can set `NAUKRI_AI_MODEL` and `NAUKRI_AI_BASE_URL` instead of passing flags.

## What it checks

| Section | Points | What it looks at |
| --- | --- | --- |
| Headline | 25 | Length, target role named, role keywords, a number, filler words |
| Key skills | 25 | 12–25 skills, core skills for your role, too many soft skills |
| Profile summary | 20 | Length, role keywords, results with numbers, filler phrases |
| Employment | 10 | Designation matches target role, resume attached |
| Activity | 10 | Updated in the last 7 days |
| Career profile | 10 | Preferred locations, notice period, expected salary |

The rules are plain Python in [`naukri_optimizer/core.py`](naukri_optimizer/core.py) and the role keywords are in [`naukri_optimizer/data/roles.json`](naukri_optimizer/data/roles.json). Read them, argue with them and send a pull request.

## Use it in your own app

```python
from naukri_optimizer import analyze

result = analyze({"target_role": "java-developer", "headline": "...", "key_skills": ["Java", "Spring Boot"]})
print(result["score"], result["missing_core"])
```

A JavaScript port that returns identical results is in [`js/scorer.js`](js/scorer.js). It works in the browser and in Node.

## Supported roles

Data Analyst, Data Scientist, Java Developer, Python Developer, Full Stack Developer, Frontend Developer, QA / Test Engineer, DevOps Engineer, Business Analyst, Customer Success Manager, Customer Support, Sales / Business Development, HR / Recruiter, Digital Marketing, Finance / Accounts.

Missing yours? Adding a role is a single JSON edit. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Want someone to do the whole job search for you?

This tool fixes your profile. [FirstDay AI](https://firstdayai.in/?utm_source=github&utm_medium=readme&utm_campaign=naukri_optimizer) is a Chennai-based team that rewrites your resume and profiles, applies to jobs across 15+ portals, follows up with HR and coordinates your interviews. [Book a free strategy call](https://firstdayai.in/?utm_source=github&utm_medium=readme_cta&utm_campaign=naukri_optimizer).

---

Not affiliated with Naukri.com or Info Edge (India) Ltd. "Naukri" is used only to describe the profiles this tool checks. MIT licensed.
