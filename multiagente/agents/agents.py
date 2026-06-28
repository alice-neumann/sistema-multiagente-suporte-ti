"""Definição dos agentes e fluxo de coordenação."""

from typing import Any, Dict, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from multiagente.config.config import Config
from multiagente.mcp.mcp_client import MCPClient
import asyncio


# Valores de context que indicam ausência de documentação relevante
_SEM_CONTEXTO_VALORES = {
    "",
    "sem_informacao",
    "contexto não disponível",
    "nenhum documento relevante encontrado na base.",
}


def _sem_contexto(context: Optional[str]) -> bool:
    """Retorna True se o contexto está vazio ou indica ausência de documentação."""
    if not context:
        return True
    return context.strip().lower() in _SEM_CONTEXTO_VALORES


def _limpar_resposta(text: str) -> str:
    """
    Remove artefatos de vazamento de prompt da saída do LLM.
    O llama2 tende a repetir rótulos do prompt no início da resposta.
    """
    labels = [
        "RESPOSTA:", "RESPONSE:", "OUTPUT:", "SAÍDA:",
        "CHAMADO DO USUÁRIO:", "DOCUMENTAÇÃO TÉCNICA:",
        "INSTRUÇÕES IMPORTANTES:", "INSTRUÇÕES:",
        "FORMULÁRIO:", "CATEGORIA:",
    ]
    result = text.strip()
    for label in labels:
        if result.upper().startswith(label.upper()):
            result = result[len(label):].strip()
    return result


class TriageAgent:
    """Agente de Triagem - analisa o chamado e define os parâmetros de busca."""

    def __init__(self):
        """Inicializa o agente de triagem."""
        model_config = Config.get_model_config()
        self.llm = ChatOllama(
            model=model_config["model"],
            base_url=model_config["base_url"],
            temperature=0.1,
            stop=model_config.get("stop", []),
        )
        self.name = "Triagem"

    def plan(self, user_query: str) -> Dict[str, Any]:
        """
        Classifica o chamado com base em um template rígido.

        Args:
            user_query: consulta do usuário

        Returns:
            plano estruturado com passos
        """
        # llama2: SystemMessage separada é mais eficaz para forçar idioma
        # do que colocar a instrução dentro do HumanMessage.
        # O template rígido de formulário evita alucinação — o modelo preenche
        # campos fixos em vez de gerar texto livre.
        system = SystemMessage(content=(
            "Você é um agente de triagem de suporte de TI brasileiro. "
            "Responda SEMPRE e SOMENTE em português do Brasil. "
            "Nunca use inglês, nem parcialmente."
        ))

        prompt = (
            f"Classifique o chamado preenchendo o formulário abaixo.\n"
            f"Use APENAS as informações do chamado. Não invente nada.\n\n"
            f"Chamado: {user_query}\n\n"
            f"Preencha exatamente assim:\n"
            f"CATEGORIA: <Rede, Software, Hardware, Acesso, Banco de Dados ou Outro>\n"
            f"PALAVRAS_CHAVE: <3 a 5 termos técnicos, separados por vírgula>\n"
            f"PRIORIDADE: <Baixa, Média, Alta ou Crítica>\n"
            f"RESUMO: <uma frase descrevendo o problema>\n\n"
            f"Responda em português do Brasil:"
        )

        messages = [system, HumanMessage(content=prompt)]

        try:
            response = self.llm.invoke(messages)
            return {
                "status": "success",
                "agent": self.name,
                "plan": _limpar_resposta(response.content),
                "query": user_query
            }
        except Exception as e:
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }


class RecoveryAgent:
    """Agente Recuperador - realiza a busca de informações na base de conhecimento RAG."""

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
            result = asyncio.run(self.mcp_client.call_tool("search_knowledge_base", query=query, top_k=5))
        elif strategy == "context":
            result = asyncio.run(self.mcp_client.call_tool("get_context_for_query", query=query))
        elif strategy == "category":
            result = asyncio.run(self.mcp_client.call_tool("search_by_category", query=query))
        else:
            result = asyncio.run(self.mcp_client.call_tool("search_knowledge_base", query=query))

        return {
            "status": result.get("status"),
            "agent": self.name,
            "strategy": strategy,
            "result": result,
            "nr_documents": result.get("nr_documents", 0) if result.get("status") == "success" else 0
        }


