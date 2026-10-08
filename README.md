# SourceRankedBallotBox

A reusable GenLayer primitive for authenticated, source-interpreted ranked ballots and immutable pairwise-tally results. Experimental, public and low-stakes only. Not an audited election system.

## Problem and why GenLayer

A normal voting contract counts numeric rankings but cannot safely interpret comparative preferences from prose. A centralized language model would become the authority deciding which votes count. Here each validator independently acquires the exact public ballot and interprets its complete strict ranking. That consequential AI output updates the onchain pairwise tally; it is not a decorative prompt around a deterministic state transition.

This does **not** certify factual claims, competence, service delivery or the truth of the ballot document. An authenticated eligible voter authoritatively expresses their own preference by binding public document bytes to this election. Hashes bind the bytes being interpreted; they do not establish external truth. The creator only defines immutable choices, roster and deadline, and cannot approve, veto or rewrite votes/results.

```text
fixed choices + roster + deadline
                  |
eligible voter binds pinned public document
                  |
independent full-body fetch + raw SHA-256 verification
                  |
independent AI strict-order interpretation
                  |
exact report equality across validators
                  |
COUNTED → pairwise increments / ABSTAINED → no invented order
                  |
any caller closes after all slots filled or deadline
                  |
strongest-path winner set → DECIDED / TIED / EMPTY
```

## Different mechanism, not a renamed graph

Storage consists of fixed polls, authenticated voter slots, pairwise count matrices, bounded acquisition attempts and terminal tally results. There are no editable objects, graph-edge proposals, parent versions, graph heads, permission certificates, budgets, transfers or one-time execution capabilities. There is one representative ranked-ballot implementation, not parallel domain variants. Universal novelty and steward acceptance are not claimed.

