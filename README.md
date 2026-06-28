# Sistema Multiagente para Suporte de TI

## Integrantes da Equipe

- Alice Neumann | 190523
- Gabriel Trentini Teixeira | 202578

## Descrição do Problema

Equipes de Help Desk lidam diariamente com um alto volume de chamados de suporte, sendo grande parte deles ocorrências simples e repetitivas, como por exemplo: 

- Redefinição de senhas

- Problemas de conectividade

- Dúvidas sobre ferramentas

Sem um mecanismo automatizado de triagem, analistas qualificados acabam consumindo tempo com demandas que não exigem intervenção especializada, criando gargalos que atrasam a resolução de incidentes críticos e limitando o suporte ao horário comercial.

## Objetivo da Solução

Desenvolver um sistema multiagente inteligente capaz de receber, classificar e resolver de forma autônoma chamados de suporte de baixa complexidade, oferecendo respostas padronizadas aos usuários sem necessidade de intervenção humana. Casos que exijam análise mais aprofundada serão escalados automaticamente para a equipe de TI, permitindo que os analistas concentrem seus esforços onde realmente fazem diferença.

## Arquitetura Multiagente
```
┌─────────────────────────────────────────────────────────────┐
│                    CONSULTA DO USUÁRIO                      │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 1. TRIAGEM                                                             │
│    Papel: Lê o chamado do usuário e traça a estratégia de busca.       │
│    Entrada: Reclamação do usuário (ex: "Estou sem internet").          |
|    Saída: Um plano de ação detalhado do que precisa ser pesquisado.    │
└────────────┬───────────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 2. RECUPERADOR                                                           │
│    Papel: Executa a busca na base de dados corporativa.                  │
│    Entrada: O plano de ação do Agente 1.                                 │
│    Saída: Os trechos dos manuais técnicos relevantes para o problema.    │
└────────────┬─────────────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│ 3. SUPORTE                                                                     │
│    Papel: Analisa os manuais e redige o passo a passo final para o usuário.    │
│    Entrada: Os documentos recuperados pelo Agente 2.                           |
│    Saída: A solução técnica formatada e amigável para o usuário final.         | 
└────────────┬───────────────────────────────────────────────────────────────────┘
             │
             ▼
       RESPOSTA FINAL
```

## Estrutura do Projeto

O código-fonte foi organizado de forma modular, separando as responsabilidades de orquestração, acesso a dados (RAG) e a camada de ferramentas (MCP). Abaixo está a visão geral da estrutura de diretórios e arquivos:

```text
sistema-multiagente-suporte-ti/
│
├── multiagente/                  # Pacote principal 
│   │
│   ├── agents/                   # Lógica de inteligência e orquestração
│   │   ├── __init__.py
│   │   └── agents.py             # Definição dos agentes (Triagem, Recuperador e Suporte)
│   │
│   ├── config/                   # Parâmetros e configurações globais
│   │   ├── __init__.py
│   │   └── config.py             # Definição do modelo local, caminhos de diretórios e URLs
│   │
│   ├── mcp/                      # Camada do MCP
│   │   ├── __init__.py
│   │   ├── mcp_client.py         # Cliente para os agentes chamarem as ferramentas
│   │   ├── mcp_server.py         # Servidor FastMCP que expõe os recursos do RAG na porta 8000
│   │   └── tools.py              # Registro das ferramentas de busca e validação
│   │
│   ├── rag/                      # Processamento e busca de dados
│   │   ├── __init__.py
│   │   ├── knowledge_base.py     # Base de documentos contendo os manuais 
│   │   └── rag_system.py         # Lógica do banco ChromaDB, chunking e geração de embeddings
│   │
│   └── __main__.py               # Ponto de entrada do sistema (menu interativo do terminal)
│
├── README.md                     
└── requirements.txt              # Dependências do projeto
```

## Tools e Integração MCP

