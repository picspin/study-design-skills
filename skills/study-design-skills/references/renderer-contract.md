# Renderer Contract

Renderers transform a validated study-package JSON object into CSV, XLSX, HTML, Markdown, and figures. They do not choose a study design or invent clinical content.

## Allowed Renderer Decisions

- file names, sheet names, column widths, fonts, colors, borders, and print settings;
- deterministic numeric formatting and rounding;
- HTML accessibility attributes and responsive layout;
- selection of a layout named by `route.flow_layout`;
- selection of a table structure named by `route.table_profile`;
- explicit display of `pending`, `not estimable`, or validation warnings.

## Forbidden Renderer Decisions

- inferring a reporting guideline from free text;
- deciding whether PSM, MI, blinding, calibration, or external validation is appropriate;
- changing the primary estimand or endpoint hierarchy;
- inventing counts, exclusions, sample sizes, journal evidence, or completed analyses;
- silently converting a protocol plan into an executed result;
- maintaining separate medical narratives for HTML, XLSX, CSV, and Markdown.

## Compatibility Boundary

Legacy flat JSON remains accepted. `compile_study_spec.py` must convert it to the canonical contract before rendering.

Existing text-based renderer fallbacks may remain during migration, but:

1. canonical `route.flow_layout` and `route.table_profile` take precedence;
2. no new medical inference may be added to a renderer fallback;
3. every new design family must first be registered in `route-registry.json`;
4. every package must save the compiled JSON used for rendering.

## Failure Behavior

- Unknown route: stop with a validation error.
- Missing required clinical content: warn during protocol development and fail strict validation.
- Unknown denominator: render `n = pending`.
- Unsupported statistical calculation: return assumptions required, not a fabricated estimate.
- Missing external evidence: render `not verified` with provenance.
