# Feature Specification: Ingestão Híbrida (Texto/Imagem)

**Feature Branch**: `[003-hybrid-ingestion]`  
**Created**: 2025-12-18  
**Status**: Draft  
**Input**: User description: "Permita que ao selecionar para ingerir um dataset de documentos, faça uma ingestão hibrida com dois modelos, seja de imagem ou de texto ou ambos, em que é feita a concatenação dos vetores para que ao fazer a busca vetorizada possa realizar uma busca vetorial"

## User Scenarios & Testing *(mandatory)*

### User Story 0 - Criar novo banco de dados com ingestão híbrida na UI (Priority: P0)

Como pessoa usuária, eu quero criar um novo banco de dados na home page da UI selecionando o modo de ingestão (texto/imagem/híbrido) e fazer upload de documentos em uma única operação, para que eu possa começar a usar o sistema rapidamente.

**Why this priority**: É o ponto de entrada principal para usuários da UI utilizarem a funcionalidade de ingestão híbrida. Sem esta interface, usuários não conseguem criar bancos de dados com os diferentes modos de ingestão.

**Independent Test**: Pode ser testado acessando a home page da UI, clicando em criar novo banco de dados, selecionando cada modo (texto/imagem/híbrido), fazendo upload de arquivos, e verificando que o banco é criado e os documentos são ingeridos.

**Acceptance Scenarios**:

1. **Given** estou na home page da UI, **When** clico em "Criar Novo Banco de Dados", **Then** um modal/formulário é exibido com campos para nome do banco, seleção de modo, área de upload e configurações avançadas (colapsadas).
2. **Given** estou no formulário de criação de banco, **When** seleciono modo "Texto e Imagem (Híbrido)" via radio button, **Then** o sistema configura embedders para texto e imagem com valores padrão.
3. **Given** estou no formulário de criação com modo híbrido, **When** expando a seção "Avançado", **Then** posso personalizar os modelos de embedder para texto e imagem e seus parâmetros.
4. **Given** completei o formulário e fiz upload de arquivos, **When** submeto a criação, **Then** o sistema valida os arquivos, exibe resumo detalhado ("X processados, Y ignorados, Z falhas" com motivos), e permite prosseguir ou cancelar.
5. **Given** a validação mostra arquivos incompatíveis, **When** escolho prosseguir, **Then** o banco é criado e apenas os documentos compatíveis são ingeridos, com relatório final de processamento.

---

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
- O que acontece se o usuário tenta criar um banco com um nome que já existe?
- Como o sistema lida com falha de upload de arquivo grande ou timeout durante o upload?
- O que acontece se o usuário fecha o modal durante o upload/processamento?
- Como o sistema lida quando TODOS os arquivos carregados são incompatíveis com o modo selecionado?

## Requirements *(mandatory)*

### Functional Requirements
#### UI Requirements

- **FR-UI-001**: A home page da UI DEVE exibir uma opção visível para "Criar Novo Banco de Dados".
- **FR-UI-002**: Ao clicar em "Criar Novo Banco de Dados", o sistema DEVE exibir um modal/formulário contendo:
  - Campo de texto para nome do banco de dados (obrigatório)
  - Seleção de modo via radio buttons com três opções explícitas: "Somente Texto", "Somente Imagem", "Texto e Imagem (Híbrido)"
  - Área de upload de arquivos/documentos
  - Seção "Avançado" (colapsada por padrão) para customização de modelos embedder e parâmetros
- **FR-UI-003**: O sistema DEVE fornecer valores padrão sensatos para os modelos embedder de texto e imagem, permitindo criação rápida sem necessidade de configuração avançada.
- **FR-UI-004**: Na seção "Avançado", o sistema DEVE permitir seleção e configuração de:
  - Modelo embedder de texto (se modo texto ou híbrido selecionado)
  - Modelo embedder de imagem (se modo imagem ou híbrido selecionado)
  - Parâmetros relevantes dos modelos (dimensões de vetor, etc.)
- **FR-UI-005**: Ao submeter o formulário, o sistema DEVE validar todos os arquivos carregados contra o modo selecionado e exibir um resumo detalhado de validação contendo:
  - Número de arquivos que serão processados com sucesso
  - Número de arquivos que serão ignorados (com motivos específicos para cada arquivo)
  - Número de arquivos que falharam na validação (com motivos específicos)
  - Lista de nomes de arquivos problemáticos
- **FR-UI-006**: Após exibir o resumo de validação, o sistema DEVE permitir que o usuário escolha "Prosseguir" (criar banco com arquivos válidos) ou "Cancelar" (abortar operação).
- **FR-UI-007**: Ao prosseguir, o sistema DEVE criar o banco de dados E executar a ingestão dos documentos válidos em uma única operação transacional.
- **FR-UI-008**: Após conclusão, o sistema DEVE exibir um relatório final de processamento com estatísticas finais de documentos processados/ignorados/falhas.

