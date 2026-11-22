# Release checklist: v0.1.0 public launch

Run these once the empty public repo `FirstDay-AI/naukri-profile-optimizer`
exists on GitHub. Create it with **no** README, licence or .gitignore, so the
first push is clean.

## GitHub "About" box

**Description** (302 characters, limit 350):

```text
Find out why recruiters skip your Naukri profile and fix it. Free, open-source Naukri profile checker for Indian job seekers: a 0-100 score with fixes for 15 roles, plus an optional AI rewrite of your headline, summary and key skills with your own OpenAI, Anthropic or Ollama key. Runs on your machine.
```

**Website:**

```text
https://firstdayai.in/tools/naukri-profile-optimiser?utm_source=github&utm_medium=about&utm_campaign=naukri_optimizer
```

**Topics** (15):

`naukri`, `naukri-profile`, `resume`, `resume-optimizer`, `job-search`,
`job-seekers`, `india`, `career`, `ats`, `llm`, `openai`, `anthropic`,
`ollama`, `cli`, `python`

(`linkedin-alternative` is left out on purpose: the tool doesn't touch LinkedIn.)

## 1. Push

```bash
cd naukri-profile-optimizer
git remote add origin https://github.com/FirstDay-AI/naukri-profile-optimizer.git
git push -u origin main
```

## 2. Description, website and settings

```bash
gh repo edit FirstDay-AI/naukri-profile-optimizer \
  --description "Find out why recruiters skip your Naukri profile and fix it. Free, open-source Naukri profile checker for Indian job seekers: a 0-100 score with fixes for 15 roles, plus an optional AI rewrite of your headline, summary and key skills with your own OpenAI, Anthropic or Ollama key. Runs on your machine." \
  --homepage "https://firstdayai.in/tools/naukri-profile-optimiser?utm_source=github&utm_medium=about&utm_campaign=naukri_optimizer" \
  --enable-issues \
  --enable-wiki=false
```

## 3. Topics

```bash
gh api -X PUT repos/FirstDay-AI/naukri-profile-optimizer/topics \
  -H "Accept: application/vnd.github+json" \
  -f "names[]=naukri" \
  -f "names[]=naukri-profile" \
  -f "names[]=resume" \
  -f "names[]=resume-optimizer" \
  -f "names[]=job-search" \
  -f "names[]=job-seekers" \
  -f "names[]=india" \
  -f "names[]=career" \
  -f "names[]=ats" \
  -f "names[]=llm" \
  -f "names[]=openai" \
  -f "names[]=anthropic" \
  -f "names[]=ollama" \
  -f "names[]=cli" \
  -f "names[]=python"
```

Check: `gh api repos/FirstDay-AI/naukri-profile-optimizer/topics -q .names`

## 4. Issue label

`bug` and `enhancement` exist by default. The new-role issue form uses `role`:

```bash
gh label create role --repo FirstDay-AI/naukri-profile-optimizer \
  --color dcf881 --description "New role or better keywords"
```

## 5. Social preview (web UI only)

GitHub has no API for this. Go to
**https://github.com/FirstDay-AI/naukri-profile-optimizer/settings** →
**General → Social preview → Edit → Upload an image** and choose
`docs/social-preview.png` (1280×640).

## 6. Check CI is green on main

```bash
gh run list --repo FirstDay-AI/naukri-profile-optimizer --workflow tests.yml --limit 1
gh run watch --repo FirstDay-AI/naukri-profile-optimizer \
  "$(gh run list --repo FirstDay-AI/naukri-profile-optimizer --workflow tests.yml --limit 1 --json databaseId -q '.[0].databaseId')"
```

## 7. Tag v0.1.0 and release

Pushing the tag runs `.github/workflows/release.yml`: tests, build, then a
GitHub Release with the sdist and wheel attached and the v0.1.0 notes from
`CHANGELOG.md`.

```bash
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0

gh run watch --repo FirstDay-AI/naukri-profile-optimizer \
  "$(gh run list --repo FirstDay-AI/naukri-profile-optimizer --workflow release.yml --limit 1 --json databaseId -q '.[0].databaseId')"
gh release view v0.1.0 --repo FirstDay-AI/naukri-profile-optimizer
```

Fallback, only if the workflow can't run (don't do both):

```bash
python -m pip install build && python -m build
awk '/^## \[0.1.0\]/{on=1;next} on&&/^## \[/{exit} on' CHANGELOG.md > /tmp/notes.md
gh release create v0.1.0 dist/* --repo FirstDay-AI/naukri-profile-optimizer \
  --title v0.1.0 --notes-file /tmp/notes.md
```

PyPI stays off until the one-time setup in [RELEASING.md](RELEASING.md) is done.

## 8. Final checks

- [ ] The README demo image and badges load on the repo home page.
- [ ] Every firstdayai.in link in the README opens and carries `utm_source=github`.
- [ ] `pipx install git+https://github.com/FirstDay-AI/naukri-profile-optimizer` works on a clean machine, then `naukri-optimizer init` and `naukri-optimizer check profile.json`.
- [ ] The Releases sidebar shows v0.1.0 with a `.whl` and a `.tar.gz`.
- [ ] The social preview shows when the repo link is pasted into WhatsApp, LinkedIn or X.
- [ ] Link the repo from the hosted tool page and firstdayai.in footer, so search engines and AI assistants connect the two.
