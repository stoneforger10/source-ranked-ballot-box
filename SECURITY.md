# Security and trust model

Experimental public preference tally. No independent security audit, secret ballot, universal novelty or high-stakes election suitability is claimed.

## Invariants

- Poll identity includes deployment, creator and poll ID. Fixed choices, deadline and roster cannot be changed after creation.
- Every cast checks authenticated sender against the same poll roster and binds the independently checked report to poll, definition root and voter.
- Complete source bytes, not caller summaries/ranks, determine the model input. Exact validator recomputation checks the ranking and its consequential decision.
- Counted/abstained voter slots cannot be overwritten. Four acquisition attempts maximum; uncertainty consumes the slot to prevent model resampling.
- Only a complete strict permutation increments the matrix. Models never supply matrix entries, path strengths, winner sets or arbitrary scores.
- Finalization reconstructs tallies from bound ballots, preserves unresolved ties, records missing voters, and is callable by anyone after the deadline or all slots are terminal.
- Finalized results and attempt records are immutable. Operation/result roots are deployment-bound; history is append-only.
- Public bounds prevent unbounded work in one transaction. Nonzero native value is rejected in deployment and every write; external contract writes, asset accounting and transfer permissions are not used.

## Residual risks

The poll creator chooses a small roster, which can censor or contain Sybil accounts. Address control does not prove personhood. Preferences and identity-address links are public; coercion and vote buying are not prevented. Publisher-controlled documents can be misleading or contain prompt injection; AI can confidently misinterpret them even with agreement. Exact agreement can reduce liveness. A semantically ambiguous ballot permanently abstains, so a mistaken classification cannot be corrected in place. Network/source failure may exhaust the bounded retries, but deadline closure still works. Commit-pinned URLs and raw hashes bind snapshots, not ongoing current opinion or source ownership. HTTP redirect authenticity is not independently attested.

A successful poll says only how this fixed roster's authenticated source ballots were interpreted under this deployment's fixed policy. It does not certify external truth or grant execution/payment rights. Use offchain review and separate reviewed governance controls if integrating with consequential systems.

Report vulnerabilities privately to the repository owner. Do not disclose keys, credentials or confidential ballots.
