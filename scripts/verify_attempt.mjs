import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';

const [address, voter, id, attemptId, expectedState, expectedReason] = process.argv.slice(2);
const canonical = value => {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value !== null && typeof value === 'object') return '{' + Object.keys(value).sort()
    .map(key => canonical(key) + ':' + canonical(value[key])).join(',') + '}';
  return JSON.stringify(value).replace(/[\u0080-\uffff]/g, char => '\\u' + char.charCodeAt(0).toString(16).padStart(4, '0'));
};
try {
  assert.match(address, /^0x[0-9a-fA-F]{40}$/);
  assert.match(voter, /^0x[0-9a-fA-F]{40}$/);
  const client = createClient({chain: studionet});
  const read = (functionName, args) => client.readContract({address, functionName, args});
  const key = await read('poll_key', [voter, id]);
  const poll = await read('get_poll', [key]);
  const report = await read('get_attempt', [key, voter, attemptId]);
  const {root, ...payload} = report;
  assert.equal(root, crypto.createHash('sha256').update(canonical(payload)).digest('hex'));
  assert.equal(report.spec.poll, key);
  assert.equal(report.spec.definition_root, poll.definition_root);
  assert.equal(report.spec.voter.toLowerCase(), voter.toLowerCase());
  assert.equal(report.spec.attempt, attemptId);
  assert.equal(report.state, expectedState);
  assert.equal(report.reason, expectedReason);
  if (expectedState === 'WITHHELD') {
    assert.deepEqual(report.order, []);
    assert.equal(report.uncertain, true);
    assert.equal(poll.counted, 0);
    assert.equal(poll.processed, 0);
    assert.deepEqual(poll.matrix, poll.definition.choices.map(() => poll.definition.choices.map(() => 0)));
    assert.notEqual(report.hash, report.spec.expected_hash);
  }
  console.log(JSON.stringify({key, attempt: attemptId, state: report.state, reason: report.reason,
    report_root_verified: true, binding_verified: true, counted: poll.counted, processed: poll.processed}));
} catch (error) {
  console.error(error.code === 'ERR_ASSERTION' ? error.message : error.shortMessage ?? 'Attempt verification failed');
  process.exitCode = 1;
}