#### Core Requirements- **FR-000**: O sistema DEVE aceitar APENAS arquivos CSV como entrada para ingestão, independente do modo selecionado:
  - **Modo Texto**: CSV deve conter colunas com texto direto e label
  - **Modo Imagem**: CSV deve conter colunas com caminhos para arquivos de imagem e label
  - **Modo Híbrido**: CSV deve referenciar documentos/imagens/PDFs que contêm ambas as modalidades- **FR-001**: O sistema DEVE permitir selecionar o modo de ingestão para um dataset de documentos como:
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

- **Banco de Dados**: Entidade que agrupa configurações (nome, modo de ingestão, modelos embedder) e documentos ingeridos. Criado via UI.
- **Documento**: Item lógico do dataset contendo, opcionalmente, texto e/ou imagem, mais metadados associados.
- **Dataset**: Conjunto de documentos selecionado para ingestão e busca.
- **Modo de Ingestão**: Regra escolhida pela pessoa usuária para determinar quais modalidades serão vetorizadas e como o vetor final é produzido (Somente Texto / Somente Imagem / Texto e Imagem - Híbrido).
- **Vetor Híbrido**: Representação vetorial composta por múltiplas modalidades (texto e imagem) por concatenação determinística.
- **Resumo de Validação**: Relatório exibido antes de confirmar a criação do banco, contendo estatísticas de arquivos processáveis, ignoráveis e com falhas, além de detalhes de arquivos problemáticos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-UI-001**: Na home page da UI, usuário consegue identificar e clicar em botão/opção "Criar Novo Banco de Dados" em menos de 5 segundos.
- **SC-UI-002**: Usuário consegue criar um banco de dados no modo híbrido com valores padrão e fazer upload de 10 documentos mistos em menos de 2 minutos.
- **SC-UI-003**: Quando 30% ou mais dos arquivos carregados são incompatíveis com o modo selecionado, o resumo de validação lista todos os arquivos problemáticos com motivos específicos antes de permitir prosseguir.
- **SC-UI-004**: Ao prosseguir após validação com arquivos incompatíveis, o banco é criado apenas com os documentos válidos e o relatório final mostra estatísticas corretas (100% de precisão na contagem).
- **SC-001**: Dado um dataset com pelo menos 100 documentos mistos (somente texto, somente imagem e texto+imagem), a pessoa usuária consegue completar a ingestão nos três modos (texto, imagem, híbrido) via UI e obter um resultado final com contagem de processados/ignorados/falhas.
- **SC-002**: Para um dataset ingerido no modo híbrido via UI, uma busca híbrida (texto+imagem) retorna pelo menos 1 resultado quando existem documentos relevantes e não falha por incompatibilidade de formato de vetor.
- **SC-003**: Reingestões repetidas do mesmo dataset com a mesma configuração produzem vetores híbridos com composição determinística (ordem de concatenação invariável) e metadados indicando as modalidades usadas em 100% dos documentos processados.
- **SC-004**: Um conjunto de regressão contendo ao menos 20 casos (10 somente texto, 10 somente imagem) continua retornando resultados na busca, sem alteração de comportamento percebida pela pessoa usuária.

## Assumptions
- **CSV como ponto de entrada único**: Para todos os modos (texto, imagem ou híbrido), a ingestão SEMPRE começa com o upload de um arquivo CSV:
  - **Modo Texto**: CSV contém colunas (texto, label) onde a coluna de texto contém o conteúdo textual direto
  - **Modo Imagem**: CSV contém colunas (caminho_imagem, label) onde a coluna de caminho aponta para arquivos de imagem
  - **Modo Híbrido**: CSV contém colunas que referenciam documentos/imagens/PDFs que possuem ambas as modalidades- A ingestão de “dataset de documentos” pode conter documentos com somente texto, somente imagem, ou ambos.
- Quando o modo selecionado exigir uma modalidade ausente em um documento, o sistema deve produzir um resultado previsível e relatável (processado/ignorado/falhou), sem comportamento silencioso.
- A busca vetorial deve ser possível com pelo menos uma das modalidades (texto e/ou imagem), conforme disponibilidade do dataset.

## Dependencies

- Existência de um mecanismo de armazenamento e busca por similaridade vetorial para persistir vetores e executar consultas.
- Disponibilidade de modelos de vetorização para texto e para imagem, e capacidade de executar ambos quando o modo híbrido for selecionado.
