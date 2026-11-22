<h1 align="center">Naukri Profile Optimizer</h1>

<p align="center"><b>Free Naukri profile score checker and AI rewriter for job seekers in India.</b><br>
Find out why recruiters skip your Naukri profile, and fix it in 2 minutes. Open source, runs on your machine.</p>

<p align="center">
<a href="https://github.com/FirstDay-AI/naukri-profile-optimizer/actions/workflows/tests.yml"><img src="https://github.com/FirstDay-AI/naukri-profile-optimizer/actions/workflows/tests.yml/badge.svg" alt="tests"></a>
<a href="https://github.com/FirstDay-AI/naukri-profile-optimizer/releases/latest"><img src="https://img.shields.io/github/v/release/FirstDay-AI/naukri-profile-optimizer?color=1959eb&label=release" alt="Latest release"></a>
<a href="https://github.com/FirstDay-AI/naukri-profile-optimizer/stargazers"><img src="https://img.shields.io/github/stars/FirstDay-AI/naukri-profile-optimizer?style=flat&color=dcf881&labelColor=142724" alt="GitHub stars"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/licence-MIT-142724.svg" alt="Licence: MIT"></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.9%2B-1959eb.svg" alt="Python 3.9+"></a>
<a href="https://firstdayai.in/tools/naukri-profile-optimiser?utm_source=github&utm_medium=readme_badge&utm_campaign=naukri_optimizer"><img src="https://img.shields.io/badge/try%20it-free%20online-dcf881.svg?labelColor=142724" alt="Try it free online"></a>
</p>

<p align="center">
<a href="https://firstdayai.in/tools/naukri-profile-optimiser?utm_source=github&utm_medium=readme_hero&utm_campaign=naukri_optimizer"><b>Try it online, no install</b></a> ·
<a href="#quickstart-30-seconds"><b>Run it locally</b></a> ·
<a href="#compared-with-paid-tools"><b>vs paid tools</b></a> ·
<a href="#free-tool-or-done-for-you"><b>Get interviews, not just a score</b></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/FirstDay-AI/naukri-profile-optimizer/main/docs/demo.gif" alt="Animated demo: naukri-optimizer check scores a sample Data Analyst profile 17 out of 100 with a list of fixes, then scores the fixed profile 100 out of 100" width="820">
</p>

> ⭐ **If this helps you, star the repo.** Stars are how other job seekers find it.

Recruiters on Naukri find candidates by searching keywords, then filtering by location, notice period, salary and how recently a profile was active. If your profile doesn't use the words they search for, you don't show up, however good you are.

This tool scores your profile out of 100 against what recruiters search for in your target role. It tells you exactly what to fix, biggest wins first. Optionally, it rewrites your headline, summary and key skills with your own AI key.

- **Free score, no API key, no network.** The checks are plain rules you can read.
- **Built for Naukri and Indian roles.** 15 roles with recruiter keywords, in an open JSON file.
- **AI rewrite with your own key.** OpenAI, Anthropic, any OpenAI-compatible API, or a local Ollama model.
- **Private.** Your profile stays on your machine.

**Who it's for:** working professionals in India looking for their next role on Naukri: developers, analysts, QA, DevOps, sales, HR, marketing, finance and support, from about 1 to 15 years of experience. Freshers can use it too, but the score rewards results and experience you may not have yet.

<details>
<summary><b>Contents</b></summary>

