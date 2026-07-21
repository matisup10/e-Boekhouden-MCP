# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Strict MCP input validation for pagination, invoice lines, and batch requests.
- Rate-limit metadata and one-time expired-session recovery.
- Coverage, type checking, security scanning, CodeQL, and release artifact checks.

### Fixed

- Preserve explicitly supplied VAT amounts on mutation rows.
- Avoid mutable defaults on invoice and mutation response collections.

## 0.2.0 - 2026-07-21

### Added

- Standalone MCP distribution with its bundled e-Boekhouden API client.
- Read-only default tool surface and operator-controlled write tools.
- Explicit write confirmation, tool annotations, API host guarding, and archive
  path allowlisting.
- Setup instructions for common local MCP clients.
