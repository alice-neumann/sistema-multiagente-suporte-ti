"""Definição dos agentes e fluxo de coordenação."""

from typing import Any, Dict, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from multiagente.config.config import Config
from multiagente.mcp.mcp_client import MCPClient
import asyncio

class TriageAgent:
    """Agente de Triagem - analisa o chamado e define os parâmetros de busca."""

    def __init__(self):
        """Inicializa o agente de triagem."""
        model_config = Config.get_model_config()
        self.llm = ChatOllama(
            model=model_config["model"],
            base_url=model_config["base_url"],
            temperature=0.3,
        )
        self.name = "Triagem"

    def plan(self, user_query: str) -> Dict[str, Any]:
        """
        Decompõe o chamado em etapas.

        Args:
            user_query: consulta do usuário

        Returns:
            plano estruturado com passos
        """
        prompt = f"""Você é um analista de triagem de suporte de TI (Nível 1).

                Sua tarefa é analisar o chamado do usuário e preparar os dados para o sistema de busca técnica:

                CHAMADO DO USUÁRIO: `{user_query}`

                Analise o chamado e forneça:
                1. Categoria do problema (ex: Hardware, Software, Rede, Banco de Dados, Acesso)
                2. Breve diagnóstico inicial do que pode estar ocorrendo
                3. Lista de 3 a 5 palavras-chave técnicas essenciais para buscar em manuais
                4. Nível de prioridade (Baixa, Média, Alta, Crítica)

                Responda em formato estruturado."""

        messages = [HumanMessage(content=prompt)]

        try:
            response = self.llm.invoke(messages)
            return {
                "status": "success",
                "agent": self.name,
                "plan": response.content,
                "query": user_query
            }
        except Exception as e:
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }

class RecoveryAgent:
    """Agente Recuperador - realiza a busca de informações na base de conhecimento RAG ."""

    def __init__(self):
        """Inicializa o agente recuperador."""
        self.mcp_client = MCPClient()
        self.name = "Recuperador"

    def retrieve(self, query: str, strategy: str = "search") -> Dict[str, Any]:
        """
        Recupera manuais e documentações relevantes.

        Args:
            query: consulta para recuperação
            strategy: estratégia de recuperação (search, context, category)

        Returns:
            informações recuperadas
        """
        if strategy == "search":
            result = asyncio.run( self.mcp_client.call_tool('search_knowledge_base',query=query, top_k=5))
        elif strategy == "context":
            result = asyncio.run(self.mcp_client.call_tool('get_context_for_query', query=query))

        elif strategy == "category":
            result = asyncio.run(self.mcp_client.call_tool('search_by_category', query=query))
        else:
            result = asyncio.run(self.mcp_client.call_tool('search_knowledge_base', query=query))

        return {
            "status": result.get("status"),
            "agent": self.name,
            "strategy": strategy,
            "result": result,
            "nr_documents": result.get("nr_documents", 0) if result.get("status") == "success" else 0
        }

class SupportAgent:
    """Agente de Suporte - resolve o chamado com base na documentação."""

    def __init__(self):
        """Inicializa o agente de suporte."""
        model_config = Config.get_model_config()
        self.llm = ChatOllama(
            model=model_config["model"],
            base_url=model_config["base_url"],
            temperature=0.0,
        )

        self.__mcp_client = MCPClient()
        self.name = "Suporte"

    def execute(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa o atendimento com o manual recuperado.

        Args:
            query: consulta a executar
            context: contexto opcional já recuperado

        Returns:
            resultado da execução
        """
        if context is None:
            context = asyncio.run(self.__mcp_client.call_tool('get_context_for_query', query=query)).get("context", "Contexto não disponível")

        prompt = f"""Você é um analista de Suporte de TI (Nível 2) experiente.

                    1 - CHAMADO ORIGINAL DO USUÁRIO: 
                    ###
                        {query}
                    ###

                    2- MANUAL RELEVANTE NA BASE DE CONHECIMENTO:
                    ###
                        {context}
                    ###
                    
                    3 - INVARIANTES DE ATENDIMENTO
                    - CONSIDERE que ### são delimitadores e tudo entre eles é parte do contexto ou da consulta.
                    - Mantenha um tom profissional, empático e resolutivo.
                    - Forneça a solução em um passo a passo numerado, claro e fácil de seguir para um usuário leigo.
                    - NÃO INVENTE comandos de terminal, IPs ou configurações que NÃO ESTEJAM NO TEXTO DE CONTEXTO.
                    - SE NÃO HOUVER RESPOSTA, RESPONDA: `Desculpe, não encontrei um procedimento padrão para este problema na nossa base de conhecimento. Por favor, escale este chamado para a equipe de infraestrutura.`
                """

        messages = [HumanMessage(content=prompt)]

        try:
            response = self.llm.invoke(messages)
            return {
                "status": "success",
                "agent": self.name,
                "response": response.content,
                "query": query,
                "context_used": len(context) > 0
            }
        except Exception as e:
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }

class MultiAgentOrchestrator:
    """Orquestrador de agentes - coordena fluxo entre agentes."""

    def __init__(self):
        """Inicializa os agentes de TI."""
        self.triage = TriageAgent()
        self.recovery = RecoveryAgent()
        self.support = SupportAgent()
        self.__mcp_client = MCPClient()

    def process_query(self, user_query: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Processa o chamado passando pelas camadas de atendimento.

        Args:
            user_query: chamado do usuário
            verbose: se True, mostra etapas intermediárias

        Returns:
            resposta final estruturada
        """
        if verbose:
            print("\n" + "=" * 60)
            print(f"NOVO CHAMADO: {user_query}")
            print("=" * 60)

        # Validar consulta
        validation = asyncio.run(self.__mcp_client.call_tool('validate_query',query = user_query))
        if validation["status"] == "invalid":
            return {
                "status": "error",
                "message": "Descrição do chamado inválida",
                "issues": validation["issues"]
            }

        # Etapa 1: Triagem
        if verbose:
            print("\n[1/3] AGENTE DE TRIAGEM - Analisando e extraindo palavras-chave...")
        triage_result = self.triage.plan(user_query)

        if verbose and triage_result.get("status") == "success":
            print(f"✓ Análise concluída:\n{triage_result['plan'][:300]}...")

        # Etapa 2: Recuperação de Manuais
        if verbose:
            print("\n[2/3] AGENTE RECUPERADOR - Buscando manuais na base de conhecimento...")
        recovery_result = self.recovery.retrieve(user_query, strategy="context")

        if verbose:
            print(f"{recovery_result['nr_documents']} manuais técnicos recuperados")

        # Obter contexto
        context = recovery_result.get("result", {}).get("context", "")

        # Etapa 3: Suporte
        if verbose:
            print("\n[3/3] AGENTE DE SUPORTE - Formulando passo a passo...")
        support_result = self.support.execute(user_query, context=context)

        if verbose and support_result.get("status") == "success":
            print(f"Resposta gerada:\n{support_result['response'][:200]}...")

        # Compilar resultado final
        final_result = {
            "status": "success",
            "query": user_query,
            "stages": {
                "triage": triage_result,
                "recovery": recovery_result,
                "support": support_result,
            },
            "final_response": support_result.get("response", ""),
        }

        return final_result
