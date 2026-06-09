# How to Contribute

## Community Guidelines

This project follows [Google's Open Source Community Guidelines](https://opensource.google/conduct/).

## Contributor License Agreement

Contributions to this project must be accompanied by a Contributor License
Agreement (CLA). You (or your employer) retain the copyright to your
contribution; this simply gives us permission to use and redistribute your
contributions as part of the project. Head over to
<https://cla.developers.google.com/> to see your current agreements on file or
to sign a new one.

You generally only need to submit a CLA once, so if you've already submitted one
(even if it was for a different project), you probably don't need to do it again.

## Code Reviews

All submissions, including submissions by project members, require review. We
use GitHub pull requests for this purpose. Consult
[GitHub Help](https://help.github.com/articles/about-pull-requests/) for more
information on using pull requests.

## Local Development Setup

### Prerequisites

Pyink requires **Python 3.10 or newer**. The macOS system Python (3.9) is not
supported. We recommend installing Python 3.11 via Homebrew:

```sh
brew install python@3.11
```

Install `tox` using the Homebrew Python:

```sh
pip3.11 install tox
```

### Running the test suite

Because macOS ships with Python 3.9, you must explicitly tell tox which Python
to use:

```sh
tox -e py311 --override testenv.basepython=python3.11
```

### Verifying pyink formats its own source

The `run_self` environment checks that pyink can format its own codebase:

```sh
tox -e run_self --override testenv.basepython=python3.11
```

If it fails with files to reformat, run pyink directly using the tox virtualenv
and then re-run the check:

```sh
.tox/run_self/bin/pyink .
tox -e run_self --override testenv.basepython=python3.11
```

### Note on pyink's own formatting style

Pyink formats its own source using **Black style** (not pyink style). This is
intentional — see `pyproject.toml` where `pyink = false` is set under
`[tool.pyink]`. The `run_self` tox env uses `pyink --check` to verify this,
relying on the project's `pyproject.toml` config to apply Black-compatible
formatting.
