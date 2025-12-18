# Quickstart: Ingestão Híbrida (Texto/Imagem)

**Feature**: 003-hybrid-ingestion  
**Date**: 2025-12-18

## Objetivo

Permitir que você:
- Ingerir um dataset selecionando o modo: **texto**, **imagem** ou **híbrido** (texto+imagem).
- Buscar com consulta compatível: **texto**, **imagem** ou **híbrida**.

## Pré-requisitos

- Ambiente Python compatível com o projeto.
- Qdrant configurado (local por path ou remoto por URL), conforme configuração da UI.

## Rodar a UI

- Inicie o servidor web via CLI do projeto.
- Acesse:
  - Home: `http://127.0.0.1:8000/`
  - Docs API: `http://127.0.0.1:8000/api/docs`

## Ingestão (pela UI)

1. Na página inicial, faça upload do CSV.
2. Selecione o modo de ingestão:
   - `texto`
   - `imagem`
   - `híbrido`
3. Selecione as colunas necessárias:
   - texto: coluna de conteúdo textual
   - imagem: coluna que referencia a imagem
   - híbrido: ambas
4. Aguarde a conclusão do upload/ingestão e valide que a base aparece como pronta.

## Busca (pela UI)

- Use a aba “Text Search” para consultas textuais.
- Use a aba “Image Search” para consultas por imagem.
- Use a opção de busca híbrida (quando disponível) para enviar texto e imagem juntos.

## Verificação rápida (API)

- Health check:
  - `GET /api/health`

> Observação: Os detalhes de endpoints e payloads específicos estão documentados em `contracts/`.
