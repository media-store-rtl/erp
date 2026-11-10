# Medimo Dolibarr OpenAPI MCP bridge (read-only)

This is a separate developer integration; it does not modify Dolibarr core or
replace Dolibarr's built-in MCP module. It reads the live Swagger/OpenAPI
document and exposes its documented **GET** operations to Claude Desktop.
POST, PUT, PATCH and DELETE are deliberately not exposed.

## Requirements

- Python 3.10+
- A Dolibarr API key belonging to a dedicated, least-privilege user
- Network access from the computer running Claude Desktop to the Medimo server

## Install

```bash
cd dev/medimo-openapi-mcp
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Set these environment variables in the process environment (do not commit a
real `.env` file or credentials):

- `DOLIBARR_BASE_URL=https://erp.mymedimo.ir`
- `DOLIBARR_OPENAPI_URL=https://erp.mymedimo.ir/api/index.php/explorer/swagger.json`
- `DOLIBARR_API_KEY=<new API key>`

The Dolibarr API key is sent in the `DOLAPIKEY` HTTP header. The supplied
account password is not needed by this bridge and must not be stored here.

## Claude Desktop

Configure Claude Desktop to launch `server.py` with the Python interpreter
from this virtual environment. Example (replace paths with actual local paths):

```json
{
  "mcpServers": {
    "medimo-dolibarr": {
      "command": "/absolute/path/to/dev/medimo-openapi-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/dev/medimo-openapi-mcp/server.py"],
      "env": {
        "DOLIBARR_BASE_URL": "https://erp.mymedimo.ir",
        "DOLIBARR_OPENAPI_URL": "https://erp.mymedimo.ir/api/index.php/explorer/swagger.json",
        "DOLIBARR_API_KEY": "SET_LOCALLY_NOT_IN_GIT"
      }
    }
  }
}
```

On Windows, use the full path to `.venv\\Scripts\\python.exe`. Keep the real
API key in the local Claude configuration or a protected environment variable;
never paste it into source code, issues, commits, or logs.

## Available tools

- `list_read_operations(search)`: find documented GET operations.
- `dolibarr_get(operation_id, parameters)`: invoke one documented GET operation.

The bridge validates the operationId and accepts only declared path/query
parameters. It never executes arbitrary URLs or non-GET operations. Review the
Dolibarr user's permissions and test with non-sensitive records first.

## Important

This bridge is a conservative fallback. If the built-in Dolibarr MCP endpoint
is already enabled and accessible to Claude Desktop, prefer that native
integration instead of running a second bridge. The Swagger URL must be
reachable from the machine running this server; this repository integration
has not been able to test access to the live Medimo host from the GitHub
execution environment.