- [Quickstart](#quickstart-30-seconds)
- [Sample output](#sample-output)
- [How the score works](#how-the-score-works)
- [AI rewrite with your own key](#ai-rewrite-with-your-own-key)
- [Compared with paid tools](#compared-with-paid-tools)
- [Where it falls short](#where-it-falls-short)
- [Free tool or done for you](#free-tool-or-done-for-you)
- [Roles supported](#roles-supported)
- [Privacy](#privacy)
- [Use it in your own app](#use-it-in-your-own-app)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Star history](#star-history)

</details>

## Quickstart (30 seconds)

Needs Python 3.9 or newer. No other dependencies.

```bash
pipx install git+https://github.com/FirstDay-AI/naukri-profile-optimizer
naukri-optimizer init profile.json     # writes a blank profile file
# open profile.json and paste in your Naukri headline, key skills, summary and details
naukri-optimizer check profile.json    # your score and what to fix
```

No pipx? Use pip instead:

```bash
python -m pip install git+https://github.com/FirstDay-AI/naukri-profile-optimizer
```

Want to see it work before filling anything in? Run it on the bundled sample profile, no install needed:

```bash
git clone https://github.com/FirstDay-AI/naukri-profile-optimizer
cd naukri-profile-optimizer
python -m naukri_optimizer check examples/data_analyst_before.json
```

### The profile file

`naukri-optimizer init` writes this. Copy each field from your Naukri profile.

```json
{
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
  "resume_attached": true
}
```

- `target_role`: the job you want next. Use an id from `naukri-optimizer roles`, or a title like "QA engineer".
- `key_skills` and `preferred_locations`: a list, or one comma-separated string.
- `last_updated_days`: days since you last edited your Naukri profile.

## Sample output

A real run on [`examples/data_analyst_before.json`](examples/data_analyst_before.json) (shortened):

```text
$ naukri-optimizer check examples/data_analyst_before.json

Naukri profile score: 17/100  (Needs work)
Target role: Data Analyst

  Headline         [####----------------] 5/25
  Key skills       [#####---------------] 6/25
  Profile summary  [#-------------------] 1/20
  Employment       [--------------------] 0/10
  Activity         [--------------------] 0/10
  Career profile   [##########----------] 5/10

Fix these first:
  -11 pts  2 of 10 core Data Analyst skills listed. Add the missing core skills you genuinely have (see the list below).
  -10 pts  Profile last updated 64 day(s) ago. Update something on your profile every week; recruiters often filter for recently active profiles.
  - 7 pts  Headline has 0 role keyword(s). Put 3–5 of your strongest skills in the headline.
  - 6 pts  Headline doesn't name your target role. Start the headline with "Data Analyst" so recruiter searches match it.
  ...

Missing core skills (add only the ones you really have):
  Power BI, Tableau, Python, Data Visualization, Dashboards, Data Analysis, Statistics, Advanced Excel

Headline template:
  Data Analyst | 3+ Years | SQL, Excel, Power BI, Tableau | [one result with a number]
```

The same person's improved profile, [`examples/data_analyst_after.json`](examples/data_analyst_after.json), scores 100/100. Add `--json` to any command for machine-readable output.

## How the score works

Six sections, 100 points. Every rule is in [`naukri_optimizer/core.py`](naukri_optimizer/core.py).

| Section | Points | What it checks |
| --- | --- | --- |
| Headline | 25 | 60–250 characters, names your target role, 3+ role keywords, has a number (years or a result), no filler like "hardworking" |
| Key skills | 25 | 12–25 skills, the core skills recruiters search for in your role, few generic soft skills |
| Profile summary | 20 | 300–1000 characters, 6+ role keywords, results with numbers, no filler phrases |
| Employment | 10 | Current designation matches the target role, resume attached |
| Activity | 10 | Profile updated in the last 7 days (partial credit up to 30) |
| Career profile | 10 | 1–5 preferred locations, notice period of 30 days or less, expected salary filled in |

80 and above is **Strong**, 60–79 is **Average**, below 60 **Needs work**.

The score is this tool's own measure. It is not a number from Naukri, and nobody outside Naukri knows exactly how its search ranks profiles. The rules encode what recruiters can see and filter on: keywords, recency, notice period, location and salary.

## AI rewrite with your own key

`naukri-optimizer rewrite` sends your profile and its score report to the AI provider you choose. It returns a new headline, summary and key-skills list, plus next steps. The prompt tells the model never to invent employers, numbers or skills; where a number would help, it leaves a `[placeholder]` for you to fill in. Always check every line before you paste it into Naukri.

```bash
# OpenAI
export OPENAI_API_KEY=sk-...
naukri-optimizer rewrite profile.json --provider openai --model <model-name>

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...
naukri-optimizer rewrite profile.json --provider anthropic --model <model-name>

# Any OpenAI-compatible API: Groq, OpenRouter, Together, DeepSeek and others
export OPENAI_API_KEY=<that provider's key>
naukri-optimizer rewrite profile.json --provider openai --base-url https://api.groq.com/openai/v1 --model <model-name>

# Local and free with Ollama (no key)
naukri-optimizer rewrite profile.json --provider ollama --model llama3.1
```

| Setting | Flag | Environment variable |
| --- | --- | --- |
| Provider | `--provider openai \| anthropic \| ollama` (default `openai`) | |
| Model | `--model` | `NAUKRI_AI_MODEL` |
| API base URL | `--base-url` | `NAUKRI_AI_BASE_URL` |
| OpenAI or compatible key | | `OPENAI_API_KEY` |
| Anthropic key | | `ANTHROPIC_API_KEY` |

Flags win over environment variables. On Windows PowerShell, set a variable with `$env:OPENAI_API_KEY="sk-..."`.

## Compared with paid tools

Most resume checkers are built for US-style resumes and job descriptions. Naukri profiles are different: recruiters search the headline and key skills, then filter on notice period, location, salary and recent activity. Here is how this tool compares with the common alternatives.

| | **This tool** | Naukri FastForward | Jobscan | Resume Worded | Asking ChatGPT |
| --- | --- | --- | --- | --- | --- |
| Price | **Free** (MIT) | Paid add-ons | 5 free scans a month, then $49.95/month | Free scan, Pro $49/month or $229/year | Free or paid plan |
| What it checks | Your **Naukri profile**: headline, key skills, summary, notice period, salary, activity | Resume writing and paid visibility on Naukri | Resume against one job description | Resume and LinkedIn profile | Whatever you paste and ask |
| Indian role keywords | ✅ 15 roles, open JSON | ✅ | ❌ | ❌ | Depends on the prompt |
| Rules you can read | ✅ | ❌ | ❌ | ❌ | ❌ |
| Runs on your machine | ✅ | ❌ | ❌ | ❌ | ❌ |
| No account needed | ✅ | ❌ | ❌ | ❌ | Optional |
| AI rewrite | ✅ with your own key, or local Ollama | Human writers (paid) | ✅ (paid) | ✅ (paid) | ✅ |

Prices are from public pricing pages and reviews, checked November 2026; check each vendor for current prices. Naukri FastForward and Resume Display are Naukri's own paid services and are the only ones here that change how prominently Naukri shows your profile. This tool does not.

## Where it falls short

- **The score is ours, not Naukri's.** Nobody outside Naukri knows exactly how its search ranks profiles. The rules encode what recruiters can see and filter on.
- **You paste your profile in.** The command-line tool doesn't read your resume PDF or log in to Naukri. (The [hosted version](https://firstdayai.in/tools/naukri-profile-optimiser?utm_source=github&utm_medium=readme_limits&utm_campaign=naukri_optimizer) reads your resume in your browser.)
- **15 roles so far.** Other roles fall back to generic checks. [Add yours](docs/adding-a-role.md).
- **A better profile gets you found, not hired.** You still have to apply, follow up and interview.

## Free tool or done for you

| | **This repo** | **Free online version** | **FirstDay AI plans** |
| --- | --- | --- | --- |
| Price | Free | Free | From ₹5,999/month |
| Naukri profile score and fixes | ✅ | ✅ | ✅ |
| AI rewrite of headline, summary and skills | ✅ with your own key | ✅ no key needed | ✅ written by our team |
| Reads your resume | ❌ | ✅ in your browser | ✅ |
| ATS resumes written for your target roles | ❌ | ❌ | ✅ |
| Naukri, Indeed and LinkedIn profiles optimised for you | ❌ | ❌ | ✅ |
| Applications sent and interviews coordinated for you | ❌ | ❌ | ✅ Elite plan |
| | [Quickstart](#quickstart-30-seconds) | [**Try it online**](https://firstdayai.in/tools/naukri-profile-optimiser?utm_source=github&utm_medium=readme&utm_campaign=naukri_optimizer) | [**See plans**](https://firstdayai.in/?utm_source=github&utm_medium=readme_tiers&utm_campaign=naukri_optimizer#pricing) |

The free online version runs the same scoring rules in your browser. For the AI rewrite without an API key it asks for your name and WhatsApp number.

FirstDay AI is a managed job-search service in India. The Job Search plan (₹5,999/month) includes 5 ATS-optimised resumes, Naukri and Indeed profile optimisation and monthly profile upkeep. The Co-Pilot plan (₹24,999 once) adds lifetime interview assistance with LinkedIn and Naukri optimisation. The Elite plan (₹59,999 for 12 months) adds targeted applications sent for you and referrals. Plan details: [firstdayai.in](https://firstdayai.in/?utm_source=github&utm_medium=readme_plans&utm_campaign=naukri_optimizer#pricing).

## Roles supported

Data Analyst, Data Scientist, Java Developer, Python Developer, Full Stack Developer, Frontend Developer, QA / Test Engineer, DevOps Engineer, Business Analyst, Customer Success Manager, Customer Support, Sales / Business Development, HR / Recruiter, Digital Marketing, Finance / Accounts.

Run `naukri-optimizer roles` to see the ids. Missing yours? [Add it](docs/adding-a-role.md) with a single JSON edit, or [request it](https://github.com/FirstDay-AI/naukri-profile-optimizer/issues/new?template=new_role.yml).

## Privacy

- Everything runs locally. `check`, `init` and `roles` make no network calls at all.
- No accounts, no telemetry, no analytics.
- `rewrite` sends your profile to one place only: the AI provider you pick (or the `--base-url` you set). Your API key never leaves your machine except to that provider. With Ollama, nothing leaves your machine.
- The tool never logs in to Naukri or scrapes anything. You paste your own details into a local file.

## Use it in your own app

```python
from naukri_optimizer import analyze

result = analyze({"target_role": "java-developer", "headline": "...", "key_skills": ["Java", "Spring Boot"]})
print(result["score"], result["missing_core"])
```

A JavaScript port that returns identical results is in [`js/scorer.js`](js/scorer.js). It works in the browser and in Node, and a test keeps the two in step.

## FAQ

### How do I improve my Naukri profile?

Fix the parts recruiters search and filter on. Start your headline with your target job title, then your years of experience, 3–5 core skills and one result with a number. List 12–25 specific key skills (tools and methods, not "communication"). Write a 300–1000 character summary with role keywords and results. Attach a current resume, fill in notice period, expected salary and 1–5 preferred locations, and update something every week. `naukri-optimizer check` shows which of these your profile misses, biggest gaps first.

### Why am I not getting calls on Naukri?

Usually because recruiters never see your profile. They search by keywords and filter by role, location, notice period, salary and how recently a profile was active. Common reasons a profile drops out: the headline doesn't name the job you want, key skills miss the core tools for the role, the profile hasn't been updated in weeks, the expected salary is empty, or the notice period is long with no mention of buyout. A profile that shows up can still be skipped if the headline and summary have no concrete results.

### What should I write in my Naukri headline?

Use this pattern: `Role | Years | 3–5 core skills | one result with a number`. For example: `Data Analyst | 3+ Years | SQL, Power BI, Python, Advanced Excel | Built 25+ dashboards that cut weekly reporting time 40%`. Avoid filler such as "hardworking professional seeking a challenging position"; recruiters don't search for it. The tool prints a headline template for your role.

### How many key skills should I add on Naukri?

12–25 specific skills is a good range. Fewer limits how many searches you match; a very long list dilutes your strongest skills. Include the core skills for your role that you really have, and drop generic ones like MS Office, teamwork or communication.

### How often should I update my Naukri profile?

At least once a week. Recruiters can sort and filter search results by how recently candidates were active, so a profile untouched for a month or more is easy to miss. A small real edit, such as refining your summary or adding a skill you've used, is enough.

### Is this an official Naukri tool? Does it need my Naukri password?

No and no. It is an independent open-source project by FirstDay AI. It never logs in to Naukri and never asks for your password. You copy your own profile text into a local file, and the score is calculated on your machine.

## Contributing

The most useful contribution is a new role or better keywords for an existing one. Each role is a single entry in [`naukri_optimizer/data/roles.json`](naukri_optimizer/data/roles.json): job titles, 10 core skills and 10 extra skills, taken from real job descriptions. See [docs/adding-a-role.md](docs/adding-a-role.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
python -m unittest discover -s tests    # or: python -m pytest
```

## Need interviews, not just a better profile?

FirstDay AI's team applies to jobs for you. We write your resume and optimise your profiles for your target roles, apply across 15+ job portals, follow up with HR teams and coordinate your interviews. If you'd rather spend your time preparing than applying, [see how it works](https://firstdayai.in/?utm_source=github&utm_medium=readme&utm_campaign=naukri_optimizer&utm_content=closing) or [book a strategy call](https://firstdayai.in/?utm_source=github&utm_medium=readme_cta&utm_campaign=naukri_optimizer).

## Star history

If this helped, please **star the repo**: it helps other job seekers find it. Found a wrong keyword or a missing role? [Open an issue](https://github.com/FirstDay-AI/naukri-profile-optimizer/issues).

<a href="https://star-history.com/#FirstDay-AI/naukri-profile-optimizer&Date">
  <img src="https://api.star-history.com/svg?repos=FirstDay-AI/naukri-profile-optimizer&type=Date" alt="Star history chart" width="600">
</a>

---

MIT licensed. Made in Chennai by [FirstDay AI](https://firstdayai.in/?utm_source=github&utm_medium=readme_footer&utm_campaign=naukri_optimizer).
Not affiliated with Naukri.com or Info Edge (India) Ltd. "Naukri" is used only to describe the profiles this tool checks.
