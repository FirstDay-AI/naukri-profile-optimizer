# Contributing

The most useful contributions are better keywords for a role and new roles.

## Add or improve a role

1. Edit `naukri_optimizer/data/roles.json`.
2. Each role has:
   - `id`: lowercase, dashes, e.g. `sap-consultant`
   - `name`: shown to users
   - `headline_name` (optional): how the role should start a headline, if different from `name`
   - `titles`: job titles recruiters use for this role, lowercase
   - `core`: the 10 skills recruiters search for most
   - `extra`: 10 more that help
3. Write keywords as `Display|alias|alias`, e.g. `Power BI|powerbi`. The first part is shown; all parts are matched.
4. Run the tests: `python -m unittest discover -s tests`

Please base keywords on real job descriptions, and mention two or three in your pull request.

## Change a scoring rule

Rules live in `naukri_optimizer/core.py` and are mirrored in `js/scorer.js`. Change both. `tests/test_parity.py` fails if they drift apart (it needs Node installed).
