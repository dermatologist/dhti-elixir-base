from mcp.server.mcpserver import MCPServer


class BaseMCPServer(MCPServer):
    """Base class for MCP servers, extending MCPServer for custom functionality."""

    def __init__(self, name: str | None = None):
        self._name = name or "BaseMCPServer"
        super().__init__(name=self._name)

    @property
    def name(self):
        """Return the name of this MCP server instance."""
        return self._name