class SupportAgent:
    """Agente de Suporte - resolve o chamado com base na documentação ou escala para TI."""

    # Mensagem padrão de escalada — usada quando não há documentação relevante.
    # Definida como constante para garantir consistência e evitar variação do LLM.
    _RESPOSTA_ESCALADA = (
        "Olá! Seu chamado foi registrado e será encaminhado para nossa equipe "
        "especializada de TI, pois requer análise mais aprofundada.\n\n"
        "Você será contatado em até 4 horas úteis.\n"
        "Para urgências, entre em contato pelo ramal 1234 ou pelo e-mail: ti@empresa.com."
    )

    def __init__(self):
        """Inicializa o agente de suporte."""
        model_config = Config.get_model_config()
        self.llm = ChatOllama(
            model=model_config["model"],
            base_url=model_config["base_url"],
            temperature=0.0,
            stop=model_config.get("stop", []),
        )
        self.__mcp_client = MCPClient()
        self.name = "Suporte"

    def execute(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Executa o atendimento com o manual recuperado.

        Fluxo binário:
        - COM contexto relevante -> LLM gera passo a passo
        - SEM contexto relevante -> escalada automática, sem chamar o LLM

        Args:
            query: consulta a executar
            context: contexto opcional já recuperado pelo RecoveryAgent

        Returns:
            resultado da execução
        """
        # Busca contexto se não foi fornecido pelo orquestrador
        if context is None:
            result = asyncio.run(self.__mcp_client.call_tool("get_context_for_query", query=query))
            context = result.get("context", "")

        # ESCALADA AUTOMÁTICA: sem contexto relevante, não chama o LLM.
        # Isso evita que o modelo alucine soluções ou vire chatbot.
        if _sem_contexto(context):
            return {
                "status": "success",
                "agent": self.name,
                "response": self._RESPOSTA_ESCALADA,
                "query": query,
                "context_used": False,
                "escalated": True
            }

        # COM contexto: llama2 responde melhor com SystemMessage separada +
        # prompt curto e direto + "Responda em português do Brasil:" no final.
        system = SystemMessage(content=(
            "Você é um agente de Suporte de TI brasileiro. "
            "Responda SEMPRE e SOMENTE em português do Brasil. "
            "Nunca use inglês. Sua resposta é definitiva — não faça perguntas."
        ))

        prompt = (
            f"Chamado do usuário: {query}\n\n"
            f"Documentação técnica disponível:\n{context}\n\n"
            f"Com base SOMENTE na documentação acima, escreva um passo a passo numerado "
            f"para resolver o chamado. Não invente comandos, IPs ou configurações que não "
            f"estejam na documentação. Não faça perguntas. Comece com 'Olá!' e termine com: "
            f"'Caso o problema persista, entre em contato com a equipe de TI pelo ramal 1234.'\n\n"
            f"Responda em português do Brasil:"
        )

        messages = [system, HumanMessage(content=prompt)]

        try:
            response = self.llm.invoke(messages)
            return {
                "status": "success",
                "agent": self.name,
                "response": _limpar_resposta(response.content),
                "query": query,
                "context_used": True,
                "escalated": False
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
        validation = asyncio.run(self.__mcp_client.call_tool("validate_query", query=user_query))
        if validation["status"] == "invalid":
            return {
                "status": "error",
                "message": "Descrição do chamado inválida",
                "issues": validation["issues"]
            }

        # Etapa 1: Triagem
        if verbose:
            print("\n[1/3] AGENTE DE TRIAGEM - Classificando o chamado...")
        triage_result = self.triage.plan(user_query)

        if verbose and triage_result.get("status") == "success":
            print(f"Classificação:\n{triage_result['plan']}")

        # Etapa 2: Recuperação de Manuais
        if verbose:
            print("\n[2/3] AGENTE RECUPERADOR - Buscando manuais na base de conhecimento...")
        recovery_result = self.recovery.retrieve(user_query, strategy="context")

        nr_docs = recovery_result.get("nr_documents", 0)
        if verbose:
            print(f"{nr_docs} manual(is) técnico(s) recuperado(s)")

        # Extrai o contexto para passar diretamente ao SupportAgent
        context = recovery_result.get("result", {}).get("context", "")

        # Etapa 3: Suporte
        if verbose:
            if _sem_contexto(context):
                print("\n[3/3] AGENTE DE SUPORTE - Nenhuma documentação relevante. Escalando...")
            else:
                print("\n[3/3] AGENTE DE SUPORTE - Formulando passo a passo...")

        support_result = self.support.execute(user_query, context=context)

        if verbose and support_result.get("status") == "success":
            escalado = support_result.get("escalated", False)
            status_label = "ESCALADO PARA TI" if escalado else "RESOLVIDO"
            print(f"Status: {status_label}")

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
            "escalated": support_result.get("escalated", False),
        }

        return final_result