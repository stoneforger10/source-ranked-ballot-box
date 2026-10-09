# Evidence status and proof matrix

**StudioNet deployment, strict-ranking lifecycle and tied-preference abstention verified on October 8, 2026.**

Contract: [0x0775Be69F8a555EDF8df4b2eCb2722cEC90E22f5](https://explorer-studio.genlayer.com/address/0x0775Be69F8a555EDF8df4b2eCb2722cEC90E22f5).
Dedicated encrypted test wallet: `0x7a413BB4AB62E31d62d4cD9efC8C8a8Dae37FB42`. Gasless test transactions; no assets transferred.

Deployed source equals the published contract below, normalizing only CRLF/final newline. Normalized source SHA-256: `388beaebb05560e870fb84566b8f154c77ecb276fd643d0e44ba23136c73667a`.

## Finalized live receipts

Every successful transition below was checked for `FINALIZED`, leader execution `SUCCESS` and `MAJORITY_AGREE`. This is not a claim of unanimous validation.

| Stage | Transaction | Verified observation |
| --- | --- | --- |
| Deploy | [0x6323…f759](https://explorer-studio.genlayer.com/tx/0x6323b835d0b1ab1f28fb7fa2885db691e02fb6a5dc7cf9f247f5edcb258af759) | Source matches published contract |
| Open strict poll | [0x15bd…74f1](https://explorer-studio.genlayer.com/tx/0x15bdddbae9b09622e671a48045952043ed934cb689b4b255b4062434326774f1) | OPEN, empty tally |
| Wrong hash | [0xb696…683d](https://explorer-studio.genlayer.com/tx/0xb696ebfa6b780e2f85c8d5570c1f6688bf5088e6b4043567316951c1d453683d) | WITHHELD / HASH_MISMATCH; counted and processed both zero; report root and poll/voter binding checked |
| Strict source | [0x5564…ee1c](https://explorer-studio.genlayer.com/tx/0x55643146a2fe41e19b45a63e43a3fd012b04761f0c86613aae5aa7615907ee1c) | COUNTED; independently read exact order [0,1,2] and reconstructed matrix/root |
| Finalize strict | [0xd4f3…e153](https://explorer-studio.genlayer.com/tx/0xd4f313cb62bbaf572d09dea535dbee43a967b37d2c05a602b3646718ac19e153) | DECIDED / Reliability; reconstructed ballot roots, matrix, strongest paths and result root |
| Open tied poll | [0xefd6…6cf8](https://explorer-studio.genlayer.com/tx/0xefd660ad9dd8f0f121c18e7ff8ec3545988a60ba71a6d8675a78064494a76cf8) | SUCCESS; separate tied-live namespace |
| Tied source | [0x210c…17fa](https://explorer-studio.genlayer.com/tx/0x210c53dbe042ce3ffbf8acd9a3cb7d2ffa528b88e1bf3d6d0dc36aad79ee17fa) | ABSTAINED / UNCERTAIN_PREFERENCE; counted zero, processed one; stored report root and binding verified |
| Finalize tied | [0x8cf5…b18d](https://explorer-studio.genlayer.com/tx/0x8cf5e68d7d87263e7fb09e2f71c939805a776c12727ece4c13f5139bd23ab18d) | EMPTY; zero counted, one abstained, no winners; reconstructed matrix, strongest paths and roots |

These are synthetic, single-voter demonstrations of authenticated preference intent, not independent factual observations, multi-person participation or production-election assurance.

Published contract/fixture commit: `ccd74ceda5b5faf31c5386d77cb792e9be66ffa3`.

## Verified local evidence

- GenVM lint and SDK validation pass: eight methods, five views, three writes, zero constructor parameters. Runner is pinned; the linter reports only an informational newer-runner notice.
- **35 direct tests pass**, using mocked HTTP/AI in leader-only execution. They exercise actual contract state and exact-equivalence helper behavior, not distributed validator consensus.
- **Two Node tests pass**: mocked one-shot transport and a synthetic CLI-parser compatibility test. Neither signs or sends transactions.
- Published strict fixture independently fetched as HTTP 200, raw SHA-256 `06767910e01ca3044a33440b9b0e85dcc805d391d67405f6814b14f500af936c`.
- Published tied fixture independently fetched as HTTP 200, raw SHA-256 `0d1a0d85cf3afa5ffac46180b5c89aeb8a4103409c3f365b74e6e8a3d615ff0e`. These are synthetic public voter-intent examples, not third-party factual observations.

| Scenario | Direct check | Live status |
| --- | --- | --- |
| Comparative prose → strict rank → pairwise increments → Reliability winner | PASS | PASS: COUNTED then DECIDED; stored roots/tally reconstructed |
| Different interpreted ranking changes winner/tally | PASS | Not run |
| Tied/ambiguous preference → ABSTAINED; no invented strict order | PASS | PASS: ABSTAINED then EMPTY; no winners, stored roots/tally reconstructed |
| Wrong response hash → WITHHELD; voter slot remains available | PASS | PASS: WITHHELD; subsequent correct ballot COUNTED |
| Cross-poll unauthorized sender cannot mutate another tally | PASS | Not run |
| Replayed voter slot / acquisition attempt rejected | PASS | Not run |
| Missing voter: any third party closes at deadline | PASS | Not run |
| Terminal result cannot be overwritten/reset | PASS | Not run |
| Indirect strongest paths resolve a pairwise-majority cycle | PASS helper | Not run |
| Pairwise ties remain a winner set | PASS | Not run |
| Ranking/uncertainty/hash/binding disagreement rejects equivalence | PASS helper only | Distributed disagreement experiment not run |
| Invalid source, malformed vector, retry quota or native value | PASS | Not run |

## Deployment attempts — excluded from proof claims

The initial CLI deployment failed during pre-broadcast gas-price reads. The read-fallback retry hit Windows' command-length limit during gas estimation and then a Node HTTPS broadcast timeout. Public account history was checked after both attempts and contained no new transaction: last observed nonce was 105, next nonce `0x6a` (106). No deployment hash is fabricated.

The transport was changed to stream public RPC data over stdin, with an explicit one-shot broadcast bridge. Two automatic permission reviews timed out before that deployment command started. Those are neither failed onchain transactions nor successful deployments. The later successful deployment is listed above.

Initial `open_poll` transaction `0x09920a44e5ffa0c8829a52a076739248723a7a8090a5d77b8498440bc950c92a` finalized with execution ERROR / `[EXPECTED] invalid poll definition`: CLI 0.39.2 coerced a single voter address into the wrong argument type. No poll was created. It is excluded from successful lifecycle evidence. A temporary local parser patch was restored; the published process-local `cli_string_args.cjs` loader supports explicit `text#` string arguments without editing the installed CLI.

## Reproducible verification workflow

1. Deploy with the dedicated encrypted StudioNet test account. Record the real hash once returned; never blindly rebroadcast after a timeout.
2. `node scripts/check.mjs --success DEPLOY_HASH`: require `FINALIZED`, leader `SUCCESS`, `MAJORITY_AGREE`. A CLI success banner is insufficient; majority is not unanimity.
3. `node scripts/check.mjs --source ADDRESS`: compare normalized deployed source against this repository's contract. Normalize only CRLF/final newline.
4. Open a small poll; use `poll_key` to derive its deployment/creator-bound identity. Source URLs must pin the fixture commit above.
5. Cast an intentionally wrong nonnumeric SHA-256 string, e.g. 64 lowercase `b` characters; verify `WITHHELD`, unchanged matrix and no terminal ballot. CLI coercion of all-zero strings can invalidate the intended test.
6. Cast the correct strict source. Verify the entire stored order `[0,1,2]`, source/hash/spec binding, report root and pairwise matrix. Check a second cast rejects the spent voter slot without double counting.
7. Permissionlessly finalize, then `node scripts/verify_poll.mjs ADDRESS CREATOR strict-live DECIDED Reliability 0,1,2` to reconstruct the matrix, strongest paths, winner set and roots. A one-voter demo does not prove multi-person participation.
8. Run a separate ambiguity poll with the tied fixture; expect `ABSTAINED` then `EMPTY`, not a fabricated strict ranking. Verify with `node scripts/verify_poll.mjs ADDRESS CREATOR tied-live EMPTY`.

Prepend `--require ./scripts/windows_read_transport.cjs` for Windows public RPC read fallback. Do not classify planned stages or mocked assertions as live proofs.
