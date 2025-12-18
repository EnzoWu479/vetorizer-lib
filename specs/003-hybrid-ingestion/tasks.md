# Tasks: Ingestão Híbrida (Texto/Imagem)

**Input**: Design documents from `/specs/003-hybrid-ingestion/`
**Prerequisites**: `specs/003-hybrid-ingestion/plan.md`, `specs/003-hybrid-ingestion/spec.md`, `specs/003-hybrid-ingestion/research.md`, `specs/003-hybrid-ingestion/data-model.md`, `specs/003-hybrid-ingestion/contracts/openapi.yaml`

**Tests**: Incluídos (a constituição do projeto exige testes; priorizar mocks para execução rápida).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar base técnica para implementar as histórias sem refatoração desnecessária.

- [x] T001 Verificar toolchain e dependências do projeto em pyproject.toml (repo root: pyproject.toml)
- [x] T002 Criar utilitário de composição de vetores híbridos com type hints e docstring em vetorizer_lib/models (vetorizer_lib/models/hybrid.py)
- [x] T003 [P] Criar fixtures de teste reutilizáveis para vetores e documentos em tests/conftest.py (tests/conftest.py)
- [x] T004 [P] Definir stubs/mocks para embedders de texto e imagem para testes rápidos (tests/unit/test_mocks_embedders.py)


---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infra de validação/compatibilidade de dimensões e contratos internos para suportar texto/imagem/híbrido.

- [x] T005 Implementar enum/modo de ingestão e modo de busca (text/image/hybrid) em modelos compartilhados (vetorizer_lib/models/config.py)
- [x] T006 Implementar validação de compatibilidade de vetor (dimensão esperada por modo) como função pura (vetorizer_lib/models/hybrid.py)
- [x] T007 Implementar concatenação determinística (texto || imagem) e metadados de composição (vetorizer_lib/models/hybrid.py)
- [x] T008 Atualizar modelo Document para suportar metadados de modalidades usadas, sem quebrar APIs existentes (vetorizer_lib/models/document.py)
- [x] T009 Criar exceção específica para incompatibilidade de vetor/modalidade (vetorizer_lib/exceptions.py)

---

## Phase 3: User Story 1 - Ingerir dataset com modo híbrido (Priority: P1) MVP

**Goal**: Permitir ingestão por texto, por imagem, ou híbrida (texto+imagem) com vetor concatenado.

**Independent Test**: Ingerir um CSV de teste contendo linhas com texto+imagem em modo híbrido e validar que:
- a ingestão conclui,
- o vetor salvo tem dimensão esperada,
- a operação não quebra ingestões existentes.

### Tests for User Story 1

- [x] T010 [P] [US1] Unit test da concatenação determinística e validação de dimensão (tests/unit/test_hybrid_vector.py)
- [ ] T011 [P] [US1] Unit test do cliente: gera embedding híbrido chamando ambos embedders via mocks (tests/unit/test_client_hybrid_ingest.py)
- [ ] T012 [P] [US1] Integration test do fluxo de upload híbrido na API usando TestClient + mocks (tests/integration/web/test_upload_hybrid.py)

### Implementation for User Story 1

- [x] T013 [US1] Adicionar API pública de ingestão híbrida no VetorizerClient (vetorizer_lib/client.py)
- [x] T014 [US1] Adicionar suporte a dois modelos no VetorizerClient para modo híbrido (texto e imagem) sem quebrar init atual (vetorizer_lib/client.py)
- [x] T015 [US1] Implementar leitura de CSV com duas colunas (texto e imagem) para modo híbrido (vetorizer_lib/ingest/csv.py)
- [x] T016 [US1] Implementar orquestração de embedding híbrido e atribuição ao Document (vetorizer_lib/client.py)
- [x] T017 [US1] Garantir que upsert em Qdrant use o vetor híbrido e registre metadados de modalidade (vetorizer_lib/stores/qdrant.py)
- [x] T018 [US1] Estender MetadataStore para persistir `mode` e dimensões por base (vetorizer_lib/web/models/metadata_store.py)
- [x] T019 [US1] Atualizar schema VectorDatabaseResponse para expor `mode` e dimensões por modalidade (vetorizer_lib/web/models/schemas.py)
- [x] T020 [US1] Atualizar schema UploadJobResponse para registrar colunas usadas e modo (vetorizer_lib/web/models/schemas.py)
- [x] T021 [US1] Atualizar rota de upload para aceitar `ingest_mode`, `text_column`, `image_column` e validar combinações (vetorizer_lib/web/routes/upload.py)
- [x] T022 [US1] Atualizar upload_service.process_csv para suportar ingestão híbrida e chamar o método do cliente correto (vetorizer_lib/web/services/upload_service.py)
- [x] T023 [US1] Atualizar template de upload para permitir selecionar modo e colunas (incluindo coluna de imagem) (vetorizer_lib/web/templates/partials/upload_form.html)

