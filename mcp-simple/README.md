# MCP Simple

## Setup

1. Copy [.env.example](.env.example) to `.env` and fill in the values.
2. Install uv

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
3. Install dependencies

    ```bash
    uv sync
    ```

## Run the server with MCP Inspector

```bash
uv run mcp dev server.py
```
## Connect MCP server with Cursor
1. modify the [mcp.json](mcp.json) file to include the MCP server directory:
```json
{
    "mcpServers": {
        "job-scraper": {
            "command": "uv",
            "args": [
                "run",
                "--directory",
                "<path-to-project>",
                "server.py"
            ]
        }
    }
}
```
2. Add it to `~/.cursor/mcp.json` file

## Run the client locally

```bash
uv run client.py -q "what are the opening jobs at factored for software engineer?"