"""Python and JavaScript scorers must return identical results."""
import json
import random
import shutil
import subprocess
import unittest
from pathlib import Path

from naukri_optimizer.core import analyze, load_roles

ROOT = Path(__file__).parent.parent
WORDS = ["SQL", "Python", "Power BI", "Excel", "hardworking", "Java", "Spring Boot", "React",
         "Node.js", "Selenium", "GST", "Tally", "SEO", "Google Ads", "CRM", "Docker", "AWS",
         "team player", "3+ years", "40%", "Data Analyst", "QA Engineer", "Recruiter", "MS Office"]


def random_profile(rng, roles):
    pick = lambda k: rng.sample(WORDS, k)
    return {
        "target_role": rng.choice([r["id"] for r in roles] + ["", "Developer"]),
        "headline": " | ".join(pick(rng.randint(0, 6))),
        "key_skills": pick(rng.randint(0, 20)),
        "summary": ". ".join(pick(rng.randint(0, 12))) * rng.randint(1, 6),
        "current_designation": rng.choice(["", "Data Analyst", "Software Engineer", "Recruiter"]),
        "years_experience": rng.choice([0, 1, 3.5, 8, None]),
        "last_updated_days": rng.choice([None, 0, 7, 8, 30, 31, 90]),
        "notice_period_days": rng.choice([None, 0, 15, 30, 60, 90]),
        "preferred_locations": pick(rng.randint(0, 7)),
        "expected_salary": rng.choice(["", "8 LPA"]),
        "resume_attached": rng.choice([True, False]),
    }


@unittest.skipUnless(shutil.which("node"), "node not installed")
class ParityTests(unittest.TestCase):
    def test_same_results(self):
        roles = load_roles()
        rng = random.Random(7)
        profiles = [json.loads(p.read_text()) for p in sorted((ROOT / "examples").glob("*.json"))]
        profiles += [random_profile(rng, roles) for _ in range(300)]
        py = []
        for p in profiles:
            try:
                py.append(analyze(p, roles))
            except ValueError:
                py.append("ERROR")
        js_code = (
            "const S=require(process.argv[1]);const roles=require(process.argv[2]).roles;"
            "const ps=JSON.parse(require('fs').readFileSync(0,'utf8'));"
            "console.log(JSON.stringify(ps.map(p=>{try{return S.analyze(p,roles)}catch(e){return 'ERROR'}})));"
        )
        out = subprocess.run(
            ["node", "-e", js_code, str(ROOT / "js" / "scorer.js"),
             str(ROOT / "naukri_optimizer" / "data" / "roles.json")],
            input=json.dumps(profiles), capture_output=True, text=True, check=True)
        js = json.loads(out.stdout)
        for i, (a, b) in enumerate(zip(py, js)):
            self.assertEqual(a, b, f"profile {i} differs: {profiles[i]}")


if __name__ == "__main__":
    unittest.main()
