<!--
SYNC IMPACT REPORT
==================
Version change: 1.1.0 → 1.2.0 (MINOR - expanded type hinting and function documentation requirements)
Modified principles:
  - I. Code Quality & Testability (added Type Hinting section)
  - V. Documentation Standards (expanded Function Documentation section)
Added sections: None
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (Constitution Check section exists, compatible)
  - .specify/templates/spec-template.md ✅ (User scenarios, requirements, success criteria align)
  - .specify/templates/tasks-template.md ✅ (Test-first workflow, checkpoints align)
Follow-up TODOs: None
-->

# Vetorizer-Lib Constitution

## Core Principles

### I. Code Quality & Testability

Code MUST be written with testability as a primary design constraint:

- **Single Responsibility**: Each module, class, and function MUST have one clear purpose
- **Dependency Injection**: External dependencies MUST be injectable to enable isolation testing
- **Pure Functions**: Prefer pure functions with no side effects; side effects MUST be isolated at boundaries
- **Interface Segregation**: Components MUST depend on abstractions, not concrete implementations
- **Minimal Coupling**: Modules MUST minimize dependencies on other modules; circular dependencies are FORBIDDEN
- **Self-Documenting Code**: Names MUST clearly convey intent; complex logic MUST include inline rationale
- **Type Hinting** (NON-NEGOTIABLE):
  - ALL function parameters MUST have type hints
  - ALL function return types MUST be explicitly annotated
  - Use `typing` module for complex types (Union, Optional, List, Dict, etc.)
  - Generic types MUST specify their type parameters (e.g., `list[str]`, not `list`)
  - `Any` type is FORBIDDEN except with documented justification
  - Type hints MUST be validated by a static type checker (mypy/pyright)

**Rationale**: Testable code is maintainable code. Design decisions that compromise testability create technical debt that compounds over time.

### II. Testing Standards

Testing is NON-NEGOTIABLE and MUST follow these standards:

- **Test-First Development**: Tests MUST be written before implementation (Red-Green-Refactor)
- **Coverage Requirements**: 
  - Unit tests: MUST cover all public APIs and edge cases
  - Integration tests: MUST cover all external boundaries (APIs, databases, file systems)
  - Contract tests: MUST exist for all inter-service communication
- **Test Independence**: Each test MUST be isolated and repeatable; no test may depend on another test's state
- **Deterministic Results**: Tests MUST produce consistent results; flaky tests MUST be fixed or removed immediately
- **Fast Feedback**: Unit tests MUST complete in <100ms each; full suite MUST complete in <5 minutes
- **Meaningful Assertions**: Tests MUST verify behavior, not implementation details

**Rationale**: Comprehensive testing enables confident refactoring, prevents regressions, and serves as living documentation.

### III. User Experience Consistency

All user-facing interfaces MUST maintain consistency:

- **Design System Compliance**: UI components MUST adhere to the established design system
- **Interaction Patterns**: Similar actions MUST behave consistently across the application
- **Error Handling**: Errors MUST be user-friendly, actionable, and consistent in format
- **Feedback**: User actions MUST provide immediate visual/textual feedback
- **Accessibility**: Interfaces MUST meet WCAG 2.1 AA standards minimum
- **Responsive Design**: Interfaces MUST function correctly across supported viewport sizes
- **Loading States**: Async operations MUST display appropriate loading indicators

**Rationale**: Consistent UX reduces cognitive load, improves user satisfaction, and decreases support burden.

### IV. Performance Requirements

Performance MUST be treated as a feature, not an afterthought:

- **Response Time Budgets**:
  - API responses: <200ms p95 for standard operations
  - Page load: <3s Time to Interactive (TTI)
  - User interactions: <100ms perceived response
- **Resource Constraints**:
  - Memory usage MUST be bounded and documented
  - CPU-intensive operations MUST not block the main thread
- **Scalability**: Design MUST support horizontal scaling without architectural changes
- **Monitoring**: Performance metrics MUST be instrumented and monitored
- **Regression Prevention**: Performance tests MUST be part of CI/CD pipeline
- **Optimization Discipline**: Premature optimization is forbidden; optimize based on measured data only

