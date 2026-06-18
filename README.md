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
│ 1. PLANEJADOR - Analista de Triagem                                    │
│    Papel: Lê o chamado do usuário e traça a estratégia de busca.       │
│    Entrada: Reclamação do usuário (ex: "Estou sem internet").          |
|    Saída: Um plano de ação detalhado do que precisa ser pesquisado.    │
└────────────┬───────────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 2. RECUPERADOR - Busca de Manuais                                        │
│    Papel: Executa a busca na base de dados corporativa.                  │
│    Entrada: O plano de ação do Agente 1.                                 │
│    Saída: Os trechos dos manuais técnicos relevantes para o problema.    │
└────────────┬─────────────────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│ 3. EXECUTOR - Ténico de Suporte N2                                             │
│    Papel: Analisa os manuais e redige o passo a passo final para o usuário.    │
│    Entrada: Os documentos recuperados pelo Agente 2.                           |
│    Saída: A solução técnica formatada e amigável para o usuário final.         | 
└────────────┬───────────────────────────────────────────────────────────────────┘
             │
             ▼
       RESPOSTA FINAL
```

## Dependências do Projeto
## Instruções para instalação e execução
## Exemplos de Uso