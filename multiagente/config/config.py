import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuração da aplicação multiagente."""

    # Modelo Local (Ollama)
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-oss:120b-cloud")
    MODEL_API_BASE = os.getenv("MODEL_API_BASE", "http://localhost:11434")

    # Embeddings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")

    # ChromaDB
    CHROMA_PATH = os.getenv("CHROMA_PATH", "../chroma_db")
    COLLECTION_NAME = "suporte_ti"

    # MCP (Model Context Protocol)
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")


    # LangGraph
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    @classmethod
    def get_model_config(cls) -> dict:
        """Retorna configuração do modelo."""
        return {
            "model": cls.MODEL_NAME,
            "base_url": cls.MODEL_API_BASE,
        }

    @classmethod
    def get_mcp_config(cls) -> dict:
        """Retorna configuração do MCP."""
        return {
            "server_url": cls.MCP_SERVER_URL,
        }