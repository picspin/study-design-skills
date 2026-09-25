# Optional TypeSafe/Jev Judgment Layer

Use this only when the user requests Jev or a calibrated semantic judgment would resolve genuine classification ambiguity. Keep it separate from the route registry, clinical statements, and numerical calculations.

## Routing

1. Gather a short de-identified scientific aim, comparator, allocation, data source, outcome, and analysis unit.
2. Run `python scripts/jev_review.py spec.json --mode route --out route-judgment.json` when `TYPESAFE_API_KEY` is available.
3. Treat its Choice probabilities as advisory evidence, not a validated probability that the proposed design is correct.
4. Preserve an explicit user-confirmed design. If Jev disagrees, show the competing design and ask only the unresolved high-impact question.
   `outside_current_registry` means the design is known but needs a new statement-backed route; it is not a reason to silently substitute a generic observational template.
5. If the top Choice is `insufficient_information`, confidence is low, or a mandatory structural fact is absent, continue the one-question triage.
6. The registry selects statements, Table 1 profile, flow layout, and bias controls after confirmation. Jev does not select a guideline or risk-of-bias tool by itself.

## Final Review

Run `python scripts/jev_review.py spec.json --mode benchmark --out benchmark-judgment.json` on a compact source-backed specification. Four independent Score questions evaluate question/design fit, reporting/bias fit, artifact coherence, and journal fit. The final benchmark conservatively uses `min(rule score, 0.8 × rule score + 0.2 × Jev score)`. Existing rule-based blockers and caps bind.

Save model ID, per-dimension scores, probabilities, and confidence with the package. A missing key, network error, or unvalidated response means `not assessed`; never fabricate a Jev result. Do not transmit patient-level records, hospital names, IP addresses, or free-text survey responses to the provider.

TypeSafe API: https://docs.typesafe.ai/api
Choice: https://docs.typesafe.ai/primitives/choice
Score: https://docs.typesafe.ai/primitives/score
