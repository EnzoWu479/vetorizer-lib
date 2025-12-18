# Feature Specification: Ingestão Híbrida (Texto/Imagem)

**Feature Branch**: `[003-hybrid-ingestion]`  
**Created**: 2025-12-18  
**Status**: Draft  
**Input**: User description: "Permita que ao selecionar para ingerir um dataset de documentos, faça uma ingestão hibrida com dois modelos, seja de imagem ou de texto ou ambos, em que é feita a concatenação dos vetores para que ao fazer a busca vetorizada possa realizar uma busca vetorial"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ingerir dataset com modo híbrido (Priority: P1)

Como pessoa usuária, eu quero selecionar um dataset de documentos e escolher a ingestão como texto, imagem, ou ambos, para que o sistema gere uma representação vetorial adequada para busca semântica.

**Why this priority**: Sem ingestão híbrida consistente, a busca vetorial não consegue cobrir datasets multimodais.

**Independent Test**: Pode ser testado ingerindo um dataset com documentos que tenham somente texto, somente imagem e texto+imagem, verificando que todos são aceitos e ficam disponíveis para busca vetorial.

**Acceptance Scenarios**:

1. **Given** um dataset contendo documentos com texto, **When** eu seleciono ingestão por texto, **Then** os documentos são ingeridos e ficam disponíveis para busca com consulta textual.
2. **Given** um dataset contendo documentos com imagem, **When** eu seleciono ingestão por imagem, **Then** os documentos são ingeridos e ficam disponíveis para busca com consulta por imagem.
3. **Given** um dataset contendo documentos com texto e imagem, **When** eu seleciono ingestão por ambos, **Then** o sistema gera um vetor híbrido por documento e o armazena para busca vetorial.

---

### User Story 2 - Buscar com consulta multimodal (Priority: P2)

Como pessoa usuária, eu quero pesquisar usando texto, imagem, ou ambos, para que o sistema encontre documentos relevantes independentemente do tipo de conteúdo ingerido.

**Why this priority**: A ingestão híbrida só é útil se houver um fluxo de busca que utilize o mesmo “modo” de representação vetorial.

**Independent Test**: Pode ser testado executando buscas com texto e/ou imagem e verificando que resultados retornam para documentos ingeridos em modos compatíveis.

**Acceptance Scenarios**:

1. **Given** que existem documentos ingeridos no modo texto, **When** eu busco por texto, **Then** eu recebo resultados relevantes ranqueados por similaridade.
2. **Given** que existem documentos ingeridos no modo imagem, **When** eu busco por imagem, **Then** eu recebo resultados relevantes ranqueados por similaridade.
3. **Given** que existem documentos ingeridos no modo ambos (híbrido), **When** eu busco informando texto e imagem, **Then** eu recebo resultados relevantes ranqueados por similaridade usando a consulta híbrida.

---

### User Story 3 - Previsibilidade e rastreabilidade do vetor híbrido (Priority: P3)

Como pessoa usuária, eu quero que o vetor híbrido seja composto de maneira determinística e rastreável, para que buscas repetidas e reindexações sejam consistentes.

**Why this priority**: Sem determinismo e rastreabilidade, é difícil comparar resultados, debugar e reprocessar datasets.

**Independent Test**: Pode ser testado ingerindo o mesmo dataset duas vezes sob a mesma configuração e verificando que o formato do vetor híbrido e os metadados de origem se mantêm consistentes.

**Acceptance Scenarios**:

1. **Given** um documento ingerido no modo ambos, **When** o vetor híbrido é gerado, **Then** o sistema registra quais modalidades compõem o vetor e a ordem de concatenação.

---

### Edge Cases

