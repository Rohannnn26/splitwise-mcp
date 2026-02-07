"""Register all MCP tools from sub-modules."""

# Import each tool module so their @mcp.tool() decorators run at import time.
import splitwise_mcp.tools.users  # noqa: F401
import splitwise_mcp.tools.groups  # noqa: F401
import splitwise_mcp.tools.friends  # noqa: F401
import splitwise_mcp.tools.expenses  # noqa: F401
import splitwise_mcp.tools.comments  # noqa: F401
import splitwise_mcp.tools.notifications  # noqa: F401
import splitwise_mcp.tools.other  # noqa: F401
