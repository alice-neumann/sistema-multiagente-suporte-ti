#!/usr/bin/env python3
"""
Sistema Multiagente com LLMs - Help Desk de TI

Demonstração de uma arquitetura multiagente para suporte técnico usando:
- LangChain para orquestração
- RAG com ChromaDB e embeddings para recuperação de manuais
- Modelos locais via Ollama
- Múltiplos agentes especializados (Triagem, Recuperação e Suporte)
"""

import sys
from multiagente.agents.agents import MultiAgentOrchestrator


def print_header():
    print("\n" + "=" * 70)
    print(" " * 12 + "SISTEMA DE SUPORTE DE TI MULTIAGENTE")
    print("=" * 70)
    print("\nAssistente inteligente para triagem e resolução de chamados de TI")
    print("Arquitetura ativa: Triagem → Recuperador → Suporte\n")


def print_menu():
    print("-" * 70)
    print("OPÇÕES:")
    print("  1. Abrir um novo chamado")
    print("  0. Sair do sistema")
    print("-" * 70)


def interactive_mode(orchestrator: MultiAgentOrchestrator):
    print("\n" + "=" * 70)
    print("ATENDIMENTO AO USUÁRIO")
    print("=" * 70 + "\n")

    while True:
        try:
            query = input("Descreva o problema (ou digite 0 para voltar ao menu): ").strip()

            if query == "0" or query.lower() in ["sair", "exit", "quit"]:
                break

            if not query:
                print("Por favor, digite uma descrição válida para o chamado.\n")
                continue

            print("\nIniciando o processamento do chamado...")
            result = orchestrator.process_query(query, verbose=True)

            print("\n" + "=" * 70)
            print("RESULTADO FINAL DO ATENDIMENTO")
            print("=" * 70)

            if result.get("status") == "success":
                print("\nSOLUÇÃO PROPOSTA:")
                print("-" * 70)
                print(result.get("final_response", "Nenhuma solução gerada."))
            else:
                print(f"Erro: {result.get('message', 'Erro desconhecido')}")

            print()

        except KeyboardInterrupt:
            print("\n\nAtendimento interrompido pelo usuário.")
            break

        except Exception as e:
            print(f"Erro no sistema: {str(e)}")
            print("Tente novamente.\n")

def main():
    print_header()

    try:
        orchestrator = MultiAgentOrchestrator()
    except Exception as e:
        print(f"Erro ao inicializar o sistema: {str(e)}")
        sys.exit(1)

    while True:
        print_menu()
        choice = input("Escolha uma opção (1 ou 0): ").strip()

        if choice == "1":
            interactive_mode(orchestrator)
        elif choice == "0":
            print("Encerrando o sistema...")
            sys.exit(0)
        else:
            print("Opção inválida. Digite 1 para iniciar um chamado ou 0 para sair.")

if __name__ == "__main__":
    main()
