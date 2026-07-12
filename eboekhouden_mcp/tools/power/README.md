# Power tools

A self-contained add-on layer for the e-Boekhouden MCP server. It adds **12
tools** on top of the 37 base tools, aimed at two things:

- **Fewer tool calls / round-trips** — search and batch tools hydrate full
  detail internally, so one call replaces "list, then `get_*` each id".
- **Fewer output tokens** — results are *compact by default* (null/empty fields
  dropped); pass `verbose: true` for raw JSON.

Everything here is additive. The base tools are untouched. The whole layer is
wired in with a single call:

```python
from eboekhouden_mcp.tools.power import register_power_tools
register_power_tools(registry)
```

(`register_all_tools` already calls this, so a normal server gets them for free.)

## Why this layer exists

The API's list endpoints return thin records and cannot filter on the fields you
most often want:

- `RelationListItem` is only `id / type / code` — **no name**. Finding a relation
  by name meant one `list` + one `get` per hit.
- `MutationListItem` has no `rows`, `relationId`, `description` or VAT breakdown.
- Mutations can only be filtered server-side by `type`, `id`, `date`,
  `description`, `invoiceNumber` — not by relation, ledger, cost center or amount.
- There are no aggregate endpoints beyond single-ledger balance and outstanding
  invoices.

These tools close those gaps client-side.

## The tools

### Enriched search (`search.py`)

| Tool | What it does |
|------|--------------|
| `search_relations` | Search by name/email/city/code/contact/type and **auto-hydrate full detail**. The way to look up a relation by name. |
| `search_mutations` | Server-side `type`/`date`/`id`/`description`/`invoice_number` **plus** client-side `relation_id`/`ledger_id`/`cost_center_id`/`amount` filters, with hydrated rows + VAT. |
| `search_invoices` | Search by number/relation/date/amount; header totals by default, `hydrate: true` for line items. |

### Batch detail (`batch.py`)

| Tool | What it does |
|------|--------------|
| `get_mutations_batch` | Full detail (rows, VAT, relation) for a list of mutation ids. |
| `get_relations_batch` | Full detail (name, address, IBAN…) for a list of relation ids. |
| `get_invoices_batch` | Full detail (line items, VAT) for a list of invoice ids. |

Ids accept a JSON array (preferred), or a JSON/comma string via `ids_json`.

### Reports / aggregates (`reports.py`)

| Tool | What it does |
|------|--------------|
| `get_trial_balance` | Balance of every ledger over a period, grouped by category with subtotals + grand total. |
| `get_profit_loss` | VW ledgers split into revenue vs expense with net result. |
| `get_balance_sheet` | BAL ledgers split into assets vs liabilities. |
| `get_vat_summary` | VAT per code over a period (hydrates mutation detail). |
| `get_ar_ap_aging` | Outstanding AR/AP bucketed 0-30 / 31-60 / 61-90 / 90+ per relation. |
| `get_ledger_transactions` | Every mutation touching a ledger over a period, with a running total. |

## Conventions

- **Compact output** by default. `verbose: true` returns raw `model_dump()` JSON.
- **Cap + truncation.** Search/batch tools bound how many records they hydrate
  with `max_details` (default 50). When there are more matches, the result
  carries `truncated: true` and a `hint` on how to narrow. `scan_limit`
  (default 500, max 2000) bounds how many candidates are pulled before filtering.
- **Reports** accept `format: "markdown"` to add a paste-ready table alongside
  the structured data.
- **Sequential hydration.** Detail is fetched one id at a time on purpose — the
  SDK client shares a single auto-refreshing session, so parallel `get()`s could
  race the token refresh. The caps keep latency and token cost bounded.
  Concurrency is a possible future enhancement.
- **Sign conventions** (reports): positive balance = debit (asset / expense),
  negative = credit (liability/equity / revenue).

## Files

```
power/
  __init__.py    register_power_tools(registry)
  _helpers.py    compact / hydrate / apply_filters / range filters / markdown
  search.py      search_relations, search_mutations, search_invoices
  batch.py       get_mutations_batch, get_relations_batch, get_invoices_batch
  reports.py     trial_balance, profit_loss, balance_sheet, vat_summary,
                 ar_ap_aging, ledger_transactions
```

Tests live in `eboekhouden-mcp/tests/test_power_*.py`.