**Rationale**: Performance directly impacts user experience and operational costs. Proactive performance management prevents costly rewrites.

### V. Documentation Standards

Documentation MUST be treated as a first-class deliverable, updated continuously:

- **README as Entry Point**: README.md MUST provide:
  - One-line project description
  - Installation command (`uv add vetorizer-lib` or `pip install vetorizer-lib`)
  - Minimal working example (copy-paste runnable)
  - Link to full documentation
- **Continuous Updates**: Documentation MUST be updated in the same PR as code changes
- **Clear & Direct Style**: Follow Python library documentation conventions:
  - Lead with "what it does", not "what it is"
  - Show code examples before explanations
  - Use imperative mood for instructions
  - Avoid jargon; define terms on first use
- **Function Documentation** (NON-NEGOTIABLE): Every function MUST have:
  - **Docstring**: Google-style or NumPy-style format, consistently applied
  - **Description**: First line MUST describe what the function does (not how)
  - **Args section**: Each parameter with type and clear description of purpose/constraints
  - **Returns section**: Return type and description of what is returned
  - **Raises section**: All exceptions that can be raised with conditions
  - **Example section**: At least one runnable code example showing typical usage
  - **Type hints**: Redundant in docstring if already in signature, but MUST match
  ```python
  def process_vectors(data: list[float], normalize: bool = True) -> np.ndarray:
      """Transform raw float data into normalized vector representation.

      Args:
          data: Input values to vectorize. Must contain at least one element.
          normalize: If True, scales output to unit length. Defaults to True.

      Returns:
          NumPy array of shape (n,) containing the processed vector.

      Raises:
          ValueError: If data is empty or contains non-finite values.

      Example:
          >>> result = process_vectors([1.0, 2.0, 3.0])
          >>> result.shape
          (3,)
      """
  ```
- **Changelog**: CHANGELOG.md MUST be updated for every release following Keep a Changelog format
- **uv Integration**: Document uv-specific workflows:
  - `uv sync` for environment setup
  - `uv run` for script execution
  - `uv add/remove` for dependency management

**Rationale**: Good documentation reduces onboarding time, support burden, and adoption friction. If it's not documented, it doesn't exist.

## Quality Gates

All code changes MUST pass these gates before merge:

| Gate | Requirement | Enforcement |
|------|-------------|-------------|
| Linting | Zero errors, zero warnings | Automated CI |
| Type Safety | Full type coverage, no `any` escapes without justification | Automated CI |
| Unit Tests | All pass, coverage threshold met | Automated CI |
| Integration Tests | All pass | Automated CI |
| Performance | No regression beyond 10% threshold | Automated CI |
| Code Review | Minimum 1 approval from code owner | PR requirement |
| Documentation | Public APIs documented | PR checklist |

## Development Workflow

### Code Review Requirements

- All changes MUST be reviewed before merge
- Reviewers MUST verify:
  - Constitution principle compliance
  - Test coverage adequacy
  - Performance impact assessment
  - UX consistency (for user-facing changes)
- Authors MUST respond to all review comments before merge

### Continuous Integration

- All pushes MUST trigger CI pipeline
- Failed CI MUST block merge
- CI MUST complete within 15 minutes

### Definition of Done

A feature is complete when:
1. All acceptance criteria are met
2. All quality gates pass
3. Documentation is updated
4. Performance impact is measured and acceptable
5. UX review completed (for user-facing changes)

## Governance

This constitution supersedes all other development practices:

- **Compliance**: All PRs and code reviews MUST verify constitution compliance
- **Amendments**: Changes to this constitution require:
  1. Written proposal with rationale
  2. Impact assessment on existing code
  3. Migration plan if breaking changes
  4. Team review and approval
- **Exceptions**: Temporary exceptions MUST be documented with:
  - Justification
  - Remediation timeline
  - Tracking issue reference
- **Versioning**: Constitution follows semantic versioning (MAJOR.MINOR.PATCH)

**Version**: 1.2.0 | **Ratified**: 2025-12-17 | **Last Amended**: 2025-12-17
