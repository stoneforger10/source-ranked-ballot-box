# Draft contribution text

**Deployment is pending. Do not submit as live-proven work yet.** Replace this status only after successful receipts, matching deployed source and stored-result checks are documented in LIVE_PROOFS.md.

Contribution Type: **Builder → Intelligent Contracts**

Title:
```text
SourceRankedBallotBox — Source-Interpreted Ranked Voting
```

Notes / Description (under 1,000 characters):
```text
SourceRankedBallotBox is a reusable GenLayer ranked-voting primitive, not a versioned graph or certificate. A fixed poll defines options, eligible addresses and a deadline. Each voter binds a public preference document to the poll and raw SHA-256. Leader and validators independently fetch the complete document and interpret its strict ranking; exact agreement on source hashes, election/voter bindings, order, uncertainty and derived state is required. Only a complete rank increments the pairwise tally. Ambiguity records a permanent abstention; acquisition failures allow bounded retries. Voter slots prevent double voting. Anyone can close after all slots finish or the deadline; closure rebuilds the tally, computes winning-votes strongest paths and preserves unresolved ties in an immutable result. Preferences are authenticated intent, not proof of external facts. GenVM lint, SDK validation and 35 mocked direct tests pass. StudioNet deployment remains pending; no live result is claimed.
```

Evidence URLs:
```text
https://github.com/stoneforger10/source-ranked-ballot-box
https://github.com/stoneforger10/source-ranked-ballot-box/blob/main/contracts/SourceRankedBallotBox.py
https://github.com/stoneforger10/source-ranked-ballot-box/blob/main/README.md
https://github.com/stoneforger10/source-ranked-ballot-box/blob/main/docs/architecture.md
https://github.com/stoneforger10/source-ranked-ballot-box/blob/main/LIVE_PROOFS.md
```

Use the actual work date. Add Explorer source and real verified transaction links after deployment. Public, experimental, low-stakes polls only; no privacy, personhood, production audit, acceptance or points are guaranteed.
