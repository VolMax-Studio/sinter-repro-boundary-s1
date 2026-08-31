# LIMITATIONS: Scope, Non-Claims, and Epistemic Boundaries

This is a positive control on the measurement instrument.
It is NOT an independent verification of any third party's claim.

No party has publicly claimed that sinter is byte-reproducible.
There is therefore no claimant and no claim under audit here.

Neither outcome of this test constitutes evidence that any
published QEC result is incorrect, or that any published QEC
result is correct.

Three distinct properties are separated and only the first is
measured here:
  1. byte identity of the output artifact   [MEASURED]
  2. statistical agreement of the estimates [NOT MEASURED]
  3. scientific validity of the benchmark   [NOT MEASURED]

Data source independence: the data measured here is generated
by the same party performing the measurement. On the source-
independence axis this is the weakest configuration. No verdict
of "independently verified" can follow from this instance.

Scope: one machine, one OS, one CPU, the worker counts listed
in PREREGISTRATION.md. Nothing outside that scope is claimed.

Statistical resolution limit on distance d=5:
Due to the chosen low physical noise rate (p = 0.001) and sampling
budget (50,000 shots per run), observed logical errors for d=5
are in the single digits (2–12 errors per run, Poisson noise
dominates). This dataset is strictly designed to evaluate artifact
and batch row structural properties; it MUST NOT be used to derive
or assert logical error rates or threshold scaling for d=5.

Interpretation of the CSV 'seconds' Column:
The raw 'seconds' column in sinter CSV outputs reflects internal
sub-routine timing rather than total benchmark wall-clock duration.
This field is not interpreted, has no physical runtime claims attached,
and does not enter into any decision rule.


