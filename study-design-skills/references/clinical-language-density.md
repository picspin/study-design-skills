# Clinical Language And Density Rules

Apply these rules to every generated protocol, Table 1 note, flowchart, HTML section, spreadsheet note, and Markdown memo.

## Audience

Write for clinicians, medical students, nurses, technologists, statisticians, and research coordinators who must act on the design.

- Prefer clinical nouns and explicit actions: `adjudicated extravasation`, `randomized sequence`, `reference-standard verification`.
- Define an abbreviation at first use; do not make the reader decode a method stack.
- Separate what is known, planned, pending approval, and not yet estimable.
- Never convert a statistical assumption into a clinical fact.
- Use `participant`, `patient`, `examination`, `image`, `lesion`, `reader`, `encounter`, `cluster`, `period`, `record`, `report`, or `study` deliberately. Do not mix denominator units.

## Density

- Keep a prose block to three sentences.
- Keep a bullet to one action or one claim, normally no more than 18 English words or about 36 Chinese characters.
- Keep a table cell to 25 English words or about 50 Chinese characters.
- Put parallel content in one table:
  - rows = stages, endpoints, bias domains, periods, or analysis sets;
  - columns = groups, devices, models, sites, or study variants.
- Do not write three long parallel paragraphs for three study arms, validation cohorts, sensitivity models, or implementation stages.
- Move definitions, coding rules, denominator notes, and model details to table footnotes or a methods-notes block.
- Use a connected flowchart for sequential enrollment, attrition, allocation, verification, dataset splitting, or workflow states. Do not narrate a flowchart as a long paragraph.
- Use one short paragraph followed by a structured table when a section contains both rationale and parallel operational detail.

## Clinical Sequence

Present methods in the order a study actually occurs:

1. source population and setting;
2. eligibility and time zero;
3. allocation, exposure, index test, prediction point, or intervention;
4. follow-up, reference standard, or outcome ascertainment;
5. analysis sets and missing data;
6. primary model;
7. sensitivity, validation, safety, and subgroup analyses.

Do not lead with software, a regression model, PSM, multiple imputation, or a reporting checklist before defining the clinical question and design.

## Tables

- Use one comparison table when multiple designs solve the same proposal.
- Use one objective-to-analysis table when primary and secondary objectives require different endpoints or models.
- Use one bias-control matrix when several methods address different threats.
- Keep Table 1 labels compact; put operational definitions in footnotes.
- Avoid repeating the same covariate list in the protocol prose, Table 1, and propensity-model section. Register it once in the JSON content source and reference it.

## Flowcharts

- Keep each node to a short label, denominator, and at most one detail line.
- Put exclusion reasons in side boxes, not in the retained cohort spine.
- Put long eligibility definitions in the protocol table or caption.
- Label unknown counts `n = pending`; never invent a denominator.
- Reconcile parent counts with retained and excluded child counts before finalization.

## Anti-AI Language Checks

Remove:

- generic openings such as `This comprehensive study aims to`;
- repeated claims that the design is `robust`, `rigorous`, or `novel` without evidence;
- ornamental transitions such as `Furthermore` and `It is worth noting that`;
- long method inventories with no mapping to a bias or objective;
- conclusions that merely repeat the objective.

Replace them with the clinical decision, operational definition, or unresolved assumption.
