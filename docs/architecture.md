# Consensus boundary

One representative primitive: an authenticated, source-interpreted ranked ballot accumulator. No owner-controlled knowledge graph, versioned proposal head, certificate or execution consumption.

1. A creator fixes 2–8 option labels, 1–8 eligible addresses and a deadline. This defines a small private-roster poll; it does not establish human identity or democratic legitimacy.
2. An eligible voter binds a commit-pinned public preference document to the election and raw SHA-256 in an authenticated transaction. The document states that voter's intent, not proof of real-world achievements.
3. Leader and validators independently fetch the complete UTF-8 document, verify its hash and interpret a complete strict order of the exact option labels. Partial, tied, ambiguous or injected instructions produce an abstention rather than invented preferences.
4. Exact agreement on the full source/interpretation report is required. The contract deterministically converts the accepted order into pairwise increments. Neither caller nor model supplies tally values.
5. A counted ballot or semantic abstention permanently occupies that voter slot. Acquisition failure records a bounded retry attempt without occupying the slot. Up to four attempts per voter/election.
6. Anyone may finalize after the deadline or all voter slots are terminal. Winning-votes strongest paths produce an immutable winner set; unresolved ties remain ties. No payments or external writes occur.

Frontend owns previews and publication of preferences. Publishers own source bytes. The contract owns source acquisition, authenticated election binding, semantic order, pairwise tally and final result. It does not verify mailbox identity, source truth, or voter independence.

Residual risks: public ballots, roster-manager censorship at creation, vote buying/coercion, Sybil addresses, semantic mistakes, prompt injection, host outages and exact-agreement liveness. Use only experimental low-stakes polls; no privacy or election-security audit is claimed.
