# zrok-mcp

An [MCP server](https://modelcontextprotocol.io/) for [zrok](https://zrok.io/) — the open-source secure sharing platform built on OpenZiti. Lets AI agents manage zrok tunnels, shares, and access programmatically.

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

### STDIO (for Claude Desktop, Cursor, etc.)

```bash
zrok-mcp
```

### With MCP Inspector

```bash
mcp dev src/zrok_mcp/server.py
```

## Configuration

### Claude Desktop

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

### Cursor / Crush

Add to your crush settings or MCP config:

```json
{
  "zrok": {
    "command": "uv",
    "args": ["--directory", "/path/to/zrok-mcp", "run", "zrok-mcp"]
  }
}
```

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
