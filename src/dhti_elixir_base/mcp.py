from mcp.server.fastmcp import FastMCP


class BaseMCPServer(FastMCP):
    """Base class for MCP servers, extending FastMCP for custom functionality."""

    def __init__(self, name: str | None = None):
        self._name = name or "BaseMCPServer"
        super().__init__(name=self._name)

    @property
    def name(self):
        """Return the name of this MCP server instance."""
        return self._name

