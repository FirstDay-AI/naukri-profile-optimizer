# Contributing

Thanks for helping. The most useful contributions are new roles and better
keywords for existing roles. Bug reports and scoring ideas backed by real
recruiter behaviour are welcome too.

By taking part you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Set up

You need Python 3.9 or newer. Node 18+ is optional but needed for the
JS parity test. There are no dependencies.

```bash
git clone https://github.com/FirstDay-AI/naukri-profile-optimizer
cd naukri-profile-optimizer
python -m pip install -e .
python -m unittest discover -s tests      # or: python -m pytest
```

## Add or improve a role

Edit `naukri_optimizer/data/roles.json`. The full guide, with the field list
and keyword format, is in [docs/adding-a-role.md](docs/adding-a-role.md).

Please base keywords on real job descriptions, and link two or three in your
pull request.

## Change a scoring rule

Rules live in `naukri_optimizer/core.py` and are mirrored in `js/scorer.js`.
Change both. `tests/test_parity.py` fails if they drift apart (it needs Node).
If the rule changes the demo output, regenerate the images with
`python scripts/make_images.py` (needs Pillow).

Explain in the pull request why recruiters care about the thing the rule
checks.

## Pull requests

- Keep each pull request to one change.
- Add a line to `CHANGELOG.md` under "Unreleased" if users will notice it.
- Never commit real people's profiles, names, phone numbers or emails.

## Security

Please report security problems privately. See [SECURITY.md](SECURITY.md).
