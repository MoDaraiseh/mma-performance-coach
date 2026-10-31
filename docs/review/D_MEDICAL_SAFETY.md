# D — medical and safety reviewer pack

Workflow: **independent review pending**. This app does not provide diagnosis, rehabilitation, medical clearance, clinical nutrition or competition preparation. Automated review does not establish those capabilities.

## Scope and algorithm map

Review P1–P6, T1–T8, N1–N9 and C1 in [the inventory](METHODOLOGY_INVENTORY.md). Focus on sensitive populations, referral/withholding boundaries and potential false reassurance, rather than approval of individual training doses. Sources R5/R6/R9 support scope cautions only. No physician has signed this pack.

Inputs include reported age13–90, physical measurements, optional bodyfat, generic limitations/recovery text, sleep, subjective fatigue/soreness/readiness and a clinical-nutrition flag. Free text is not a validated screening questionnaire or medical triage tool. No condition is diagnosed. A nonempty training limitation withholds all automatic exercise sessions; reported recovery concerns reduce initial workloads and prevent progression, but may still leave a gentle template. Numerical nutrition is withheld for under18, clinical needs, unspecified metabolic equation input, unsupported energy/body-size context or detected rapid-cut goals. Adult BMI categories are explicitly inappropriate for minors.

## Synthetic cases and actual output to inspect

Read [examples.json](examples.json), including complete inputs and reason strings.

| Case | Actual behavior | Medical/safety question |
| --- | --- | --- |
| `minor` | No numerical nutrition or target weight; capped adult-derived informational training template remains | Is this scope acceptable, or should youth programming require an explicit qualified-review gate? |
| `injury_conflict` | Knee pain plus request for jumps yields zero automatic sessions | Is the withholding/referral wording sufficient without diagnosing or reading free text as clearance? |
| `low_recovery` | Sleep3h/exhaustion yields reduced template, blocked progression; maintenance nutrition still available | Which reported symptoms require all exercise withheld or urgent care wording instead? |
| `rapid_cut_request` | Numerical meal plan withheld; no individualized target weight; no dehydration instructions | Confirm no alternative flow creates the requested cut or implies weigh-in readiness. |
| `unknown_allergy` | Meals withheld | Unknown classification must not imply absence or safe cross-contact. |

## Specific questions and acceptance criteria

1. Assess youth, pregnancy/breastfeeding, eating-disorder and medical-condition scope. Acceptance requires clear exclusions/referrals and no implication that an unchecked optional flag means medical clearance.
2. Review symptom language and missing structured medical screening. The lexical coach screen is incomplete and may overblock benign text; it cannot safely rule out disease, injury or urgent conditions.
3. Assess whether reduced-work recommendations for severe sleep/fatigue are potentially inappropriate without clinician evaluation. Define explicit changes and tested acceptance cases; do not silently certify existing cutoffs.
4. Review BMI/bodyfat/lean-mass explanations, extreme body-size limits and metabolic equation assumptions. Numerical precision must not imply measurement certainty, pediatric classification or health status.
5. Confirm energy availability and REDs are not diagnosed from self-report, calorie floors, bodyfat or missing data. Nutritional completeness and allergy/halal certification must not be asserted.
6. Confirm no automated contact clearance, rehabilitation, unsafe rapid cut, hard sparring, high-risk submission or unsupervised throw prescription exists. Coaching access is unverified and does not equal medical clearance.
7. Review privacy and consent needs before introducing additional health screening. Do not request medical records merely to fill unknown fields; synthetic review cases contain no athlete data.

Known outstanding gates include qualified review of youth templates, symptom screening/referral, high-fatigue withholding, energy-availability boundaries, contact participation and return-to-training. None is satisfied by the automated test suite.

## Feedback and reviewer record

Reviewer name: ____________________  Professional license / regulator / jurisdiction: ____________________

Relevant specialty and scope of practice: ____________________

Review date: ____________________  Code version/hash reviewed: ____________________

Approval status: ____________________  Approved scope, exclusions and required follow-up: ____________________

| Method ID / case | Hazard / correction requested | Clinical rationale / reference | Severity | Acceptance test | Decision / implementation reference |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
| | | | | | |

Reviewer signature/original feedback reference: ____________________
