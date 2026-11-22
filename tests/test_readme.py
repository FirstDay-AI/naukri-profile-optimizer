"""The README is the landing page: its commands and links must match the real tool."""
import re
import shlex
import unittest
from pathlib import Path

from naukri_optimizer import __version__
from naukri_optimizer.cli import build_parser
from naukri_optimizer.core import load_roles

ROOT = Path(__file__).parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
PYPROJECT = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
REPO = "github.com/FirstDay-AI/naukri-profile-optimizer"
HOSTED = "https://firstdayai.in/tools/naukri-profile-optimiser"


def entry_point():
    m = re.search(r"\[project\.scripts\]\s*\n\s*([\w-]+)\s*=\s*\"([\w.]+):(\w+)\"", PYPROJECT)
    return m.group(1), m.group(2), m.group(3)


def shell_lines():
    """Command lines from ```bash blocks, without comments or blank lines."""
    out = []
    for block in re.findall(r"```bash\n(.*?)```", README, re.S):
        for line in block.splitlines():
            line = line.split(" #", 1)[0].strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out


def subcommands():
    parser = build_parser()
    action = next(a for a in parser._actions if a.__class__.__name__ == "_SubParsersAction")
    return set(action.choices)


class ReadmeTests(unittest.TestCase):
    def test_entry_point_is_the_cli_main(self):
        name, module, func = entry_point()
        self.assertEqual(name, "naukri-optimizer")
        self.assertEqual((module, func), ("naukri_optimizer.cli", "main"))

    def test_quickstart_uses_real_commands(self):
        name = entry_point()[0]
        cmds = [shlex.split(l) for l in shell_lines()
                if l.startswith((name + " ", "python -m naukri_optimizer "))]
        cli = [c for c in cmds if c[0] == name]
        cli += [[name] + c[3:] for c in cmds if c[:3] == ["python", "-m", "naukri_optimizer"]]
        self.assertTrue(cli, "README has no naukri-optimizer commands")
        used = {c[1] for c in cli}
        # The quickstart must show init then check, and every documented
        # subcommand must exist.
        self.assertTrue({"init", "check", "roles", "rewrite"} <= subcommands())
        self.assertTrue({"init", "check", "rewrite"} <= used, used)
        parser = build_parser()
        for c in cli:
            with self.subTest(cmd=" ".join(c)):
                self.assertIn(c[1], subcommands())
                try:
                    parser.parse_args(c[1:])
                except SystemExit:
                    self.fail(f"argparse rejected: {' '.join(c)}")
        for cmd in re.findall(r"`naukri-optimizer (\w+)", README):
            self.assertIn(cmd, subcommands(), f"README mentions unknown subcommand {cmd!r}")

    def test_quickstart_order(self):
        lines = shell_lines()
        install = next(i for i, l in enumerate(lines) if l.startswith("pipx install"))
        init = next(i for i, l in enumerate(lines) if l.startswith("naukri-optimizer init"))
        check = next(i for i, l in enumerate(lines) if l.startswith("naukri-optimizer check"))
        self.assertLess(install, init)
        self.assertLess(init, check)

    def test_install_urls_point_at_this_repo(self):
        self.assertIn(f'Source = "https://{REPO}"', PYPROJECT)
        installs = [l for l in shell_lines() if " install " in f" {l} "]
        self.assertTrue(any(l.startswith("pipx install") for l in installs))
        self.assertTrue(any("pip install" in l and not l.startswith("pipx") for l in installs))
        for l in installs:
            self.assertIn(f"git+https://{REPO}", l)

    def test_links_to_hosted_tool_with_utm(self):
        links = re.findall(re.escape(HOSTED) + r"\?[^)\s\"']+", README)
        self.assertTrue(links, "README must link to the hosted tool")
        for link in links:
            self.assertIn("utm_source=github", link)
        self.assertIn(HOSTED + "?utm_source=github&utm_medium=readme&utm_campaign=naukri_optimizer", README)

    def test_firstday_links_are_tagged(self):
        for link in re.findall(r"https://firstdayai\.in[^)\s\"'>]*", README):
            self.assertIn("utm_source=github", link, link)

    def test_lists_every_role(self):
        for role in load_roles():
            self.assertIn(role["name"], README, f"README's role list is missing {role['name']}")

    def test_no_overclaims(self):
        lower = README.lower()
        for phrase in ("guarantee", "100% placement", "users trust", "thousands of"):
            self.assertNotIn(phrase, lower)

    def test_version_matches_pyproject(self):
        m = re.search(r'^version = "([^"]+)"', PYPROJECT, re.M)
        self.assertEqual(m.group(1), __version__)

    def test_sample_output_is_real(self):
        import contextlib
        import io
        from naukri_optimizer.cli import main

        block = re.search(r"```text\n\$ naukri-optimizer check (\S+)\n(.*?)```", README, re.S)
        self.assertIsNotNone(block, "README sample output block not found")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["check", str(ROOT / block.group(1))])
        real = buf.getvalue().splitlines()
        for line in block.group(2).splitlines():
            if line.strip() and line.strip() != "...":
                self.assertIn(line, real)

    def test_images_exist(self):
        for path in re.findall(r"naukri-profile-optimizer/main/(docs/[\w.-]+\.png)", README):
            self.assertTrue((ROOT / path).exists(), path)


if __name__ == "__main__":
    unittest.main()
