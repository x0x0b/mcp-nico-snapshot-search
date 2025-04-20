# MCP Nicovideo Snapshot Search

This project provides an MCP server for searching videos on Nicovideo using the [Snapshot Search API](https://site.nicovideo.jp/search-api-docs/snapshot).

## Example Configuration for MCP Server

```json
{
  "mcpServers": {
    "mcp-nico-snapshot-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/owner/dev/mcp-nico-snapshot-search",
        "run",
        "main.py"
      ]
    }
  }
}
```

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
