# Security policy

## Reporting a vulnerability

Please do not open a public issue for a vulnerability or exposed credential.
Use GitHub's **Security** tab and select **Report a vulnerability** to send a
private report to the maintainers.

Include the affected version, reproduction steps, impact, and any suggested
mitigation. Do not include real accounting data or working credentials.

## Credential exposure

This project never needs maintainer-owned e-Boekhouden credentials. Every user
supplies credentials for their own administration. If a token is accidentally
committed, logged, or shared, revoke it in e-Boekhouden immediately, issue a new
token, and remove the exposed value from every client configuration and shell
history where it appeared.

## Security defaults

- Only the official HTTPS API host is accepted by default.
- Credentials are represented as secret values and are never printed by the
  configuration checker.
- Accounting write tools are disabled unless explicitly enabled.
- Digital archive delivery is separately opt-in and can only read files below
  a configured directory.
- MCP tool annotations identify read-only and destructive operations so clients
  can apply approval policies.
