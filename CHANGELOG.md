# Changelog

All notable changes to this project are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-22

First public release.

### Added

- `naukri-optimizer check`: a rule-based Naukri profile score out of 100, with
  no API key and no network. Six sections: headline (25), key skills (25),
  profile summary (20), employment (10), activity (10) and career profile (10).
- A "Fix these first" list ordered by points lost, the missing core skills for
  your role and a headline template.
- 15 target roles with recruiter keywords in `naukri_optimizer/data/roles.json`.
- `naukri-optimizer rewrite`: an AI rewrite of your headline, summary and key
  skills with your own API key. Works with OpenAI, Anthropic, any
  OpenAI-compatible API (`--base-url`) and local Ollama models.
- `naukri-optimizer init` writes a blank profile file; `naukri-optimizer roles`
  lists the supported roles.
- `--json` output for `check` and `rewrite`.
- A JavaScript port of the scorer (`js/scorer.js`) for the browser and Node,
  kept identical to the Python version by a parity test.
- Python API: `from naukri_optimizer import analyze`.

[Unreleased]: https://github.com/FirstDay-AI/naukri-profile-optimizer/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/FirstDay-AI/naukri-profile-optimizer/releases/tag/v0.1.0
