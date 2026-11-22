# Releasing

Releases are cut by pushing a version tag. The
[release workflow](.github/workflows/release.yml) then:

1. runs the full test suite (Python 3.9, 3.12, 3.13 and the JS parity test);
2. checks the tag matches `version` in `pyproject.toml`;
3. builds the sdist and wheel with `python -m build` and smoke-tests the wheel;
4. creates a GitHub Release named after the tag, with the notes for that
   version from `CHANGELOG.md` and both files attached;
5. publishes to PyPI, but only once the one-time setup below is done.

## Cutting a release

1. Update `version` in `pyproject.toml` and `__version__` in
   `naukri_optimizer/__init__.py` (a test checks they match).
2. Move the `Unreleased` notes in `CHANGELOG.md` under a new
   `## [X.Y.Z] - YYYY-MM-DD` heading and update the compare links at the bottom.
3. Commit, then tag and push:

   ```bash
   git commit -am "Release vX.Y.Z"
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin main vX.Y.Z
   ```

4. Watch it: `gh run watch` and then `gh release view vX.Y.Z`.

If the workflow fails before the GitHub Release step, fix the problem, delete
the tag (`git push --delete origin vX.Y.Z && git tag -d vX.Y.Z`) and tag again.

## One-time PyPI setup (optional)

The `pypi` job uses [trusted publishing](https://docs.pypi.org/trusted-publishers/),
so no API token is stored in GitHub. Until the steps below are done the job is
skipped and releases only go to GitHub.

1. Check the name `naukri-profile-optimizer` is free on PyPI. If it is taken,
   change `name` in `pyproject.toml` and the `url` in the `pypi` job.
2. On PyPI, go to **Your account → Publishing → Add a new pending publisher**
   and enter:
   - PyPI project name: `naukri-profile-optimizer`
   - Owner: `FirstDay-AI`
   - Repository name: `naukri-profile-optimizer`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
3. In the GitHub repo, go to **Settings → Environments → New environment** and
   create `pypi`. Optionally add yourself as a required reviewer so every PyPI
   upload waits for approval.
4. Turn the job on:

   ```bash
   gh variable set PYPI_PUBLISH --body true --repo FirstDay-AI/naukri-profile-optimizer
   ```

The next tag you push also publishes to PyPI.

Once the package is on PyPI, add `pipx install naukri-profile-optimizer` to the
README quickstart.
