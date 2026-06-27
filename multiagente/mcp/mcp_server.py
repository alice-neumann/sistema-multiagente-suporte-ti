"""Servidor FastMCP para expor ferramentas do sistema multiagente."""

from fastmcp import FastMCP
from multiagente.mcp.tools import ToolRegistry

app = FastMCP("multiagente-tools")
registry = ToolRegistry()

@app.tool()
def search_knowledge_base(query: str, top_k: int = 3) -> dict:
    """Busca documentos relevantes na base de conhecimento."""
    return registry.search_knowledge_base(query, top_k)

@app.tool()
def get_context_for_query(query: str) -> dict:
    """Recupera contexto apropriado para uma consulta."""
    return registry.get_context_for_query(query)

@app.tool()
def search_by_category(category: str) -> dict:
    """Busca documentos por categoria específica."""
    return registry.search_by_category(category)

@app.tool()
def validate_query(query: str) -> dict:
    """Valida se uma consulta é bem formada."""
    return registry.validate_query(query)

@app.tool()
def summarize_results(results: list) -> dict:
    """Sumariza resultados de consultas."""
    return registry.summarize_results(results)

if __name__ == "__main__":
    app.run(transport="http", host="127.0.0.1", port=8000,path="/mcp")