The deterministic closure algorithm uses winning-votes strongest paths: an initial edge counts votes only if it beats the reverse edge; a path's strength is its weakest edge, and the strongest such path is selected. All unbeaten alternatives remain in the winner set; no arbitrary address/label tie-breaker is invented. See [Markus Schulze's paper](https://arxiv.org/abs/1804.02973) and the [ASO explanation](https://aso.icann.org/documents/operational-documents/aso-ac-icann-board-selection-procedures/description-schulze-method/). This implementation does not adopt ASO's additional random tie-breaking or repeated ranking rounds.

## State machine and liveness

```text
OPEN
  cast_source: counted strict ballot → voter slot spent, matrix updated
  cast_source: semantic uncertainty  → voter slot spent as ABSTAINED
  cast_source: acquisition failure   → WITHHELD attempt, slot remains free
  finalize: all slots terminal OR deadline elapsed
       → DECIDED (one winner), TIED (multiple), EMPTY (no counted votes)
```

Every poll is namespaced by deployment, creator and poll ID. Every attempt and ballot additionally bind the poll, immutable definition root and authenticated voter. Eligibility is checked on that same poll before fetching. Cross-poll reuse cannot mutate another tally. Up to four immutable acquisition attempts per voter/poll; a counted/abstained slot cannot be reopened or model-resampled. Any address can finalize; absent voters and a disappearing creator cannot block deadline closure. A final result cannot be reset.

Before closing, the contract reconstructs the full matrix from bound terminal ballots and checks it against the accumulated matrix. Final results contain missing/abstained/counted voters, ballot roots, source-linked provenance and deterministic result root. Events are append-only and hash-linked.

## Consensus and failure handling

Only commit-pinned raw GitHub `.txt` URLs are accepted. Full responses must be HTTP 200, 1–8 KiB, strict UTF-8 without NUL, and hash-match before interpretation. The full document and all exact option labels reach the model. A model must interpret comparative language, not mention order, and return a complete permutation or explicit uncertainty. Partial rankings, ties, conflicting preferences and classifier instructions abstain. Schema-invalid output raises `[LLM_ERROR]` and aborts consensus rather than recording an invented abstention.

Each validator refetches and independently interprets the document. Source status, body hash, poll/voter binding, exact order, uncertainty and derived state must match the leader's full report exactly. No confidence tolerance or caller-supplied numeric rank enters the public API. Validator disagreement may abort without committing a report; it is not falsely described as a stored conflict result.

## API

- `open_poll(poll_id, choices, voters, deadline)`: semicolon-separated exact option labels; comma-separated EVM-style voter addresses. 2–8 choices, 1–8 voters, deadline 30 seconds–24 hours ahead. Creator maximum eight polls per deployment.
- `poll_key(creator, poll_id)`: deployment-bound namespace key.
- `cast_source(poll_key, attempt_id, pinned_url, raw_body_sha256)`.
- `finalize(poll_key)`: permissionless closure under the fixed liveness rule.
- `get_poll`, `get_ballot`, `get_attempt`, `history`.

Choice labels are bounded ASCII letters/digits/spaces/hyphens and case-insensitively distinct. Ballots are fully public; never post private preferences or private documents.

## Install, checks, deploy

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/genvm-lint check contracts/SourceRankedBallotBox.py --json
.venv/Scripts/python -m pytest tests -q
npm ci
node --test tests/transport.test.cjs
npm install -g genlayer@0.39.2
genlayer network set studionet
genlayer account use YOUR_ENCRYPTED_TEST_KEYSTORE
genlayer deploy --contract contracts/SourceRankedBallotBox.py
```

Use an encrypted, dedicated test wallet; StudioNet is gasless. Nonzero native value is rejected. Do not commit keys, passwords, keystores or tokens. The runner is pinned, not `test`/`latest`. Tests use mocked HTTP/AI in leader-only direct execution; an equivalence helper test is not a distributed disagreement proof. Windows cleanup defers unlinking only the test framework's open temporary message file, without skipping assertions. Deadline tests explicitly refresh the raw message datetime because gltest 0.29.2's `warp()` updates sender fields but not that cached field after deployment; production GenVM supplies a fresh message per transaction.

## Demo and evidence

`examples/strict.txt` expresses Reliability over Affordability, with Portability last, despite prose mentioning them in another order. `examples/tied.txt` expressly ties its first two choices; it must abstain, never invent a strict rank. Both are synthetic public preferences from this repository, not independent third-party observations or multi-person elections.

```powershell
$deadline=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()+3600
genlayer write ADDRESS open_poll --args demo 'Reliability;Affordability;Portability' VOTER_ADDRESS $deadline
genlayer call ADDRESS poll_key --args VOTER_ADDRESS demo
genlayer write ADDRESS cast_source --args POLL_KEY attempt1 PINNED_FIXTURE_URL RAW_SHA256
genlayer write ADDRESS finalize --args POLL_KEY
genlayer call ADDRESS get_poll --args POLL_KEY
```

Publish fixtures first and pin their URLs to the exact source commit. Hash complete raw bytes, not normalized text. Inspect FINALIZED **and execution SUCCESS and majority agreement**, then read stored state and recompute roots. Failed executions are negative tests, not completed transitions. See LIVE_PROOFS.md and SUBMISSION.md when published; missing proof entries mean a scenario was not proven onchain.

Security assumptions and residual risks: [SECURITY.md](SECURITY.md). Consensus mistakes can change an irreversible ballot and result. Do not use for governmental elections, binding financial decisions or sensitive governance.

## Optional Windows RPC transport

If Node HTTPS cannot reach StudioNet, `node --require ./scripts/windows_read_transport.cjs scripts/check.mjs ...` uses native PowerShell for public reads. Request bodies travel over stdin to avoid Windows' command-line length limit. The read shim never signs or broadcasts.

For an already-signed gasless StudioNet transaction, the separate `windows_broadcast_once.cjs` requires explicit process-local `STUDIO_NATIVE_BROADCAST=1`. Signing still occurs inside the CLI's encrypted keystore. The shim forwards each signed payload once and caches success **and failure** so SDK retries cannot resend it. A timeout can mean an unknown outcome: inspect public account history/nonce and recover its receipt before launching another process. Never paste entire raw CLI receipts or signed payloads; use the metadata-only verifier.

```powershell
genlayer network set studionet
genlayer account use YOUR_ENCRYPTED_TEST_KEYSTORE
genlayer account unlock
$cli=Join-Path (npm root -g) 'genlayer/dist/index.js'
$env:STUDIO_NATIVE_BROADCAST='1'
node --require ./scripts/windows_read_transport.cjs --require ./scripts/windows_broadcast_once.cjs $cli deploy --contract contracts/SourceRankedBallotBox.py
Remove-Item Env:STUDIO_NATIVE_BROADCAST
```

The transport unit test mocks responses and sends no transaction. It is not live deployment evidence.
