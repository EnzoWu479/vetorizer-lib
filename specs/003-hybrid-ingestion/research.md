# Research: Ingestão Híbrida (Texto/Imagem)

**Feature**: 003-hybrid-ingestion  
**Date**: 2025-12-18  
**Status**: Complete

## Overview

Esta pesquisa consolida decisões de arquitetura para permitir ingestão e busca híbrida (texto+imagem) com **concatenação determinística de vetores**, refletindo isso tanto na biblioteca quanto na UI Web existente.

---

## 1. Estratégia de representação vetorial híbrida

### Decision: Vetor híbrido por concatenação determinística (texto || imagem)

**Rationale**:
- O armazenamento atual usa uma coleção com **vetor único por ponto** e dimensão fixa (definida pelo primeiro upsert).
- Concatenação produz um vetor único compatível com o mecanismo de similaridade já utilizado.
- Mantém o modelo mental simples para o usuário: “um documento = um vetor consultável”.

**Alternatives considered**:

| Alternativa | Por que não foi escolhida |
|------------|----------------------------|
| Multi-vector / named vectors nativos do Qdrant | Exige remodelar criação de coleção e operações de busca para múltiplos vetores por ponto; aumenta a complexidade e a superfície de mudança no projeto |
| Pontos duplicados (um para texto e outro para imagem) | Dificulta agregação e pode duplicar resultados; aumenta custo de armazenamento; complica UX |

**Best practices**:
- A ordem de concatenação deve ser **fixa e documentada**.
- Metadados devem registrar as modalidades e dimensões para validação de compatibilidade na busca.

---

## 2. Compatibilidade de dimensão e estratégia de coleção

### Decision: Coleções separadas por “modo de ingestão” quando necessário

**Rationale**:
- Em coleções vetoriais com dimensão fixa, inserir vetores híbridos em uma coleção existente (somente texto ou somente imagem) causará incompatibilidade.
- A UI já opera com a ideia de “database” mapeada para collection.

**Alternatives considered**:

| Alternativa | Por que não foi escolhida |
|------------|----------------------------|
| Reconfigurar coleção existente | Mudança potencialmente destrutiva e com risco de perda; não é adequado para uma biblioteca que precisa manter compatibilidade |
| Padronizar tudo como híbrido sempre | Penaliza casos simples e obriga ingestão de modalidades que não existem |

**Best practices**:
- Persistir no metadado da “database” o modo e as dimensões (texto/imagem/híbrido).
- Validar que a busca e a ingestão só operem com vetores compatíveis.

---

## 3. Estratégia de busca na biblioteca

### Decision: Busca deve aceitar consulta por texto, por imagem, e híbrida

**Rationale**:
- A UI já possui fluxos separados de busca por texto e por imagem.
- O modo híbrido deve adicionar uma forma de fornecer **texto e imagem juntos**, produzindo o vetor de consulta com a mesma regra de concatenação.

**Best practices**:
- Erros por incompatibilidade (ex.: consulta híbrida em base somente texto) devem ser **claros e acionáveis**.

---

## 4. Atualização da UI Web

### Decision: Adicionar seleção de modo de ingestão e modo de busca, mantendo padrões atuais

**Rationale**:
- A UI atual suporta:
  - Upload CSV e seleção de coluna de conteúdo
  - Busca por texto e busca por imagem em abas
- A feature deve ampliar isso com:
  - Ingestão: seleção do modo (texto/imagem/híbrido) e seleção de colunas relevantes
  - Busca: opção de “híbrida” permitindo informar texto e imagem

**Best practices**:
- Manter consistência com o design atual (mesmo padrão de formulários, mensagens e loading states).
- Evitar exigir reprocessamento para bases existentes.

---

## 5. Referências (Context7 / Qdrant)

- O Qdrant possui suporte conceitual a **multi-vector** e arquiteturas híbridas/multi-stage; porém este plano opta por concatenação para minimizar mudanças e manter aderência ao modelo atual de coleção com vetor único.