O sistema utiliza o padrão Model Context Protocol (MCP) para criar uma ponte segura e padronizada entre os agentes e a base de dados. Essa abordagem separa a inteligência dos modelos da execução de código, funcionando em duas frentes:

* **Servidor MCP (`mcp_server.py`)**: Construído com `FastMCP`, roda localmente e expõe as capacidades de busca e validação do sistema com as tools executáveis.
* **Cliente MCP (`mcp_client.py`)**: Integrado aos agentes, gerencia as requisições ao servidor e converte as respostas para serem processadas pela IA.

Ferramentas disponíveis (`tools.py`) para uso dos agentes:

* **`validate_query`**: Verifica se o chamado de suporte é válido (entre 3 e 500 caracteres).
* **`search_knowledge_base`**: Executa a busca semântica na base RAG e retorna os manuais mais apropriados ao problema.
* **`get_context_for_query`**: Agrupa o texto de vários manuais relevantes e estima o consumo de tokens para o prompt.
* **`search_by_category`**: Filtra a documentação técnica por categorias (ex: redes, software, hardware).
* **`summarize_results`**: Gera um resumo dos 3 principais documentos encontrados para agilizar o processamento do agente final.
  
## Estratégia RAG (Retrieval-Augmented Generation)

O sistema utiliza RAG para garantir respostas precisas e baseadas somente na documentação interna:

* **Base de Conhecimento:** Dados estáticos e locais (`knowledge_base.py`) que simulam procedimentos operacionais (POPs) de um Help Desk corporativo.
* **Processamento (Chunking):** Divisão dos manuais em blocos de 300 caracteres (com sobreposição de 60) para a IA não perder o contexto.
* **Busca Semântica:** Conversão dos textos em vetores matemáticos para recuperar os manuais mais relevantes.

## Embeddings e Armazenamento Vetorial

Tecnologias utilizadas para transformar os textos e permitir a busca inteligente por contexto de forma local:

* **Modelo de Embeddings:** `sentence-transformers`
* **Banco de Dados Vetorial:** `ChromaDB`
* **Métrica de Recuperação (Retrieval):** Distância do cosseno (`cosine`)

## Tecnologias Modelo utilizado 
* **Linguagem:** Python
* **Modelo Local:** llama2
* **Framework de Execução:** Ollama
* **Infraestrutura:** local e offline (CPU/GPU própria)

## Dependências do Projeto

Principais bibliotecas utilizadas (`requirements.txt`):

* **Orquestração e Agentes:** `langchain`, `langchain-community`, `langchain-ollama`, `langchainhub`, `langgraph`
* **RAG e Vetorização:** `chromadb`, `sentence-transformers`
* **Servidor MCP:** `fastmcp`
* **Utilitários:** `pydantic`, `numpy`, `python-dotenv`, `requests`

## Instruções para instalação e execução

### Pré-requisitos
- Python 3.10+
- Ollama

### 1. Instalar o Ollama e o modelo

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama2
ollama serve 
```

**Windows:**
```cmd
irm https://ollama.com/install.ps1 | iex
ollama pull llama2
ollama serve
```

### 2. Instalar dependências

**Linux:**
```bash
cd sistema-multiagente-suporte-ti
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

**Windows:**
```cmd
cd sistema-multiagente-suporte-ti
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Executar o sistema

O sistema requer **dois terminais abertos**:

**Terminal 1 — Servidor MCP:**
```bash
python -m multiagente.mcp.mcp_server
```

**Terminal 2 — Sistema:**
```bash
python -m multiagente
```

## Exemplos de Uso
### Exemplo 1: redefinição de senha
<img width="500" height="623" alt="image" src="https://github.com/user-attachments/assets/f6bff1ac-3e9e-4bb9-bec2-11027fa826cb" />

### Exemplo 2: computador lento
<img width="600" height="489" alt="image" src="https://github.com/user-attachments/assets/04fc3307-56bd-4721-822f-fc052c30f6c0" />