**Checkpoint**: US1 entrega ingestão híbrida end-to-end pela UI e API.

---

## Phase 4: User Story 2 - Buscar com consulta multimodal (Priority: P2)

**Goal**: Adicionar busca híbrida (texto+imagem) e manter busca por texto/imagem existente.

**Independent Test**: Após ingestão híbrida, executar busca híbrida com texto+imagem e obter ao menos 1 resultado, além de manter busca por texto e imagem funcionando.

### Tests for User Story 2

- [ ] T024 [P] [US2] Unit test do cliente: busca híbrida gera vetor de consulta compatível (tests/unit/test_client_hybrid_search.py)
- [ ] T025 [P] [US2] Integration test do endpoint /api/search/hybrid com upload de imagem + texto (tests/integration/web/test_search_hybrid.py)
- [ ] T026 [P] [US2] Regressão: testes de busca por texto e por imagem continuam passando (tests/integration/web/test_search_regression.py)

### Implementation for User Story 2

- [x] T027 [US2] Adicionar API pública de busca híbrida no VetorizerClient (vetorizer_lib/client.py)
- [x] T028 [US2] Implementar validação de compatibilidade de consulta vs base (modo/dimensão) com erro acionável (vetorizer_lib/client.py)
- [x] T029 [US2] Criar rota /api/search/hybrid (multipart: texto+imagem) (vetorizer_lib/web/routes/search.py)
- [x] T030 [US2] Implementar search_service.search_hybrid para orquestrar busca híbrida por database (vetorizer_lib/web/services/search_service.py)
- [x] T031 [US2] Atualizar UI de busca para oferecer opção híbrida (novo tab ou seção) (vetorizer_lib/web/templates/search.html)
- [x] T032 [US2] Criar template parcial para formulário de busca híbrida (vetorizer_lib/web/templates/partials/hybrid_search.html)

**Checkpoint**: US2 entrega busca híbrida sem quebrar fluxos existentes.

---

## Phase 5: User Story 3 - Previsibilidade e rastreabilidade do vetor híbrido (Priority: P3)

**Goal**: Tornar composição e rastreabilidade do vetor híbrido explícitas e verificáveis.

**Independent Test**: Reingerir o mesmo dataset com a mesma configuração e validar que:
- dimensões registradas são as mesmas,
- metadados de modalidades e ordem de concatenação existem,
- comportamento é determinístico sob mocks.

### Tests for User Story 3

- [ ] T033 [P] [US3] Unit test de rastreabilidade de metadados (modalidades, ordem) no payload upsertado (tests/unit/test_qdrant_payload_modalities.py)
- [ ] T034 [P] [US3] Integration test: reingestão com mesma configuração gera metadados consistentes (tests/integration/web/test_reingest_determinism.py)

### Implementation for User Story 3

- [x] T035 [US3] Persistir em metadata do documento quais modalidades foram usadas e ordem de concatenação (vetorizer_lib/client.py)
- [x] T036 [US3] Garantir que UI exiba modo/dimensões na tela de gerenciamento (vetorizer_lib/web/templates/manage.html)
- [x] T037 [US3] Ajustar serialização no MetadataStore para manter compatibilidade e incluir novos campos (vetorizer_lib/web/models/metadata_store.py)

**Checkpoint**: US3 entrega rastreabilidade visível e verificável.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Robustez, documentação e qualidade geral.

- [ ] T038 [P] Atualizar README com exemplos de uso de ingestão/busca híbrida (README.md)
- [ ] T039 [P] Atualizar OpenAPI docs (se necessário) para refletir endpoints e campos finais (specs/003-hybrid-ingestion/contracts/openapi.yaml)
- [ ] T040 Padronizar mensagens de erro acionáveis para incompatibilidade de modo/dimensão na UI (vetorizer_lib/web/routes/search.py)
- [ ] T041 [P] Rodar lint (ruff) e corrigir issues no código modificado (repo root: pyproject.toml)
- [ ] T042 Rodar mypy strict e corrigir issues (repo root: pyproject.toml)
- [ ] T043 Rodar suíte de testes específica do módulo web e unit tests do híbrido (repo root: tests/)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)** -> **Phase 2 (Foundational)** -> **Phase 3 (US1)** -> **Phase 4 (US2)** -> **Phase 5 (US3)** -> **Phase 6 (Polish)**

### User Story Dependencies

- **US1 (P1)**: depende de Foundational (validações e composição)
- **US2 (P2)**: depende de US1 (precisa de base híbrida para exercitar)
- **US3 (P3)**: depende de US1 (metadados e rastreabilidade da ingestão)

### Parallel Opportunities

- [P] tasks podem ser executadas em paralelo (arquivos distintos, sem dependências diretas).

## Suggested MVP Scope

- Implementar até o **Checkpoint da US1** (T010–T023), garantindo ingestão híbrida funcional.
