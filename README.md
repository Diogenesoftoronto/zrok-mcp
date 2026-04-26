# zrok-mcp

An [MCP server](https://modelcontextprotocol.io/) for [zrok](https://zrok.io/) — the open-source secure sharing platform built on OpenZiti. Lets AI agents manage zrok tunnels, shares, and access programmatically.

Supports **three transports**: stdio (local), streamable-http and SSE (remote/Bifrost).

## Tools

Each tool uses an `action` parameter to select the operation — no need to remember many tool names.

### `zrok_env` — Environment management
| Action | Description |
|--------|-------------|
| `status` | Check environment status (enabled, API endpoint, identity) |
| `enable` | Enable the zrok environment with an account token |
| `disable` | Disable the current zrok environment |

### `zrok_share` — Share management
| Action | Description |
|--------|-------------|
| `create` | Create a public or private share |
| `delete` | Delete a share by token |
| `list` | List all shares with optional filters |

### `zrok_access` — Access management
| Action | Description |
|--------|-------------|
| `create` | Create access to a private share |
| `delete` | Remove access to a share |
| `list` | List all accesses with optional filters |

## Requirements

- Python 3.10+
- [zrok2](https://pypi.org/project/zrok2/) Python SDK
- A zrok account and enabled environment

## Install

```bash
cd zrok-mcp
pip install -e .
```

## Run

Transport is selected via the `ZROK_MCP_TRANSPORT` environment variable (default: `stdio`).

| Transport | Use case |
|-----------|----------|
| `stdio` | Local clients (Claude Desktop, Cursor, Crush) |
| `streamable-http` | Remote / Bifrost gateway (recommended) |
| `sse` | Remote / Bifrost gateway (legacy SSE) |

### STDIO (default)

```bash
zrok-mcp
```

### Streamable HTTP (remote)

```bash
ZROK_MCP_TRANSPORT=streamable-http ZROK_MCP_PORT=8000 zrok-mcp
```

### Docker (remote)

```bash
docker build -t zrok-mcp .
docker run -p 8000:8000 -v ~/.zrok2:/root/.zrok2 zrok-mcp
```

### With MCP Inspector

```bash
mcp dev src/zrok_mcp/server.py
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ZROK_MCP_TRANSPORT` | `stdio` | Transport: `stdio`, `streamable-http`, or `sse` |
| `ZROK_MCP_HOST` | `0.0.0.0` | Bind host (HTTP/SSE transports) |
| `ZROK_MCP_PORT` | `8000` | Bind port (HTTP/SSE transports) |

## Configuration

### Claude Desktop (stdio)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "zrok": {
      "command": "uv",
      "args": ["--directory", "/path/to/zrok-mcp", "run", "zrok-mcp"]
    }
  }
}
```

### Cursor / Crush (stdio)

Add to your crush settings or MCP config:

```json
{
  "zrok": {
    "command": "uv",
    "args": ["--directory", "/path/to/zrok-mcp", "run", "zrok-mcp"]
  }
}
```

### Bifrost AI Gateway (streamable-http)

1. Deploy zrok-mcp as a remote HTTP server (Docker, Railway, etc.)
2. In the Bifrost Web UI, go to **MCP Gateway** → **New MCP Server**
3. Select **HTTP** as the connection type
4. Enter the URL: `http://your-zrok-mcp-host:8000/mcp`
5. Set `tools_to_execute` to `["*"]` (or filter as needed)

Or via config file:

```json
{
  "mcp": {
    "mcp_clients": [
      {
        "name": "zrok",
        "connection_type": "http",
        "connection_string": "http://your-zrok-mcp-host:8000/mcp",
        "tools_to_execute": ["*"]
      }
    ]
  }
}
```

For SSE transport, use `connection_type: "sse"` and `connection_string: "http://your-zrok-mcp-host:8000/sse"`.

## Example Usage

Once configured, your AI agent can do things like:

> "Share my local server on port 3000 publicly via zrok"

The agent will call `zrok_share(action="create", target="http://localhost:3000")` and return the public URL.

> "List all my zrok shares"

The agent will call `zrok_share(action="list")` and show token, mode, target, and endpoints.

> "Create a private TCP tunnel for my database on port 5432"

The agent will call `zrok_share(action="create", share_mode="private", backend_mode="tcpTunnel", target="localhost:5432")`.

## License

MIT
