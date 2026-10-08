# Evidence status and proof matrix

**Not yet deployed. No contract address or transaction proof is claimed.** Do not resubmit as a completed live deployment until the required receipts and matching Explorer source are added.

Published contract/fixture commit: `ccd74ceda5b5faf31c5386d77cb792e9be66ffa3`.

## Verified local evidence

- GenVM lint and SDK validation pass: eight methods, five views, three writes, zero constructor parameters. Runner is pinned; the linter reports only an informational newer-runner notice.
- **35 direct tests pass**, using mocked HTTP/AI in leader-only execution. They exercise actual contract state and exact-equivalence helper behavior, not distributed validator consensus.
- **One Node transport test passes**, using mocked responses, proving successful and failed signed-payload requests are not automatically rebroadcast inside the process. It does not validate live transport or signing.
- Published strict fixture independently fetched as HTTP 200, raw SHA-256 `06767910e01ca3044a33440b9b0e85dcc805d391d67405f6814b14f500af936c`.
- Local LF tied fixture raw SHA-256 `0d1a0d85cf3afa5ffac46180b5c89aeb8a4103409c3f365b74e6e8a3d615ff0e`; its published response has not yet been independently checked. These are synthetic public voter-intent examples, not third-party factual observations.

| Scenario | Direct check | Live status |
| --- | --- | --- |
| Comparative prose → strict rank → pairwise increments → Reliability winner | PASS | Not run |
| Different interpreted ranking changes winner/tally | PASS | Not run |
| Tied/ambiguous preference → ABSTAINED; no invented strict order | PASS | Not run |
| Wrong response hash → WITHHELD; voter slot remains available | PASS | Not run |
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

The transport was changed to stream public RPC data over stdin, with an explicit one-shot broadcast bridge. Two automatic permission reviews timed out before that deployment command started. Those are neither failed onchain transactions nor successful deployments. Further deployment requires execution authorization and a successful receipt.

## Planned verification workflow

1. Deploy with the dedicated encrypted StudioNet test account. Record the real hash once returned; never blindly rebroadcast after a timeout.
2. `node scripts/check.mjs --success DEPLOY_HASH`: require `FINALIZED`, leader `SUCCESS`, `MAJORITY_AGREE`. A CLI success banner is insufficient; majority is not unanimity.
3. `node scripts/check.mjs --source ADDRESS`: compare normalized deployed source against this repository's contract. Normalize only CRLF/final newline.
4. Open a small poll; use `poll_key` to derive its deployment/creator-bound identity. Source URLs must pin the fixture commit above.
5. Cast an intentionally wrong nonnumeric SHA-256 string, e.g. 64 lowercase `b` characters; verify `WITHHELD`, unchanged matrix and no terminal ballot. CLI coercion of all-zero strings can invalidate the intended test.
6. Cast the correct strict source. Verify the entire stored order `[0,1,2]`, source/hash/spec binding, report root and pairwise matrix. Check a second cast rejects the spent voter slot without double counting.
7. Permissionlessly finalize, then `node scripts/verify_poll.mjs ADDRESS CREATOR strict-live DECIDED Reliability 0,1,2` to reconstruct the matrix, strongest paths, winner set and roots. A one-voter demo does not prove multi-person participation.
8. Run a separate ambiguity poll with the tied fixture; expect `ABSTAINED` then `EMPTY`, not a fabricated strict ranking. Verify with `node scripts/verify_poll.mjs ADDRESS CREATOR tied-live EMPTY`.

Prepend `--require ./scripts/windows_read_transport.cjs` for Windows public RPC read fallback. Do not classify planned stages or mocked assertions as live proofs.
