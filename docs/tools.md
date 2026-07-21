# Tool catalog

The server registers 49 tools. The default surface contains only the 34
read-only tools. Enabling writes exposes 14 accounting write tools; enabling the
archive flag as well exposes the final archive tool.

## Search and batch detail

| Tool | Purpose |
|---|---|
| `search_relations` | Search relations with compact results and bounded scanning. |
| `search_mutations` | Search journal entries across practical filters. |
| `search_invoices` | Search invoices and optionally hydrate detail. |
| `get_relations_batch` | Fetch details for a bounded list of relation IDs. |
| `get_mutations_batch` | Fetch full mutation rows and VAT for multiple IDs. |
| `get_invoices_batch` | Fetch invoice line details for multiple IDs. |

## Reports

| Tool | Purpose |
|---|---|
| `get_trial_balance` | Aggregate debit, credit, and balance by ledger. |
| `get_profit_loss` | Build a profit-and-loss view for a period. |
| `get_balance_sheet` | Build a balance-sheet view at a date. |
| `get_vat_summary` | Summarize VAT amounts by VAT code. |
| `get_ar_ap_aging` | Age outstanding receivables or payables. |
| `get_ledger_transactions` | Return bounded transactions for one ledger. |

## Accounting records

| Area | Read tools | Opt-in write tools |
|---|---|---|
| Relations | `list_relations`, `get_relation` | `create_relation`, `update_relation`, `delete_relation` |
| Invoices | `list_invoices`, `get_invoice` | `create_invoice` |
| Mutations | `list_mutations`, `get_mutation`, `list_outstanding_invoices` | `create_mutation` |
| Products | `list_products`, `get_product`, `list_product_groups` | `create_product`, `update_product`, `delete_product` |
| Ledgers | `list_ledgers`, `get_ledger`, `get_ledger_balance` | `create_ledger`, `update_ledger` |
| Cost centers | `list_cost_centers`, `get_cost_center` | `create_cost_center`, `delete_cost_center` |
| Members | `list_members`, `get_member` | `create_member`, `delete_member` |
| Administrations | `list_administrations`, `list_linked_administrations` | - |
| Templates | `list_invoice_templates`, `list_email_templates` | - |
| Units | `list_units` | - |
| Digital archive | - | `send_file_to_digital_archive` |

## Result behavior

- Standard list tools follow the API's `limit` range of 1 through 2000 and a
  non-negative `offset`.
- Power searches and batch tools cap work to protect API usage and model context.
- Compact output removes null fields unless verbose output is requested.
- A truncated result includes a hint describing how to request the next slice.
- Decimal and date values are serialized as strings where needed for JSON.
- API failures return structured MCP errors rather than successful text results.

## Write behavior

Write tools are not advertised until
`EBOEKHOUDEN_MCP_ENABLE_WRITE_TOOLS=true`. Every advertised write schema then
contains a required `confirm` boolean. The server accepts the operation only
when its value is exactly `true` and removes it before calling the API.

The archive tool additionally requires
`EBOEKHOUDEN_MCP_ENABLE_ARCHIVE_TOOL=true`, an existing archive root, and the
Microsoft Graph variables documented in [integrations](integrations.md#optional-digital-archive-delivery).
