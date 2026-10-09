# Contribution text

Eight successful finalized StudioNet receipts and source/state verification are documented in LIVE_PROOFS.md. Work date: October 8, 2026. These are synthetic single-voter demonstrations, not production-election assurance.

Contribution Type: **Builder → Intelligent Contracts**

Title:
```text
SourceRankedBallotBox — Source-Interpreted Ranked Voting
```

Notes / Description (under 1,000 characters):
```text
SourceRankedBallotBox is a reusable GenLayer ranked-voting primitive, not a graph or certificate. Fixed polls bind choices, eligible addresses and a deadline. Voters commit public preference documents and raw SHA-256 hashes. Leader and validators independently fetch full source bodies and interpret strict rankings; exact agreement on bindings, hashes, order, uncertainty and derived state is required. Complete rankings update the pairwise tally. Tied or ambiguous intent abstains; acquisition failures permit bounded retries. Immutable voter slots prevent double counting. Anyone may close after all slots finish or the deadline; closure rebuilds the tally and computes strongest-path winners without inventing tie-breaks. StudioNet proofs show hash mismatch withholding, a strict ballot electing Reliability, and tied preferences abstaining with an EMPTY result. Source matches GitHub. These are synthetic single-voter demos. GenVM lint, SDK validation and 35 mocked direct tests pass.
```

Evidence URLs:
```text
https://github.com/stoneforger10/source-ranked-ballot-box
https://github.com/stoneforger10/source-ranked-ballot-box/blob/main/contracts/SourceRankedBallotBox.py
https://github.com/stoneforger10/source-ranked-ballot-box/blob/main/README.md
https://github.com/stoneforger10/source-ranked-ballot-box/blob/main/docs/architecture.md
https://github.com/stoneforger10/source-ranked-ballot-box/blob/main/LIVE_PROOFS.md
https://explorer-studio.genlayer.com/address/0x0775Be69F8a555EDF8df4b2eCb2722cEC90E22f5
https://explorer-studio.genlayer.com/tx/0x6323b835d0b1ab1f28fb7fa2885db691e02fb6a5dc7cf9f247f5edcb258af759
https://explorer-studio.genlayer.com/tx/0x15bdddbae9b09622e671a48045952043ed934cb689b4b255b4062434326774f1
https://explorer-studio.genlayer.com/tx/0xb696ebfa6b780e2f85c8d5570c1f6688bf5088e6b4043567316951c1d453683d
https://explorer-studio.genlayer.com/tx/0x55643146a2fe41e19b45a63e43a3fd012b04761f0c86613aae5aa7615907ee1c
https://explorer-studio.genlayer.com/tx/0xd4f313cb62bbaf572d09dea535dbee43a967b37d2c05a602b3646718ac19e153
https://explorer-studio.genlayer.com/tx/0xefd660ad9dd8f0f121c18e7ff8ec3545988a60ba71a6d8675a78064494a76cf8
https://explorer-studio.genlayer.com/tx/0x210c53dbe042ce3ffbf8acd9a3cb7d2ffa528b88e1bf3d6d0dc36aad79ee17fa
https://explorer-studio.genlayer.com/tx/0x8cf5e68d7d87263e7fb09e2f71c939805a776c12727ece4c13f5139bd23ab18d
```

Public, experimental, low-stakes polls only; no privacy, personhood, production audit, acceptance or points are guaranteed. Preferences represent authenticated voter intent, not proof of external facts. Other adversarial scenarios remain mocked direct tests unless marked live in the proof matrix.
