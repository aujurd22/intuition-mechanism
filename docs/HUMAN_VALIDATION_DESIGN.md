# Human Validation Design for the Two-Axis Interestingness Theory

Status: registered 2026-09-30 03:55.  This is the experimental design
for the HUMAN validation of the two-axis theory (P98), which is the
bridge between "a blind LLM judge can discriminate surprise from
utility" and "these are genuine mathematical cognition axes."

## Background

P91-scaled confirmed: within a fixed lambda-degree, a blind LLM judge
prefers the higher-genus-depth identity (88.9%, p = 0.039).
P92 confirmed: the judge DISCRIMINATES novelty from utility (surprise
prefers deep rows 9:7; utility prefers rational rows 13:3).
P97-b refuted: no linear degree effect at any gap (p = 0.82).

The theory: SURPRISE tracks genus-structure-depth transitions;
UTILITY tracks proximity to the published-rationality locus.  The
axes are dissociable.

## What human validation adds

If HUMAN mathematicians show the SAME dissociation (prefer deep rows
for surprise, prefer rational rows for utility), then:
1. The two-axis theory is not an LLM artifact.
2. The genus-depth proxy measures something real about mathematical
   cognition.
3. The five-row theorem's psychological significance is grounded:
   these rows are "interesting" to humans for the SAME two reasons
   (structural depth = surprising; published rationality = useful).

## Experimental design

### Stimuli
The 21 known-degree identities (same set as P33-n20/P91-scaled),
presented in isolation with no degree/genus labels.

### Participants
Target: 5-10 mathematicians or advanced math students (each
participant sees all pairs).

### Conditions (within-subject, 2 framings x 21 identities)
- SURPRISE framing: "Which of these two identities is more
  structurally surprising?"  (forced choice, 19 deg-matched pairs)
- UTILITY framing: "Which would be more useful as a seed for further
  discovery?"  (forced choice, 19 deg-matched pairs)
- PRESENTATION: order-swapped (half see AB, half see BA)

### Predictions (pre-registered)
- H1: human surprise preferences correlate with LLM surprise
  preferences (Spearman rho > 0.3 over identities)
- H2: human utility preferences correlate with LLM utility
  preferences (Spearman rho > 0.3)
- H3: the DISSOCIATION replicates (some identities are
  "surprising-not-useful" and others "useful-not-surprising" for
  both LLM and humans)
- H0-null: no above-chance agreement => the two-axis theory is an
  LLM artifact, not a mathematical cognition fact.

### Analysis
- Per-participant: Spearman(bhuman ranks, LLM ranks) per framing.
- Group: mean correlation across participants.
- Dissociation: count of identities where the group majority
  prefers A for surprise AND B for utility (dissociation score).

### Statistical power
With 5 participants and 19 pairs, Cohen's kappa > 0.4 is detectable
at power 0.8.  The design is adequately powered for a moderate
effect, not for small effects.

## What this design does NOT cover

- Expertise gradient (novice vs expert preferences)
- Cross-cultural variation
- Non-mathematical interestingness domains
- Training effects (participants see all identities)

## Preregistration

This design is being registered BEFORE any human data collection.
The predictions H1-H3 and the null H0 are fixed.  No changes to the
analysis plan are permitted after data collection begins.
