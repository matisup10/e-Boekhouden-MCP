"""Ledger tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden.models.ledger import CreateLedger, PatchLedger
from eboekhouden_mcp.tools.base import BaseTool, PaginatedInput, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListLedgersInput(PaginatedInput):
    """Input schema for list_ledgers tool."""

    code: str | None = Field(default=None, description="Filter by ledger code")
    category: str | None = Field(
        default=None, description="Filter by category (BAL, VW, etc.)"
    )


class ListLedgersTool(BaseTool):
    """List all ledger accounts."""

    name = "list_ledgers"
    description = "List all ledger accounts (chart of accounts) with optional filters for code and category"
    input_schema = ListLedgersInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.ledgers.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
            code=arguments.get("code"),
            category=arguments.get("category"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }


class GetLedgerInput(ToolSchema):
    """Input schema for get_ledger tool."""

    id: int = Field(description="Ledger ID")


class GetLedgerTool(BaseTool):
    """Get a ledger account by ID."""

    name = "get_ledger"
    description = "Get full details of a ledger account by ID"
    input_schema = GetLedgerInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        ledger = client.ledgers.get(arguments["id"])
        return ledger.model_dump()


class CreateLedgerInput(ToolSchema):
    """Input schema for create_ledger tool."""

    code: str = Field(description="Ledger code (max 10 chars)")
    description: str = Field(description="Ledger description (max 200 chars)")
    category: str = Field(description="Category: BAL (balance sheet), VW (P&L), etc.")


class CreateLedgerTool(BaseTool):
    """Create a new ledger account."""

    name = "create_ledger"
    description = "Create a new ledger account with code, description, and category"
    input_schema = CreateLedgerInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        ledger_data = CreateLedger(
            code=arguments["code"],
            description=arguments["description"],
            category=arguments["category"],
        )
        ledger_id = client.ledgers.create(ledger_data)
        return {"id": ledger_id}


class UpdateLedgerInput(ToolSchema):
    """Input schema for update_ledger tool."""

    id: int = Field(description="Ledger ID to update")
    code: str | None = Field(default=None, description="Ledger code")
    description: str | None = Field(default=None, description="Ledger description")


class UpdateLedgerTool(BaseTool):
    """Update an existing ledger account."""

    name = "update_ledger"
    description = "Update an existing ledger account's code or description"
    input_schema = UpdateLedgerInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        ledger_id = arguments.pop("id")
        ledger_data = PatchLedger(
            code=arguments.get("code"),
            description=arguments.get("description"),
        )
        client.ledgers.update(ledger_id, ledger_data)
        return {"success": True, "id": ledger_id}


class GetLedgerBalanceInput(ToolSchema):
    """Input schema for get_ledger_balance tool."""

    id: int = Field(description="Ledger ID")
    cost_center_id: int | None = Field(
        default=None, description="Filter by cost center ID"
    )
    from_date: str | None = Field(
        default=None, description="Start date for period balance (YYYY-MM-DD)"
    )
    to_date: str | None = Field(
        default=None, description="End date for balance (YYYY-MM-DD)"
    )


class GetLedgerBalanceTool(BaseTool):
    """Get the balance of a ledger account."""

    name = "get_ledger_balance"
    description = "Get the balance of a ledger account, optionally filtered by cost center and date range"
    input_schema = GetLedgerBalanceInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        import datetime

        from_date = None
        to_date = None
        if arguments.get("from_date"):
            from_date = datetime.date.fromisoformat(arguments["from_date"])
        if arguments.get("to_date"):
            to_date = datetime.date.fromisoformat(arguments["to_date"])

        balance = client.ledgers.get_balance(
            arguments["id"],
            cost_center_id=arguments.get("cost_center_id"),
            from_date=from_date,
            to_date=to_date,
        )
        return balance.model_dump()
