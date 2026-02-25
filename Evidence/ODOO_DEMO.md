# Odoo MCP Stub — Dry-Run Proof

Generated: 2026-02-25T09:05:09Z
Source:    mcp/odoo_mcp_stub.py
Server:    odoo_mcp_stub
DRY_RUN:   true (default)

---

## odoo_list_invoices

Console output:
  [odoo_mcp_stub] DRY RUN: Would list Odoo invoices
  [odoo_mcp_stub]   Limit:      5
  [odoo_mcp_stub]   State:      all
  [odoo_mcp_stub]   MoveTypes:  ['out_invoice', 'in_invoice']
  [odoo_mcp_stub]   -> Set MCP_DRY_RUN=false to enable real Odoo calls.

Return value:
{
  "server": "odoo_mcp_stub",
  "action_type": "odoo_list_invoices",
  "dry_run": true,
  "result": "dry_run_logged",
  "message": "[DRY RUN] Would list Odoo invoices: limit=5, state='', move_types=['out_invoice', 'in_invoice']",
  "timestamp": "2026-02-25T09:05:09.223438+00:00",
  "intent": {
    "limit": 5,
    "state": "",
    "move_types": [
      "out_invoice",
      "in_invoice"
    ],
    "task_file": "odoo_demo.md"
  }
}

---

## odoo_create_partner

Console output:
  [odoo_mcp_stub] DRY RUN: Would create Odoo partner
  [odoo_mcp_stub]   Name:    Demo Contact
  [odoo_mcp_stub]   Email:   demo@example.com
  [odoo_mcp_stub]   Task:    odoo_demo.md
  [odoo_mcp_stub]   -> Set MCP_DRY_RUN=false to enable real Odoo calls.

Return value:
{
  "server": "odoo_mcp_stub",
  "action_type": "odoo_create_partner",
  "dry_run": true,
  "result": "dry_run_logged",
  "message": "[DRY RUN] Would create Odoo partner: name='Demo Contact', email='demo@example.com'",
  "timestamp": "2026-02-25T09:05:09.226780+00:00",
  "intent": {
    "name": "Demo Contact",
    "email": "demo@example.com",
    "phone": "",
    "company": "",
    "task_file": "odoo_demo.md"
  }
}

---

## odoo_create_invoice

Console output:
  [odoo_mcp_stub] DRY RUN: Would create Odoo invoice
  [odoo_mcp_stub]   Partner ID: 42
  [odoo_mcp_stub]   Lines:      1
  [odoo_mcp_stub]   Currency:   USD
  [odoo_mcp_stub]   -> Set MCP_DRY_RUN=false to enable real Odoo calls.

Return value:
{
  "server": "odoo_mcp_stub",
  "action_type": "odoo_create_invoice",
  "dry_run": true,
  "result": "dry_run_logged",
  "message": "[DRY RUN] Would create Odoo invoice: partner_id=42, lines=1, total=500.0 USD",
  "timestamp": "2026-02-25T09:05:09.229409+00:00",
  "intent": {
    "partner_id": 42,
    "lines_count": 1,
    "currency": "USD",
    "ref": "",
    "task_file": "odoo_demo.md"
  }
}

---

## How to Run Live

```bash
# Set real Odoo credentials
export ODOO_URL="https://your-odoo.com"
export ODOO_DB="your_db"
export ODOO_USER="admin@example.com"
export ODOO_PASSWORD="your_password"
export MCP_DRY_RUN=false

python -c "
from mcp.router import dispatch_action
result = dispatch_action('odoo_list_invoices', {'limit': 5})
print(result)
"
```

See docs/ODOO_SETUP.md for full setup instructions.