- O que acontece quando o dataset contém documentos mistos (alguns com imagem, outros sem) e o modo selecionado exige uma modalidade ausente?
- Como o sistema lida com documentos de imagem inválida/inalcançável durante a ingestão?
- Como o sistema lida com conteúdo textual vazio ou composto apenas por espaços?
- O que acontece quando a configuração selecionada produz vetores incompatíveis com os já armazenados no mesmo dataset/coleção de busca?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir selecionar o modo de ingestão para um dataset de documentos como:
  - somente texto
  - somente imagem
  - texto e imagem (híbrido)
- **FR-002**: O sistema DEVE suportar ingestão híbrida utilizando dois modelos de vetorização (um para texto e outro para imagem), quando o modo “texto e imagem” estiver selecionado.
- **FR-003**: Quando o modo “texto e imagem” estiver selecionado, o sistema DEVE gerar um vetor híbrido por documento por meio da concatenação determinística do vetor de texto com o vetor de imagem.
- **FR-004**: O sistema DEVE permitir busca vetorial com consulta textual, consulta por imagem, e consulta híbrida (texto+imagem), desde que compatíveis com o modo de ingestão dos documentos.
- **FR-005**: O sistema DEVE registrar nos metadados de cada documento ingerido as modalidades disponíveis (texto/imagem) e o modo efetivo usado na geração do vetor (texto, imagem, híbrido).
- **FR-006**: O sistema DEVE validar a compatibilidade entre o formato do vetor de consulta e o formato do vetor armazenado, retornando um erro claro quando a consulta não for compatível.
- **FR-007**: O sistema DEVE manter compatibilidade com ingestões existentes somente texto e somente imagem, sem exigir reprocessamento para continuar funcionando.
- **FR-008**: O sistema DEVE permitir que documentos que não possuam uma modalidade requerida sejam tratados de forma previsível (por exemplo, serem ignorados com registro de erro/contagem, ou falhar a operação), de acordo com a política configurada para ingestão.

### Key Entities *(include if feature involves data)*

- **Documento**: Item lógico do dataset contendo, opcionalmente, texto e/ou imagem, mais metadados associados.
- **Dataset**: Conjunto de documentos selecionado para ingestão e busca.
- **Modo de Ingestão**: Regra escolhida pela pessoa usuária para determinar quais modalidades serão vetorizadas e como o vetor final é produzido.
- **Vetor Híbrido**: Representação vetorial composta por múltiplas modalidades (texto e imagem) por concatenação determinística.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Dado um dataset com pelo menos 100 documentos mistos (somente texto, somente imagem e texto+imagem), a pessoa usuária consegue completar a ingestão nos três modos (texto, imagem, híbrido) e obter um resultado final com contagem de processados/ignorados/falhas.
- **SC-002**: Para um dataset ingerido no modo híbrido, uma busca híbrida (texto+imagem) retorna pelo menos 1 resultado quando existem documentos relevantes e não falha por incompatibilidade de formato de vetor.
- **SC-003**: Reingestões repetidas do mesmo dataset com a mesma configuração produzem vetores híbridos com composição determinística (ordem de concatenação invariável) e metadados indicando as modalidades usadas em 100% dos documentos processados.
- **SC-004**: Um conjunto de regressão contendo ao menos 20 casos (10 somente texto, 10 somente imagem) continua retornando resultados na busca, sem alteração de comportamento percebida pela pessoa usuária.

## Assumptions

- A ingestão de “dataset de documentos” pode conter documentos com somente texto, somente imagem, ou ambos.
- Quando o modo selecionado exigir uma modalidade ausente em um documento, o sistema deve produzir um resultado previsível e relatável (processado/ignorado/falhou), sem comportamento silencioso.
- A busca vetorial deve ser possível com pelo menos uma das modalidades (texto e/ou imagem), conforme disponibilidade do dataset.

## Dependencies

- Existência de um mecanismo de armazenamento e busca por similaridade vetorial para persistir vetores e executar consultas.
- Disponibilidade de modelos de vetorização para texto e para imagem, e capacidade de executar ambos quando o modo híbrido for selecionado.
