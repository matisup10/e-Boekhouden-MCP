# AI assistant integrations

This server uses local stdio transport. Your AI application launches the
`eboekhouden-mcp` executable and communicates with it over standard input and
output. It does not open a network listener.

## Before configuring a client

1. Install the server and create the private `.env` from the README.
2. Run `eboekhouden-mcp --check-config` from the directory containing `.env`.
3. Find the absolute executable path with `command -v eboekhouden-mcp` on macOS
   or Linux, or `(Get-Command eboekhouden-mcp).Source` in PowerShell.
4. Keep write tools disabled until they are genuinely needed.

Use absolute paths. Desktop apps often start with a different working directory
and a smaller environment than your shell.

## Claude Desktop

Open **Settings > Developer > Edit Config** and add:

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

The file is normally:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Fully quit and restart Claude Desktop after editing.

## Claude Code

```bash
claude mcp add-json --scope user eboekhouden \
  '{"type":"stdio","command":"/absolute/path/to/eboekhouden-mcp","args":[],"cwd":"/absolute/path/to/.config/eboekhouden-mcp"}'
claude mcp get eboekhouden
```

Use `--scope project` instead of `--scope user` only when the configuration
should belong to one trusted project. Never put the actual token in a
repository-level configuration.

## ChatGPT desktop, Codex app, CLI, and IDE extension

These local OpenAI surfaces share Codex configuration. Add this to
`~/.codex/config.toml`:

```toml
[mcp_servers.eboekhouden]
command = "/absolute/path/to/eboekhouden-mcp"
cwd = "/absolute/path/to/.config/eboekhouden-mcp"
startup_timeout_sec = 10
tool_timeout_sec = 120
```

Restart the app or extension. Run `codex mcp list` in the CLI or open `/mcp` to
inspect the connection and discovered tools.

ChatGPT in a web browser cannot start a program on your computer. Connecting
from the web would require a separately secured remote MCP service; that is
intentionally outside this local, bring-your-own-credentials project.

## Cursor

Put the common `mcpServers` definition in:

- Global: `~/.cursor/mcp.json`
- Project: `.cursor/mcp.json`

Use global configuration when the server should be available across projects.
Open Cursor settings, select **Tools & MCP**, and verify the server is enabled.

## VS Code with GitHub Copilot

Run **MCP: Open User Configuration**. VS Code supports an environment file
directly:

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

Run **MCP: List Servers**, start `eboekhouden`, review its configuration, and
confirm trust. Use **Show Output** from the same menu for sanitized diagnostics.

## Windsurf

Put the common `mcpServers` definition in
`~/.codeium/windsurf/mcp_config.json`, then refresh the MCP list in Cascade or
restart Windsurf.

## Gemini CLI

Put the common `mcpServers` definition in user settings at
`~/.gemini/settings.json`. Keep `trust` false so tool calls continue to show
confirmation prompts:

```json
{
  "mcpServers": {
    "eboekhouden": {
      "command": "/absolute/path/to/eboekhouden-mcp",
      "args": [],
      "cwd": "/absolute/path/to/.config/eboekhouden-mcp",
      "trust": false,
      "timeout": 120000
    }
  }
}
```

Run `gemini mcp list` or `/mcp` to verify the connection. Project settings live
at `.gemini/settings.json`, but user settings are safer for credential-backed
personal tools.

## Other MCP clients

Configure a local stdio server with:

- command: the absolute `eboekhouden-mcp` executable path
- arguments: none
- working directory: the private directory containing `.env`

If a client cannot set a working directory, use its documented environment-file
or secret facility to provide `EBOEKHOUDEN_MCP_SECRET_TOKEN`. Do not place the
token directly in a tracked JSON or TOML file.

## Optional digital archive delivery

The archive helper sends a PDF or image through your own Microsoft Graph
application to your e-Boekhouden archive mailbox. It cannot link the attachment
to a mutation because the public API provides no endpoint for that action.

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

The archive root must already exist. Symlinks and resolved paths outside it are
rejected. Restart the MCP client after changing environment values.

## Troubleshooting

### Server does not appear

- Use an absolute executable path.
- Validate JSON or TOML syntax.
- Fully restart the client after a configuration change.
- Confirm the client is loading the user or project configuration you edited.

### Configuration is invalid

Run this from the private configuration directory:

```bash
eboekhouden-mcp --check-config
```

The checker reports field names, not credential values.

### Tools connect but API calls fail

- Confirm the token is current and belongs to the intended administration.
- Confirm the machine can reach `https://api.e-boekhouden.nl/`.
- Set `EBOEKHOUDEN_MCP_LOG_LEVEL=INFO`, restart the client, and inspect its MCP
  stderr log. Sanitize all logs before sharing them.

### Write tools are missing

This is the expected default. Set
`EBOEKHOUDEN_MCP_ENABLE_WRITE_TOOLS=true` in the private `.env`, restart the
client, and keep its approval prompts enabled.

## Official client references

- [Claude Desktop local MCP servers](https://modelcontextprotocol.io/docs/develop/connect-local-servers)
- [Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [ChatGPT and Codex MCP](https://learn.chatgpt.com/docs/extend/mcp)
- [Cursor MCP](https://docs.cursor.com/context/model-context-protocol)
- [VS Code MCP configuration](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
- [Windsurf MCP](https://docs.windsurf.com/windsurf/cascade/mcp)
- [Gemini CLI MCP servers](https://geminicli.com/docs/tools/mcp-server/)
