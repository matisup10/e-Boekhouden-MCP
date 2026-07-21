# Contributing

Thanks for helping improve e-Boekhouden MCP. Changes should stay focused on the
standalone MCP server, its bundled API client, tests, and documentation.

## Before opening an issue

- Search existing issues first.
- Remove API tokens, relation data, invoices, addresses, and financial values.
- Use a private security advisory for vulnerabilities or exposed credentials.
- Confirm that the behavior belongs to the public e-Boekhouden API.

## Local setup

```bash
git clone https://github.com/matisup10/e-Boekhouden-MCP.git
cd e-Boekhouden-MCP
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pre-commit install
make check
```

On Windows, activate the environment with `.venv\Scripts\activate`.

The test suite uses mocks and must not require real credentials. Keep changes
compatible with Python 3.10 through 3.13.

## Pull requests

Keep pull requests narrow and explain observable behavior. Add regression tests
for fixes and update documentation when configuration, tools, or safety behavior
changes. Avoid unrelated formatting or refactors.

New write capabilities must remain disabled by default, require explicit
confirmation, and carry accurate MCP annotations. Never weaken the official API
host guard or file allowlist for convenience.

Run `make check` before opening the pull request. By contributing, you agree that
your changes are licensed under the repository's MIT license.
