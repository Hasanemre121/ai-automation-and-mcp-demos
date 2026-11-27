"""
DEMO PROJECT (Sample Portfolio Code — Not a Client Project)
Custom Model Context Protocol (MCP) Server in Python (JSON-RPC 2.0 over stdio / FastAPI compatible)

Provides 3 realistic business tools for Claude Desktop, Cursor, or MCP clients:
1. lookup_order_status(order_id)
2. calculate_workflow_roi(hours_saved_per_week, hourly_rate_usd, team_size)
3. create_action_item(title, owner, priority)

Run self-test:
    python mcp_business_tools_server.py --selftest
Run MCP stdio server:
    python mcp_business_tools_server.py
"""

from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict

SAMPLE_ORDERS: Dict[str, Dict[str, Any]] = {
    "ORD-1001": {"status": "shipped", "carrier": "DHL", "eta": "2026-11-29", "total_usd": 149.00},
    "ORD-1002": {"status": "processing", "carrier": "UPS", "eta": "2026-12-01", "total_usd": 320.50},
    "ORD-1003": {"status": "delivered", "carrier": "FedEx", "eta": "2026-11-25", "total_usd": 89.90},
}

ACTION_ITEMS: list[Dict[str, Any]] = []

TOOLS_MANIFEST = [
    {
        "name": "lookup_order_status",
        "description": "Look up live order status, carrier, and ETA by order_id (e.g., ORD-1001).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order identifier such as ORD-1001"}
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "calculate_workflow_roi",
        "description": "Calculate monthly and annual time and cost savings from automating a business process.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "hours_saved_per_week": {"type": "number"},
                "hourly_rate_usd": {"type": "number"},
                "team_size": {"type": "integer"},
            },
            "required": ["hours_saved_per_week", "hourly_rate_usd", "team_size"],
        },
    },
    {
        "name": "create_action_item",
        "description": "Create a tracked action item in the internal task queue.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "owner": {"type": "string"},
                "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
            },
            "required": ["title", "owner", "priority"],
        },
    },
]


def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "lookup_order_status":
        oid = str(arguments.get("order_id", "")).strip().upper()
        record = SAMPLE_ORDERS.get(oid)
        if not record:
            return {"found": False, "order_id": oid, "available_demo_ids": list(SAMPLE_ORDERS.keys())}
        return {"found": True, "order_id": oid, **record}

    if name == "calculate_workflow_roi":
        hrs = float(arguments.get("hours_saved_per_week", 0))
        rate = float(arguments.get("hourly_rate_usd", 0))
        team = int(arguments.get("team_size", 1))
        weekly_usd = hrs * rate * team
        return {
            "weekly_hours_saved": round(hrs * team, 2),
            "monthly_savings_usd": round(weekly_usd * 4.33, 2),
            "annual_savings_usd": round(weekly_usd * 52, 2),
        }

    if name == "create_action_item":
        item = {
            "id": f"ACT-{len(ACTION_ITEMS) + 1:03d}",
            "title": arguments.get("title", "Untitled"),
            "owner": arguments.get("owner", "unassigned"),
            "priority": arguments.get("priority", "MEDIUM"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        ACTION_ITEMS.append(item)
        return {"created": True, "item": item}

    raise ValueError(f"Unknown tool: {name}")


def handle_rpc(request: Dict[str, Any]) -> Dict[str, Any] | None:
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "ethan-demo-mcp-server", "version": "1.0.0"},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS_MANIFEST}}
    if method == "tools/call":
        params = request.get("params", {})
        output = call_tool(params.get("name", ""), params.get("arguments", {}))
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"content": [{"type": "text", "text": json.dumps(output, indent=2)}]},
        }
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def run_selftest() -> None:
    print("=== Running MCP Server Demo Self-Test ===")
    for req in [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "lookup_order_status", "arguments": {"order_id": "ORD-1001"}},
        },
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "calculate_workflow_roi",
                "arguments": {"hours_saved_per_week": 6, "hourly_rate_usd": 35, "team_size": 3},
            },
        },
    ]:
        resp = handle_rpc(req)
        print(json.dumps(resp, indent=2))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        run_selftest()
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            response = handle_rpc(json.loads(line))
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
