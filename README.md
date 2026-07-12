# e-Boekhouden MCP Server

An MCP (Model Context Protocol) server for the [e-Boekhouden](https://www.e-boekhouden.nl/) Dutch accounting API. It exposes **49 tools** — 37 base CRUD/list tools plus a **power-tools layer** (enriched search, batch detail, and client-side reports) designed to cut tool calls and output tokens.

## Features

- **37 base tools**: full CRUD/list for relations, invoices, mutations, products, ledgers, cost centers, members, administrations, templates, units, plus digital-archive delivery.
- **12 power tools** (`eboekhouden_mcp/tools/power/`, see its [README](eboekhouden_mcp/tools/power/README.md)):
  - **Search** — `search_relations`, `search_mutations`, `search_invoices`: multi-field filters that auto-hydrate full detail in one call (e.g. find a relation *by name*, which the list endpoint can't do).
  - **Batch** — `get_mutations_batch`, `get_relations_batch`, `get_invoices_batch`: full detail for a list of ids in one call.
  - **Reports** — `get_trial_balance`, `get_profit_loss`, `get_balance_sheet`, `get_vat_summary`, `get_ar_ap_aging`, `get_ledger_transactions`: client-side rollups.
- Compact output by default (`verbose:true` for raw JSON); caps + `truncated`/`hint` guard token cost.
- Pydantic-based input validation, automatic session management and token refresh.
- Works with Claude Code and Claude Desktop (stdio transport).

## Dependencies (important for standalone use)

This package depends on the **`eboekhouden` SDK** (`dependencies = ["eboekhouden>=0.1.0", ...]`). In this monorepo the SDK is the sibling package `../eboekhouden`. If you clone this repo **standalone**, install the SDK too — from PyPI if published, otherwise from a local checkout:

```bash
pip install -e /path/to/eboekhouden      # local SDK checkout
pip install -e .                          # this MCP server
```

## Installation

From source (recommended while in beta):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e /path/to/eboekhouden        # the SDK (sibling package)
pip install -e ".[dev]"                    # this server + test deps
```

This puts an `eboekhouden-mcp` console script on the venv's PATH.

## Configuration

The server reads environment variables (prefix `EBOEKHOUDEN_MCP_`) or a `.env` file in the working directory.

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `EBOEKHOUDEN_MCP_SECRET_TOKEN` | ✅ | — | e-Boekhouden API token |
| `EBOEKHOUDEN_MCP_API_URL` | | `https://api.e-boekhouden.nl/` | API base URL |
| `EBOEKHOUDEN_MCP_SOURCE` | | `MCP-Server` | API `source` tag |

Optional digital-archive delivery via Microsoft Graph: `EBOEKHOUDEN_ARCHIVE_EMAIL`, `MS_GRAPH_TENANT_ID`, `MS_GRAPH_CLIENT_ID`, `MS_GRAPH_CLIENT_SECRET`, `MS_GRAPH_SEND_FROM_USER`.

Example `.env`:

```env
EBOEKHOUDEN_MCP_SECRET_TOKEN=your-api-token
```

## Launch options

The server speaks MCP over **stdio** — it's started by an MCP client, not run as a long-lived daemon. To sanity-check it launches (Ctrl-C to exit; it will wait for stdio input):

```bash
# 1) console script (installed by pip)
eboekhouden-mcp

# 2) module form
python -m eboekhouden_mcp.server

# 3) explicit venv interpreter (no activation needed — use this in client configs)
/abs/path/to/.venv/bin/eboekhouden-mcp

# 4) uv (if you use uv)
uv run eboekhouden-mcp
```

In **this** checkout the working interpreter is `/home/mchbakker/projects/eboekhouden-ai/.venv/bin/eboekhouden-mcp`.

### Use in Claude Code (CLI)

Register the server once, then it's available in every session:

```bash
claude mcp add eboekhouden \
  -e EBOEKHOUDEN_MCP_SECRET_TOKEN=your-api-token \
  -- /home/mchbakker/projects/eboekhouden-ai/.venv/bin/eboekhouden-mcp
```

Then in Claude Code: `/mcp` lists servers and their tools; restart a session (or run `/mcp`) to pick up changes. Use `claude mcp list` to see it and `claude mcp remove eboekhouden` to drop it.

### Use in Claude Desktop

Add to `claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`), using the **absolute venv interpreter** so no activation is needed:

```json
{
  "mcpServers": {
    "eboekhouden": {
      "command": "/home/mchbakker/projects/eboekhouden-ai/.venv/bin/eboekhouden-mcp",
      "env": { "EBOEKHOUDEN_MCP_SECRET_TOKEN": "your-api-token" }
    }
  }
}
```

Fully quit and reopen Claude Desktop after editing the config. On **WSL**, Claude Desktop runs on the Windows side, so wrap the command with `wsl.exe`:

```json
{
  "mcpServers": {
    "eboekhouden": {
      "command": "wsl.exe",
      "args": ["-e", "/home/mchbakker/projects/eboekhouden-ai/.venv/bin/eboekhouden-mcp"],
      "env": { "EBOEKHOUDEN_MCP_SECRET_TOKEN": "your-api-token" }
    }
  }
}
```

## Tools

### Power tools (12) — see [tools/power/README.md](eboekhouden_mcp/tools/power/README.md)
- **Search**: `search_relations`, `search_mutations`, `search_invoices`
- **Batch**: `get_mutations_batch`, `get_relations_batch`, `get_invoices_batch`
- **Reports**: `get_trial_balance`, `get_profit_loss`, `get_balance_sheet`, `get_vat_summary`, `get_ar_ap_aging`, `get_ledger_transactions`

### Relations (5)
`list_relations` · `get_relation` · `create_relation` · `update_relation` · `delete_relation`

### Invoices (3)
`list_invoices` · `get_invoice` · `create_invoice`

### Mutations (4)
`list_mutations` · `get_mutation` · `create_mutation` · `list_outstanding_invoices`

### Products (6)
`list_products` · `get_product` · `create_product` · `update_product` · `delete_product` · `list_product_groups`

### Ledgers (5)
`list_ledgers` · `get_ledger` · `create_ledger` · `update_ledger` · `get_ledger_balance`

### Cost Centers (4)
`list_cost_centers` · `get_cost_center` · `create_cost_center` · `delete_cost_center`

### Members (4)
`list_members` · `get_member` · `create_member` · `delete_member`

### Administration (2)
`list_administrations` · `list_linked_administrations`

### Templates (2)
`list_invoice_templates` · `list_email_templates`

### Units (1)
`list_units`

### Digital Archive (1)
`send_file_to_digital_archive` — sends a local PDF/image to the configured archive mailbox via Microsoft Graph. The public REST API has no archive-upload or file-to-mutation link endpoint, so this returns `linked_to_mutation: false`.

## Example interactions

- "Find the supplier named ‘Acme’ and show their IBAN." → `search_relations`
- "All purchase mutations for relation 42 over EUR 500 in Q1, with line items." → `search_mutations`
- "Give me the VAT summary for 2026-Q1." → `get_vat_summary`
- "Show AR aging as of today." → `get_ar_ap_aging`
- "Trial balance for last year as markdown." → `get_trial_balance` (`format:"markdown"`)

## Development

```bash
# tests (from this folder, using the SDK-enabled venv)
/home/mchbakker/projects/eboekhouden-ai/.venv/bin/python -m pytest tests/ -q
# or, with the venv activated:
pytest
```

`asyncio_mode = "auto"` is set, so async tests need no marker.

## License

MIT
