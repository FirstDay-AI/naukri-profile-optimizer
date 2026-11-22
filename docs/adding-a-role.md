# Adding a role

Every target role lives in one file:
[`naukri_optimizer/data/roles.json`](../naukri_optimizer/data/roles.json).
Adding a role is a single JSON edit, with no code changes. The Python and
JavaScript scorers both read the same file.

## 1. Collect keywords from real job posts

Open 10 or more current job descriptions for the role on Naukri and other
portals. Note:

- the **job titles** recruiters use (they search by these);
- the **skills and tools** that appear again and again.

Skip soft skills such as communication or teamwork. Recruiters rarely search
for them, and the scorer penalises them.

## 2. Add the role

Add an object to the `roles` list:

```json
{
  "id": "sap-fico-consultant",
  "name": "SAP FICO Consultant",
  "titles": ["sap fico consultant", "sap fi consultant", "sap finance consultant"],
  "core": [
    "SAP FICO|sap fi co",
    "SAP FI",
    "SAP CO",
    "S/4HANA|s4hana|s/4 hana",
    "General Ledger",
    "Accounts Payable",
    "Accounts Receivable",
    "Asset Accounting",
    "Cost Center Accounting",
    "Financial Accounting"
  ],
  "extra": [
    "Product Costing",
    "Profit Center Accounting",
    "Bank Accounting",
    "GST",
    "Month End Closing|month-end closing",
    "Fiori",
    "LSMW",
    "Data Migration",
    "Implementation",
    "Bank Reconciliation"
  ]
}
```

(This is an example of the format. Check the keywords against real job posts
before you use them.)

| Field | Required | What it is |
| --- | --- | --- |
| `id` | yes | Lowercase with dashes. Users type it in `target_role`. |
| `name` | yes | Shown to users. |
| `headline_name` | no | How a headline should start, if different from `name`. |
| `titles` | yes | Lowercase job titles. Used to detect the role and to check the headline and designation. |
| `core` | yes | The 10 skills recruiters search for most. Worth 15 points in key skills. |
| `extra` | yes | Up to 10 more skills that help. Count towards headline and summary keywords. |

### Keyword format

Write each keyword as `Display|alias|alias`. The first part is shown to users;
every part is matched, case-insensitively, on word boundaries. For example
`Power BI|powerbi` matches "Power BI" and "PowerBI", and `SQL` does not match
"PostgreSQL".

## 3. Test it

```bash
naukri-optimizer roles                    # your role should be listed
python -m unittest discover -s tests      # or: python -m pytest
```

Then try a real (anonymised) profile for the role:

```bash
naukri-optimizer init my-role.json        # set target_role to your new id
naukri-optimizer check my-role.json
```

The tests check that every role scores, that the JS and Python scorers agree
(needs Node), and that the README lists every role. Add your role's `name` to
the "Roles supported" list in `README.md`.

## 4. Open a pull request

Link two or three of the job descriptions you used. That is how reviewers
check the keywords.
