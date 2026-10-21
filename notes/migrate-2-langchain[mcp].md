# Migrate to `langchain[mcp]`

This repository has been migrated away from `langchain-mcp-adapters` to `langchain[mcp]`.

## What changed

- Replaced the project dependency `langchain-mcp-adapters` with `langchain[mcp]`.
- Updated `BaseAgent` MCP client integration to use `langchain.mcp.MCPAdapter`.
- Preserved compatibility with the previous MCP config shape by normalizing:
  - legacy: `{"server": {"transport": "...", ...}}`
  - new: `{"mcpServers": {"server": {...}}}`
- Updated MCP server usage for `mcp` v2 (`mcp.server.mcpserver.MCPServer`), including `BaseChain.get_chain_as_mcp_tool()` and `BaseMCPServer`.

## Compatibility notes

- Existing code that passes legacy MCP config dictionaries to `BaseAgent` continues to work.
- Existing tests for chain/agent behavior continue to pass with the new dependency model.
