import json

from multiagente.config.config import Config
from fastmcp import Client

class MCPClient:
    def __init__(self):
        """Inicializa cliente MCP."""
        mcp_config = Config.get_mcp_config()
        self.mcp_client = Client(mcp_config["server_url"])

    async def call_tool(self, tool_name: str, **kwargs):
        """
        Chama uma ferramenta pelo nome com argumentos fornecidos.

        Args:
            tool_name: nome da ferramenta
            **kwargs: argumentos para a ferramenta

        Returns:
            resultado da execução da ferramenta
        """
        async with self.mcp_client:
            tools = await self.mcp_client.list_tools()

            tools = [x.name for x in tools]

            if tool_name not in tools:
                return {
                    "status": "error",
                    "message": f"Ferramenta desconhecida: {tool_name}",
                    "available_tools": tools
                }

            response = await self.mcp_client.call_tool(tool_name, arguments=kwargs)
            response = response.content.pop().text
            response = json.loads(response)

            return response
