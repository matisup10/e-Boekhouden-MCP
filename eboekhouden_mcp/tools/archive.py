"""Digital archive helper tools for the e-Boekhouden MCP server."""

from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

import httpx
from pydantic import Field

from eboekhouden_mcp.tools.base import BaseTool, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


GRAPH_API_ROOT = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"
MAX_INLINE_ATTACHMENT_BYTES = 3 * 1024 * 1024
ALLOWED_ARCHIVE_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif"}


class SendFileToDigitalArchiveInput(ToolSchema):
    """Input schema for send_file_to_digital_archive."""

    file_path: str = Field(description="Absolute or working-directory-relative path to a local PDF/image file")
    invoice_number: str | None = Field(default=None, description="Invoice number used in the archive email subject and filename")
    vendor_name: str | None = Field(default=None, description="Vendor/supplier name used in the archive email subject and filename")
    mutation_id: int | None = Field(
        default=None,
        description="Optional mutation ID for response context only; the public e-Boekhouden REST API cannot link the file automatically",
    )


class SendFileToDigitalArchiveTool(BaseTool):
    """Send a local file to the e-Boekhouden digital archive mailbox."""

    name = "send_file_to_digital_archive"
    description = (
        "Send a local PDF/image file to the configured e-Boekhouden digital archive email "
        "address via Microsoft Graph. This does not automatically link the file to a "
        "mutation because the public e-Boekhouden REST API exposes no attachment/link endpoint."
    )
    input_schema = SendFileToDigitalArchiveInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        file_path = Path(arguments["file_path"]).expanduser()
        invoice_number = _clean_text(arguments.get("invoice_number")) or "unknown"
        vendor_name = _clean_text(arguments.get("vendor_name")) or "unknown"
        mutation_id = arguments.get("mutation_id")

        result: dict[str, Any] = {
            "configured": False,
            "sent": False,
            "linked_to_mutation": False,
            "mutation_id": mutation_id,
            "archive_filename": None,
            "error": None,
            "warning": _api_limitation_warning(),
        }

        if not file_path.exists() or not file_path.is_file():
            result["error"] = f"File not found: {file_path}"
            return result

        suffix = file_path.suffix.lower()
        if suffix not in ALLOWED_ARCHIVE_EXTENSIONS:
            result["error"] = (
                f"Unsupported file type '{suffix or '(none)'}'. Allowed: "
                f"{', '.join(sorted(ALLOWED_ARCHIVE_EXTENSIONS))}."
            )
            return result

        file_size = file_path.stat().st_size
        if file_size > MAX_INLINE_ATTACHMENT_BYTES:
            result["error"] = (
                f"File is too large for this MCP archive helper ({file_size} bytes). "
                f"Maximum is {MAX_INLINE_ATTACHMENT_BYTES} bytes."
            )
            return result

        config = _load_archive_config()
        missing = [key for key, value in config.items() if not value]
        if missing:
            result["error"] = (
                "Missing archive/Graph configuration: "
                + ", ".join(missing)
                + ". Configure EBOEKHOUDEN_ARCHIVE_EMAIL, MS_GRAPH_TENANT_ID, "
                "MS_GRAPH_CLIENT_ID, MS_GRAPH_CLIENT_SECRET, and MS_GRAPH_SEND_FROM_USER "
                "(or MS_GRAPH_MAILBOX_USER)."
            )
            return result
        result["configured"] = True

        archive_filename = f"{_safe_filename_part(vendor_name, 60)} - {_safe_filename_part(invoice_number, 40)}{suffix}"
        result["archive_filename"] = archive_filename
        content_type = mimetypes.guess_type(archive_filename)[0] or "application/octet-stream"
        file_data = file_path.read_bytes()

        try:
            with httpx.Client(timeout=30.0) as http:
                access_token = _get_graph_access_token(http, config)
                _send_graph_archive_email(
                    http,
                    access_token=access_token,
                    config=config,
                    archive_filename=archive_filename,
                    content_type=content_type,
                    file_data=file_data,
                    invoice_number=invoice_number,
                    vendor_name=vendor_name,
                )
        except Exception as exc:
            result["error"] = f"Graph archive send failed: {exc}"
            return result

        result["sent"] = True
        return result


