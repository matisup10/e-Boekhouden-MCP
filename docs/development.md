# Development and architecture

## Repository layout

```text
eboekhouden_mcp/
  config.py          operator configuration and host guards
  server.py          MCP lifecycle, policy, validation, and error mapping
  tools/             thin MCP tool adapters
  tools/power/       bounded search, batch, and report tools
eboekhouden/
  client.py          HTTP client and session lifecycle
  services/          endpoint-specific API operations
  models/            typed request and response models
tests/               offline regression and protocol tests
```

The `eboekhouden` package is bundled deliberately so a GitHub install is fully
standalone. Tool adapters should remain thin: validation and MCP naming belong
in `eboekhouden_mcp`, while HTTP behavior and API models belong in
`eboekhouden`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pre-commit install
```

On Windows, activate with `.venv\Scripts\activate`.

## Quality checks

```bash
make check
```

This runs:

- Ruff lint and format checks
- mypy across both packages
- Bandit security analysis
- pytest with branch coverage and an 80% floor
- wheel and source distribution builds
- Twine package metadata validation

The test suite is offline and must never require a real token. API tests should
use `httpx.MockTransport`; tool tests should use small fake services.

## Design rules

- Read behavior is enabled by default; side effects are not.
- Every new side-effecting tool belongs in `WRITE_TOOL_NAMES` and needs accurate
  destructive and idempotency annotations.
- Keep the explicit confirmation guard independent from client approval UI.
- Reflect official API constraints in both Pydantic and exposed JSON schemas.
- Do not return raw upstream authentication bodies or credential values.
- Bound iteration, hydration, and output added by power tools.
- Preserve stderr for logs and stdout for the stdio protocol.

## Adding a tool

1. Confirm the endpoint and constraints in the official e-Boekhouden OpenAPI
   description.
2. Add or update the request and response model in `eboekhouden/models`.
3. Implement endpoint behavior in the relevant service.
4. Add a focused tool adapter and strict input model.
5. Register the tool and, if it writes, add it to the write policy set.
6. Add schema, execution, error, and registration tests.
7. Update [the tool catalog](tools.md) and changelog.

## Release flow

Version values currently live in `pyproject.toml`, `eboekhouden_mcp/__init__.py`,
`eboekhouden_mcp/config.py`, `eboekhouden_mcp/server.py`, and
`eboekhouden/__init__.py`; update them together. Run `make check`, create the
GitHub release, and the release workflow will build, validate, and attach the
wheel and source distribution.
