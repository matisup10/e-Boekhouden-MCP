# e-Boekhouden MCP

[![CI](https://github.com/matisup10/e-Boekhouden-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/matisup10/e-Boekhouden-MCP/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A standalone [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for the Dutch [e-Boekhouden](https://www.e-boekhouden.nl/) accounting API. Connect your own e-Boekhouden administration to Claude, ChatGPT/Codex, Cursor, VS Code, Windsurf, Gemini CLI, or any other local MCP client.

This repository contains only the MCP server and its bundled API client. It has no hosted service, shared account, bundled credentials, or dependency on another e-Boekhouden repository.

This is an independent community project and is not affiliated with or endorsed by e-Boekhouden.nl.

## Safety first

- **Bring your own token:** the server only works with credentials from your own e-Boekhouden administration.
- **Read-only by default:** 34 query and reporting tools are exposed. The 15 tools that create, update, delete, or send data remain hidden until the operator explicitly enables them.
- **Official API only:** credentials are sent only to `https://api.e-boekhouden.nl/` unless a custom endpoint is explicitly allowed.
- **Credential redaction:** config output never prints the token. `.env` files, IDE settings, and common secret formats are ignored by Git.
- **Client approvals:** MCP annotations identify read-only and destructive tools so compatible clients can request approval for writes.
- **Archive allowlist:** the optional archive tool can only read files below one configured directory.

Accounting data returned by a tool is provided to the AI client you selected. Review that client's data and privacy terms before connecting a production administration.

## Quick start

Requirements:

- Python 3.10 or newer
- An e-Boekhouden API token for your own administration
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pipx`

Install directly from GitHub:

```bash
uv tool install git+https://github.com/matisup10/e-Boekhouden-MCP.git
```

On macOS or Linux, create a private configuration directory outside any repository:

```bash
mkdir -p ~/.config/eboekhouden-mcp
chmod 700 ~/.config/eboekhouden-mcp
printf '%s\n' 'EBOEKHOUDEN_MCP_SECRET_TOKEN=replace-with-your-own-token' \
  > ~/.config/eboekhouden-mcp/.env
chmod 600 ~/.config/eboekhouden-mcp/.env
```

Replace the placeholder, then validate the setup without contacting the API:

```bash
cd ~/.config/eboekhouden-mcp
eboekhouden-mcp --check-config
command -v eboekhouden-mcp
```

On Windows PowerShell:

```powershell
$configDir = Join-Path $env:USERPROFILE ".config\eboekhouden-mcp"
New-Item -ItemType Directory -Force $configDir
notepad (Join-Path $configDir ".env")
Push-Location $configDir
eboekhouden-mcp --check-config
Pop-Location
(Get-Command eboekhouden-mcp).Source
```

Add `EBOEKHOUDEN_MCP_SECRET_TOKEN=replace-with-your-own-token` in Notepad, replace the placeholder, and save it. Use the absolute executable path printed by `command -v` or `Get-Command` and the absolute configuration directory in client settings. GUI applications often do not inherit your shell `PATH`.

With `pipx`, use `pipx install 'git+https://github.com/matisup10/e-Boekhouden-MCP.git'` instead. To update either installation, run `uv tool upgrade eboekhouden-mcp` or `pipx upgrade eboekhouden-mcp`.

## Connect an AI assistant

The server uses local stdio transport. It is launched by the AI client and does not listen on a network port.

### Claude Desktop, Cursor, Windsurf, and Gemini CLI

These clients use the common `mcpServers` format. Replace both absolute paths:

```json
{
  "mcpServers": {
    "eboekhouden": {
      "command": "/absolute/path/to/eboekhouden-mcp",
      "args": [],
      "cwd": "/absolute/path/to/.config/eboekhouden-mcp"
    }
  }
}
```

Put that server entry in the client-specific file:

| Client | Configuration location |
|---|---|
| [Claude Desktop](https://modelcontextprotocol.io/docs/develop/connect-local-servers) | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`; Windows: `%APPDATA%\\Claude\\claude_desktop_config.json` |
| [Cursor](https://docs.cursor.com/en/tools/mcp) | User: `~/.cursor/mcp.json`; project: `.cursor/mcp.json` |
| [Windsurf](https://docs.windsurf.com/windsurf/cascade/mcp) | `~/.codeium/windsurf/mcp_config.json` |
| [Gemini CLI](https://geminicli.com/docs/tools/mcp-server/) | User: `~/.gemini/settings.json`; project: `.gemini/settings.json` |

Restart the client after editing. Claude Code can import the same definition directly:

```bash
claude mcp add-json --scope user eboekhouden \
  '{"type":"stdio","command":"/absolute/path/to/eboekhouden-mcp","args":[],"cwd":"/absolute/path/to/.config/eboekhouden-mcp"}'
claude mcp list
```

### ChatGPT desktop, Codex CLI, and Codex IDE extension

These OpenAI clients share Codex MCP configuration. Add this to `~/.codex/config.toml`:

```toml
[mcp_servers.eboekhouden]
command = "/absolute/path/to/eboekhouden-mcp"
cwd = "/absolute/path/to/.config/eboekhouden-mcp"
default_tools_approval_mode = "writes"
```

Restart the app or extension. In Codex CLI, run `codex mcp list` or open `/mcp`. The `writes` approval mode uses this server's MCP annotations to prompt for non-read-only tools. See the [Codex MCP documentation](https://learn.chatgpt.com/docs/extend/mcp.md).

ChatGPT on the web cannot start a local stdio process. A remote MCP deployment with authentication would be required; this repository intentionally ships only the local BYO-credentials server.

### VS Code with GitHub Copilot

Run **MCP: Open User Configuration** and use VS Code's `envFile` support so the token is not stored in `mcp.json`:

```json
{
  "servers": {
    "eboekhouden": {
      "type": "stdio",
      "command": "/absolute/path/to/eboekhouden-mcp",
      "args": [],
      "envFile": "/absolute/path/to/.config/eboekhouden-mcp/.env"
    }
  }
}
```

Start the server from **MCP: List Servers**, confirm trust, and select its tools in Copilot Chat. See the [VS Code MCP server guide](https://code.visualstudio.com/docs/agent-customization/mcp-servers).

### Any other MCP client

Create a local **stdio** server with:

- command: the absolute path to `eboekhouden-mcp`
- arguments: none
- working directory: the directory containing the private `.env`

If the client does not support `cwd`, pass `EBOEKHOUDEN_MCP_SECRET_TOKEN` through its documented secret or environment-variable facility. Never commit a client config containing the real token. MCP clients differ in their configuration file names, but the process and environment values are the same.

## Configuration

The server reads environment variables and a `.env` file in its working directory.

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `EBOEKHOUDEN_MCP_SECRET_TOKEN` | yes | - | Token for your own e-Boekhouden administration |
| `EBOEKHOUDEN_MCP_ENABLE_WRITE_TOOLS` | no | `false` | Expose create, update, and delete tools |
| `EBOEKHOUDEN_MCP_API_URL` | no | official API | API base URL |
| `EBOEKHOUDEN_MCP_ALLOW_CUSTOM_API_URL` | no | `false` | Allow a trusted non-official HTTPS API endpoint |
| `EBOEKHOUDEN_MCP_SOURCE` | no | `MCP-Server` | API session source label |
| `EBOEKHOUDEN_MCP_LOG_LEVEL` | no | `WARNING` | Diagnostic verbosity written to stderr |
| `EBOEKHOUDEN_MCP_ENABLE_ARCHIVE_TOOL` | no | `false` | Expose Microsoft Graph archive delivery |
| `EBOEKHOUDEN_MCP_ARCHIVE_ROOT` | for archive | - | Only directory from which archive files may be read |

Copy [`.env.example`](.env.example) for all optional archive variables. Keep that copy outside the repository and restrict its file permissions.

### Enable write tools

Writes are an operator-level decision, not something an AI can enable through a tool call. Add this to the private `.env`, restart the client, and keep client approval prompts enabled:

```env
EBOEKHOUDEN_MCP_ENABLE_WRITE_TOOLS=true
```

Before approving a write, verify the administration, relation or ledger identifier, monetary values, and the exact requested action. Every write call also requires `confirm: true`; assistants are instructed to set it only after that explicit confirmation. Delete operations are marked destructive. Creating invoices and mutations may be irreversible in normal accounting workflows even though they are not labeled as delete operations.

### Enable digital archive delivery

The archive helper sends a PDF or image through your Microsoft Graph application to your e-Boekhouden archive mailbox. It cannot automatically link the file to a mutation because the public API has no such endpoint.

Enable both write flags, set an existing allowlisted directory, and provide your own Graph credentials:

```env
EBOEKHOUDEN_MCP_ENABLE_WRITE_TOOLS=true
EBOEKHOUDEN_MCP_ENABLE_ARCHIVE_TOOL=true
EBOEKHOUDEN_MCP_ARCHIVE_ROOT=/absolute/path/to/allowed/invoices
EBOEKHOUDEN_ARCHIVE_EMAIL=your-archive-address@e-Boekhouden.nl
MS_GRAPH_TENANT_ID=your-tenant-id
MS_GRAPH_CLIENT_ID=your-client-id
MS_GRAPH_CLIENT_SECRET=your-client-secret
MS_GRAPH_SEND_FROM_USER=sender@example.com
```

Symlinks and paths resolving outside `EBOEKHOUDEN_MCP_ARCHIVE_ROOT` are rejected. Attachments are limited to 3 MiB and common PDF/image extensions.

## Tools

### Read-only tools (34, enabled by default)

- Search: `search_relations`, `search_mutations`, `search_invoices`
- Batch detail: `get_mutations_batch`, `get_relations_batch`, `get_invoices_batch`
- Reports: `get_trial_balance`, `get_profit_loss`, `get_balance_sheet`, `get_vat_summary`, `get_ar_ap_aging`, `get_ledger_transactions`
- Relations: `list_relations`, `get_relation`
- Invoices: `list_invoices`, `get_invoice`
- Mutations: `list_mutations`, `get_mutation`, `list_outstanding_invoices`
- Products: `list_products`, `get_product`, `list_product_groups`
- Ledgers: `list_ledgers`, `get_ledger`, `get_ledger_balance`
- Cost centers: `list_cost_centers`, `get_cost_center`
- Members: `list_members`, `get_member`
- Administration: `list_administrations`, `list_linked_administrations`
- Templates and units: `list_invoice_templates`, `list_email_templates`, `list_units`

### Write tools (15, opt-in)

- Relations: `create_relation`, `update_relation`, `delete_relation`
- Invoices and mutations: `create_invoice`, `create_mutation`
- Products: `create_product`, `update_product`, `delete_product`
- Ledgers: `create_ledger`, `update_ledger`
- Cost centers: `create_cost_center`, `delete_cost_center`
- Members: `create_member`, `delete_member`
- Archive: `send_file_to_digital_archive` (also requires its separate archive flag)

Power tools return compact output by default, cap result counts, and include `truncated` and `hint` fields when more data is available. Detailed behavior is documented in [`eboekhouden_mcp/tools/power/README.md`](eboekhouden_mcp/tools/power/README.md).

## Development

```bash
git clone https://github.com/matisup10/e-Boekhouden-MCP.git
cd e-Boekhouden-MCP
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
python -m pytest -q
python -m build
python -m twine check dist/*
```

No real credentials are needed for the test suite. See [SECURITY.md](SECURITY.md) for private vulnerability reporting and credential-response guidance.

## License

[MIT](LICENSE)