def _load_archive_config() -> dict[str, str]:
    sender = _config_value("MS_GRAPH_SEND_FROM_USER") or _config_value("MS_GRAPH_MAILBOX_USER")
    return {
        "EBOEKHOUDEN_ARCHIVE_EMAIL": _config_value("EBOEKHOUDEN_ARCHIVE_EMAIL"),
        "MS_GRAPH_TENANT_ID": _config_value("MS_GRAPH_TENANT_ID"),
        "MS_GRAPH_CLIENT_ID": _config_value("MS_GRAPH_CLIENT_ID"),
        "MS_GRAPH_CLIENT_SECRET": _config_value("MS_GRAPH_CLIENT_SECRET"),
        "MS_GRAPH_SEND_FROM_USER": sender,
    }


def _config_value(name: str) -> str:
    value = os.environ.get(name)
    if value:
        return value.strip()

    for env_file in _candidate_env_files():
        value = _read_env_file_value(env_file, name)
        if value:
            return value.strip()
    return ""


def _candidate_env_files() -> list[Path]:
    return [Path.cwd() / ".env"]


def _read_env_file_value(env_file: Path, name: str) -> str:
    if not env_file.exists():
        return ""
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""

    prefix = f"{name}="
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or not stripped.startswith(prefix):
            continue
        raw_value = stripped[len(prefix):].strip()
        if len(raw_value) >= 2 and raw_value[0] == raw_value[-1] and raw_value[0] in {"'", '"'}:
            raw_value = raw_value[1:-1]
        return raw_value
    return ""


def _get_graph_access_token(http: httpx.Client, config: dict[str, str]) -> str:
    response = http.post(
        f"https://login.microsoftonline.com/{config['MS_GRAPH_TENANT_ID']}/oauth2/v2.0/token",
        data={
            "client_id": config["MS_GRAPH_CLIENT_ID"],
            "client_secret": config["MS_GRAPH_CLIENT_SECRET"],
            "scope": GRAPH_SCOPE,
            "grant_type": "client_credentials",
        },
    )
    response.raise_for_status()
    access_token = response.json().get("access_token")
    if not access_token:
        raise RuntimeError("Graph token response did not include access_token")
    return str(access_token)


def _send_graph_archive_email(
    http: httpx.Client,
    *,
    access_token: str,
    config: dict[str, str],
    archive_filename: str,
    content_type: str,
    file_data: bytes,
    invoice_number: str,
    vendor_name: str,
) -> None:
    response = http.post(
        f"{GRAPH_API_ROOT}/users/{quote(config['MS_GRAPH_SEND_FROM_USER'], safe='')}/sendMail",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={
            "message": {
                "subject": f"Inkoopfactuur {invoice_number} - {vendor_name}",
                "body": {
                    "contentType": "Text",
                    "content": f"Inkoopfactuur {invoice_number} van {vendor_name}.",
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": config["EBOEKHOUDEN_ARCHIVE_EMAIL"],
                        }
                    }
                ],
                "attachments": [
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": archive_filename,
                        "contentType": content_type,
                        "contentBytes": base64.b64encode(file_data).decode("ascii"),
                    }
                ],
            },
            "saveToSentItems": True,
        },
    )
    response.raise_for_status()


def _api_limitation_warning() -> str:
    return (
        "File sent to e-Boekhouden digital archive only. The public e-Boekhouden REST API "
        "does not expose a digital archive upload endpoint or an endpoint to automatically "
        "link files to mutations/invoices."
    )


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def _safe_filename_part(value: str, max_length: int) -> str:
    cleaned = _clean_text(value).replace("/", "-").replace("\\", "-")
    return (cleaned or "unknown")[:max_length]
