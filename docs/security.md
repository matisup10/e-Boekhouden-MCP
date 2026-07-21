# Security model

e-Boekhouden MCP is a local adapter between one MCP client and the official
e-Boekhouden API. It is not an authentication broker, credential vault, hosted
service, or multi-user authorization layer.

## Data flow

1. The MCP client starts `eboekhouden-mcp` as the current operating-system user.
2. The server reads its token from the environment or a local `.env`.
3. The bundled client exchanges that token for a short-lived API session over
   HTTPS.
4. Tool results return to the same MCP client over stdio.

The selected AI client can see tool results, including accounting data. Its own
retention, model-training, workspace, and privacy controls remain outside this
project's boundary.

## Controls

| Risk | Control |
|---|---|
| Accidental write | Write tools are absent unless the operator enables them; every write also requires `confirm: true`. |
| Destructive action | MCP annotations identify destructive tools; server instructions require exact user confirmation. |
| Credential exfiltration | Only the official API host is accepted by default; custom hosts require an explicit override and HTTPS. |
| Credential leakage | Pydantic secret types redact config representations; errors omit request bodies and values. |
| Malformed tool input | Strict JSON schemas reject unknown fields, bad limits, invalid nested rows, and oversized batches before API access. |
| Session races | Session creation, refresh, and API requests are serialized; one expired-session retry is allowed. |
| Arbitrary file read | Archive delivery is disabled separately and resolves every file beneath one configured root. |
| Oversized attachment | Archive files are limited to 3 MiB and an allowlist of PDF/image extensions. |
| Protocol corruption | Application logs go to stderr; stdout is reserved for MCP JSON-RPC. |

## Operator responsibilities

- Use a token for the intended administration and revoke tokens no longer used.
- Keep `.env` outside repositories, backups, chat messages, and shared folders.
- Keep the operating system, Python runtime, MCP client, and this package current.
- Review tool arguments and output before approving accounting changes.
- Restrict access to the local user account that launches the MCP server.
- Do not expose this stdio server through an unauthenticated network wrapper.

## Custom API hosts

`EBOEKHOUDEN_MCP_ALLOW_CUSTOM_API_URL=true` disables an important credential
destination guard. Use it only for a trusted HTTPS proxy or test endpoint you
operate and have reviewed. URLs containing embedded usernames or passwords are
always rejected.

## Incident response

If a token may have been exposed:

1. Revoke it in e-Boekhouden immediately.
2. Issue a replacement with the minimum access needed.
3. Remove the old value from MCP configuration, shell history, logs, backups,
   and any AI conversation where it appeared.
4. Review recent accounting activity for unexpected changes.
5. Treat a committed secret as compromised even after the commit is rewritten.

For a vulnerability in this project, follow [SECURITY.md](../SECURITY.md) and
use a private GitHub security advisory.
