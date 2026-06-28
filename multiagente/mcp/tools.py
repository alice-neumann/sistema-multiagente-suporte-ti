"""Ferramentas para os agentes."""

from typing import Any, Dict, Optional
from multiagente.rag.rag_system import RAGSystem

class ToolRegistry:
    """Registro central de ferramentas disponíveis."""

    def __init__(self):
        self.rag_system = RAGSystem()

    def search_knowledge_base(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Busca na base de conhecimento usando RAG.

        Args:
            query: texto de consulta
            top_k: número máximo de documentos a retornar

        Returns:
            resultados da busca com relevância
        """
        try:
            results = self.rag_system.retrieve(query, top_k=top_k)

            if not results:
                return {
                    "status": "no_results",
                    "message": f"Nenhum documento encontrado para: {query}",
                    "results": []
                }

            return {
                "status": "success",
                "query": query,
                "results": results,
                "count": len(results)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao buscar: {str(e)}",
                "results": []
            }

    def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """
        Obtém contexto relevante para uma consulta.

        CORREÇÃO: get_context() agora sempre retorna dict.
        Trata explicitamente o caso sem resultados, retornando
        context="" e status="no_results" para o SupportAgent escalar.

        Args:
            query: texto de consulta

        Returns:
            contexto formatado para uso em prompts
        """
        try:
            result = self.rag_system.get_context(query)

            context = result.get("context", "")
            nr_documents = result.get("nr_documents", 0)

            if not context or nr_documents == 0:
                return {
                    "status": "no_results",
                    "query": query,
                    "context": "",
                    "nr_documents": 0,
                    "token_estimate": 0
                }

            return {
                "status": "success",
                "query": query,
                "context": context,
                "nr_documents": nr_documents,
                "token_estimate": len(context.split()) * 1.3
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao obter contexto: {str(e)}",
                "context": "",
                "nr_documents": 0
            }

    def search_by_category(self, category: str) -> Dict[str, Any]:
        """
        Busca documentos por categoria.

        Args:
            category: categoria para buscar

        Returns:
            documentos da categoria
        """
        try:
            results = self.rag_system.retrieve_by_category(category)

            if not results:
                return {
                    "status": "no_results",
                    "message": f"Nenhum documento encontrado na categoria: {category}",
                    "results": []
                }

            return {
                "status": "success",
                "category": category,
                "results": results,
                "count": len(results)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Erro ao buscar por categoria: {str(e)}",
                "results": []
            }

    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        Valida uma consulta.

        Args:
            query: texto da consulta a validar

        Returns:
            resultado da validação
        """
        issues = []

        if not query or len(query.strip()) == 0:
            issues.append("Consulta vazia")

        if len(query) < 3:
            issues.append("Consulta muito curta (mínimo 3 caracteres)")

        if len(query) > 500:
            issues.append("Consulta muito longa (máximo 500 caracteres)")

        return {
            "status": "valid" if not issues else "invalid",
            "query": query,
            "issues": issues,
            "query_length": len(query)
        }

    def summarize_results(self, results: list) -> Dict[str, Any]:
        """
        Sumariza resultados de buscas.

        Args:
            results: lista de resultados para sumarizar

        Returns:
            sumário dos resultados
        """
        if not results:
            return {
                "status": "empty",
                "message": "Nenhum resultado para sumarizar",
                "summary": ""
            }

        summary_parts = []
        for i, result in enumerate(results[:3], 1):
            if isinstance(result, dict):
                title = result.get("title", "Sem título")
                content = result.get("content", "")[:100]
                score = result.get("relevance_score", 0)
                summary_parts.append(f"{i}. {title} (relevância: {score:.2f})")
            else:
                summary_parts.append(f"{i}. {str(result)[:50]}...")

        return {
            "status": "success",
            "total_results": len(results),
            "summary": "\n".join(summary_parts),
            "details": summary_parts
        }