#!/usr/bin/env python3
"""Read-only MCP bridge for a Dolibarr REST API described by Swagger/OpenAPI.

Credentials are read only from environment variables. This server intentionally
exposes GET operations only; write operations must be added individually after
their permissions and business effects have been reviewed.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP

OPENAPI_URL = os.environ.get(
    "DOLIBARR_OPENAPI_URL",
    "https://erp.mymedimo.ir/api/index.php/explorer/swagger.json",
)
BASE_URL = os.environ.get("DOLIBARR_BASE_URL", "https://erp.mymedimo.ir").rstrip("/")
API_KEY = os.environ.get("DOLIBARR_API_KEY", "")
TIMEOUT = float(os.environ.get("DOLIBARR_TIMEOUT", "30"))
MAX_RESPONSE_CHARS = int(os.environ.get("DOLIBARR_MAX_RESPONSE_CHARS", "20000"))

mcp = FastMCP("Medimo Dolibarr (read-only)")
_spec: dict[str, Any] | None = None
_operations: dict[str, dict[str, Any]] = {}


def _load_spec() -> dict[str, Any]:
    global _spec, _operations
    if _spec is not None:
        return _spec
    headers = {"Accept": "application/json"}
    if API_KEY:
        headers["DOLAPIKEY"] = API_KEY
    with httpx.Client(timeout=TIMEOUT, follow_redirects=False) as client:
        response = client.get(OPENAPI_URL, headers=headers)
        response.raise_for_status()
        spec = response.json()
    if not isinstance(spec, dict) or not (spec.get("paths") or {}):
        raise ValueError("Swagger/OpenAPI document has no paths.")
    operations: dict[str, dict[str, Any]] = {}
    for path, methods in (spec.get("paths") or {}).items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() != "get" or not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId") or f"GET {path}"
            operations[str(operation_id)] = {
                "path": path,
                "method": "GET",
                "summary": operation.get("summary", ""),
                "parameters": operation.get("parameters", []),
            }
    _spec, _operations = spec, operations
    return spec


@mcp.tool()
def list_read_operations(search: str = "") -> str:
    """List read-only GET operations available in the Medimo Swagger document."""
    _load_spec()
    needle = search.casefold().strip()
    rows = []
    for operation_id, item in sorted(_operations.items()):
        text = f"{operation_id} {item['path']} {item['summary']}".casefold()
        if not needle or needle in text:
            rows.append({
                "operationId": operation_id,
                "path": item["path"],
                "summary": item["summary"],
                "parameters": [
                    {"name": p.get("name"), "in": p.get("in"), "required": p.get("required", False)}
                    for p in item.get("parameters", [])
                    if isinstance(p, dict)
                ],
            })
    return json.dumps(rows, ensure_ascii=False, indent=2)


@mcp.tool()
async def dolibarr_get(operation_id: str, parameters: dict[str, Any] | None = None) -> str:
    """Call one documented GET operation by operationId. Never performs writes.

    Supply path/query parameter values in the parameters object. Only parameters
    declared by that GET operation are accepted.
    """
    _load_spec()
    item = _operations.get(operation_id)
    if item is None:
        raise ValueError("Unknown GET operationId. Use list_read_operations first.")

    supplied = parameters or {}
    declared = [p for p in item.get("parameters", []) if isinstance(p, dict)]
    allowed = {str(p.get("name")): p for p in declared if p.get("in") in ("path", "query")}
    unknown = set(supplied) - set(allowed)
    if unknown:
        raise ValueError(f"Undeclared parameters: {', '.join(sorted(unknown))}")

    path = item["path"]
    query: dict[str, Any] = {}
    for name, value in supplied.items():
        param = allowed[name]
        if param.get("in") == "path":
            marker = "{" + name + "}"
            if marker not in path:
                raise ValueError(f"Path parameter {name} is not present in the URL template.")
            path = path.replace(marker, quote(str(value), safe=""))
        else:
            query[name] = value

    if re.search(r"\{[^}]+\}", path):
        raise ValueError("Missing required path parameter.")
    base_path = (_spec or {}).get("basePath", "")
    url = BASE_URL + base_path.rstrip("/") + "/" + path.lstrip("/")
    headers = {"Accept": "application/json"}
    if API_KEY:
        headers["DOLAPIKEY"] = API_KEY

    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False) as client:
        response = await client.get(url, params=query, headers=headers)
    body = response.text
    if len(body) > MAX_RESPONSE_CHARS:
        body = body[:MAX_RESPONSE_CHARS] + "\n...[truncated]"
    result = {
        "status_code": response.status_code,
        "url": str(response.request.url),
        "body": body,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
