"""
Accounting Router — /accounting

Thin API wrapper around the Xero accounting MCP stub.

POST /accounting/invoice — Create a Xero invoice via AccountingXeroTool

Never crashes: if the MCP tool import fails or raises, the endpoint
returns a structured error response rather than a 5xx.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

router = APIRouter(prefix="/accounting", tags=["Accounting"])

# Vault root is three levels above this file:
# backend/routers/accounting.py → backend/routers/ → backend/ → vault/
_VAULT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(_VAULT_ROOT) not in sys.path:
    sys.path.insert(0, str(_VAULT_ROOT))


# ── Pydantic models ───────────────────────────────────────────────────────────

class InvoiceRequest(BaseModel):
    customer: str
    amount: float

    @field_validator("customer")
    @classmethod
    def customer_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("customer must be a non-empty string")
        return v.strip()

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be a positive number")
        return round(v, 2)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/invoice",
    summary="Create a Xero invoice (stub)",
)
async def create_invoice(payload: InvoiceRequest):
    """
    Calls ``AccountingXeroTool.create_invoice()`` and returns the result.

    Simulates a Xero API invoice creation — no real credentials required.
    Returns a structured error dict (not a 5xx) if the tool fails.

    **Request body:**
    ```json
    { "customer": "Acme Corp", "amount": 1500.00 }
    ```

    **Response:**
    ```json
    {
      "invoice_id": "INV-001",
      "customer": "Acme Corp",
      "amount": 1500.00,
      "status": "created",
      "timestamp": "2026-02-26T12:00:00+00:00"
    }
    ```
    """
    try:
        from mcp_accounting_xero import AccountingXeroTool
        result = AccountingXeroTool().create_invoice(payload.customer, payload.amount)
    except Exception as exc:
        result = {
            "invoice_id": None,
            "customer":   payload.customer,
            "amount":     payload.amount,
            "status":     "error",
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            "error":      str(exc),
        }
    status_code = 201 if result.get("status") == "created" else 422
    return JSONResponse(content=result, status_code=status_code)
