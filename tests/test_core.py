import json
import unittest
from pathlib import Path

from naukri_optimizer.core import analyze, find_role, load_roles, norm

EX = Path(__file__).parent.parent / "examples"


def load(name):
    return json.loads((EX / name).read_text(encoding="utf-8"))


class CoreTests(unittest.TestCase):
    def test_strong_profile_scores_high(self):
        self.assertGreaterEqual(analyze(load("data_analyst_after.json"))["score"], 90)

    def test_weak_profile_scores_low(self):
        r = analyze(load("data_analyst_before.json"))
        self.assertLess(r["score"], 40)
        self.assertIn("Power BI", r["missing_core"])

    def test_max_is_100(self):
        r = analyze(load("data_analyst_after.json"))
        self.assertEqual(sum(c["max"] for c in r["checks"]), 100)

    def test_role_from_free_text_and_headline(self):
        roles = load_roles()
        self.assertEqual(find_role({"target_role": "QA engineer"}, roles)["id"], "qa-engineer")
        self.assertEqual(find_role({"headline": "Java Developer | 4 yrs"}, roles)["id"], "java-developer")

    def test_unknown_role_raises(self):
        with self.assertRaises(ValueError):
            analyze({"target_role": "astronaut", "headline": "space"})

    def test_keyword_boundaries(self):
        self.assertIn(" node.js ", norm("Worked with Node.js."))
        self.assertNotIn(" sql ", norm("PostgreSQL"))

    def test_every_role_scores(self):
        for r in load_roles():
            self.assertIn("score", analyze({"target_role": r["id"]}))


if __name__ == "__main__":
    unittest.main()
