# Study Intent Triage And Clarification

Use this reference before selecting a reporting guideline, Table 1 layout, flowchart, or bias-control method.

## Separation Of Layers

Keep four layers distinct:

1. **Scientific question**: intervention effect, exposure association, diagnostic accuracy, individual prediction, evidence synthesis, implementation mechanism, or economic value.
2. **Study design**: RCT, cluster/stepped-wedge trial, ITS/CITS, DiD, cohort, case-control, cross-sectional, diagnostic accuracy, prediction development/validation, systematic review, qualitative, or economic evaluation.
3. **Reporting guideline**: CONSORT, STROBE/RECORD, STARD, TRIPOD+AI, PRISMA, SQUIRE, TREND, DECIDE-AI, CHEERS, SRQR/COREQ.
4. **Bias/appraisal and analysis tools**: RoB 2, ROBINS-I/ROBINS-E, QUADAS-3/QUADAS-C, PROBAST+AI, segmented regression, randomization, blinding, weighting, external validation, hierarchical meta-analysis.

A reporting checklist does not create a valid design. A risk-of-bias tool does not replace an analysis plan.

## Conversational Intake Contract

When the user supplies only an idea or broad proposal:

1. Infer up to three candidate designs and show calibrated uncertainty.
2. Ask exactly one question at a time. Use 2-7 mutually exclusive options plus a free-text path.
3. Ask the unresolved question with the greatest design impact; do not dump a questionnaire.
4. After each answer, update candidates and ask the next highest-value question.
5. Require a concrete primary aim, comparator, time/assignment structure, data source, primary outcome family, and analysis unit when applicable.
6. Present the recommended primary design, plausible alternative, and why they differ.
7. Obtain explicit design confirmation before producing final Table 1, flowchart, bias plan, or score.

Do not ask for details already supplied. If a proposal is too broad, force one primary outcome family and place other outcomes in secondary tiers.

## High-Information Questions

Ask in this order only when unresolved:

1. Primary scientific aim.
2. Intervention allocation or rollout structure.
3. Concurrent comparator availability.
4. Data source and prospective/retrospective status.
5. Prediction stage, diagnostic comparison structure, or review target when relevant.
6. Primary outcome family.
7. Analysis unit and repeated-measure structure.

## Intent-to-Design Edges

| Observable intent/structure | Candidate design | Discriminator |
| --- | --- | --- |
| Intervention deployed at a fixed date with repeated pre/post observations | ITS | Add a comparable concurrent series to prefer CITS. |
| Fixed-date intervention plus repeated concurrent control series | CITS | Model level/slope differences, not only a post indicator. |
| Non-random staggered rollout across clusters | DiD/event study or comparative panel | Test pre-trends and account for heterogeneous rollout effects. |
| Randomized staggered cluster rollout | Stepped-wedge cluster RCT | Sequence must actually be randomized. |
| Individual/cluster random allocation | RCT/cluster RCT | CONSORT family; no PSM by default. |
| Natural exposure and outcome association | Cohort/case-control/cross-sectional | Direction of sampling and time ordering decide subtype. |
| Causal comparative effectiveness from routine data | Target-trial/RWE causal design | Time zero, treatment strategies, DAG, positivity, and confounding control. |
| Index test versus reference standard | Diagnostic accuracy | Comparative tests in the same study trigger QUADAS-C alongside QUADAS-3 for appraisal. |
| Individual future outcome probability | Prediction development/validation | Development, external validation, updating, and impact are different studies. |
| Multiple published studies | Systematic review/meta-analysis | Review target selects PRISMA extension and risk-of-bias tool. |

## LLM Quality And Safety Example

For an LLM agent introduced into clinical quality control and adverse-event warning:

- Fixed-date rollout with repeated outcomes and no control: ITS.
- Same rollout plus a comparable untreated series: CITS.
- Non-random staggered rollout: DiD/event study, with rollout and pre-trend assumptions.
- Randomized staggered rollout: stepped-wedge cluster RCT.
- Only one pre and one post aggregate: uncontrolled/controlled before-after; do not call it ITS.

Guideline overlays may include SQUIRE 2.0, TREND, RECORD, and DECIDE-AI. Primary causal bias appraisal for a non-randomized intervention belongs to ROBINS-I; repeated time-series analysis belongs to segmented regression/EPOC design criteria.

## Source Anchors

- EQUATOR study-type library: https://www.equator-network.org/reporting-guidelines-study-design/
- SQUIRE 2.0: https://www.equator-network.org/reporting-guidelines/squire/
- TREND: https://www.equator-network.org/reporting-guidelines/improving-the-reporting-quality-of-nonrandomized-evaluations-of-behavioral-and-public-health-interventions-the-trend-statement/
- RECORD: https://www.equator-network.org/reporting-guidelines/record/
- DECIDE-AI: https://www.equator-network.org/reporting-guidelines/reporting-guideline-for-the-early-stage-clinical-evaluation-of-decision-support-systems-driven-by-artificial-intelligence-decide-ai/
- Cochrane Bias Methods: https://methods.cochrane.org/bias/
- QUADAS: https://www.bristol.ac.uk/population-health-sciences/projects/quadas/
