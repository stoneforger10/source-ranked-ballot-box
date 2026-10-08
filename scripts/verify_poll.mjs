import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';

const [address, creator, id, expectedState, expectedWinners = ''] = process.argv.slice(2);
const canonical = value => {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value !== null && typeof value === 'object') return '{' + Object.keys(value).sort()
    .map(key => canonical(key) + ':' + canonical(value[key])).join(',') + '}';
  return JSON.stringify(value).replace(/[\u0080-\uffff]/g, char => '\\u' + char.charCodeAt(0).toString(16).padStart(4, '0'));
};
const digest = value => crypto.createHash('sha256').update(canonical(value)).digest('hex');
const checkRoot = report => {
  const {root, ...payload} = report;
  assert.equal(root, digest(payload));
};
try {
  assert.match(address, /^0x[0-9a-fA-F]{40}$/);
  assert.match(creator, /^0x[0-9a-fA-F]{40}$/);
  const client = createClient({chain: studionet});
  const read = (functionName, args) => client.readContract({address, functionName, args});
  const key = await read('poll_key', [creator, id]);
  const poll = await read('get_poll', [key]);
  assert.equal(poll.state, expectedState);
  assert.equal(poll.definition_root, digest(poll.definition));
  const matrix = poll.definition.choices.map(() => poll.definition.choices.map(() => 0));
  const counted = [], abstained = [], missing = [], roots = [];
  for (const voter of poll.definition.voters) {
    let ballot;
    try { ballot = await read('get_ballot', [key, voter]); }
    catch (error) {
      if (expectedState === 'OPEN') continue;
      if (!poll.result.missing.includes(voter)) throw Error('Unexplained missing ballot or RPC failure');
      missing.push(voter);
      continue;
    }
    checkRoot(ballot);
    assert.equal(ballot.spec.poll, key);
    assert.equal(ballot.spec.definition_root, poll.definition_root);
    assert.equal(ballot.spec.voter, voter);
    assert.equal(ballot.hash, ballot.spec.expected_hash);
    roots.push({voter, root: ballot.root});
    if (ballot.state === 'COUNTED') {
      assert.equal(ballot.uncertain, false);
      assert.deepEqual([...ballot.order].sort((a, b) => a - b), poll.definition.choices.map((_, i) => i));
      counted.push(voter);
      for (let i = 0; i < ballot.order.length; i++) for (let j = i + 1; j < ballot.order.length; j++)
        matrix[ballot.order[i]][ballot.order[j]]++;
    } else {
      assert.equal(ballot.state, 'ABSTAINED');
      assert.equal(ballot.uncertain, true);
      assert.deepEqual(ballot.order, []);
      abstained.push(voter);
    }
  }
  assert.deepEqual(poll.matrix, matrix);
  assert.equal(poll.counted, counted.length);
  assert.equal(poll.processed, counted.length + abstained.length);
  if (expectedState !== 'OPEN') {
    const result = poll.result;
    checkRoot(result);
    assert.equal(result.poll, key);
    assert.deepEqual(result.counted, counted);
    assert.deepEqual(result.abstained, abstained);
    assert.deepEqual(result.missing, missing);
    assert.deepEqual(result.ballot_roots, roots);
    const paths = matrix.map((row, i) => row.map((count, j) => i !== j && count > matrix[j][i] ? count : 0));
    for (let i = 0; i < paths.length; i++) for (let j = 0; j < paths.length; j++) if (j !== i)
      for (let k = 0; k < paths.length; k++) if (k !== i && k !== j)
        paths[j][k] = Math.max(paths[j][k], Math.min(paths[j][i], paths[i][k]));
    const winners = counted.length ? paths.map((_, i) => i).filter(i => paths.every((_, j) => i === j || paths[i][j] >= paths[j][i])) : [];
    assert.deepEqual(result.paths, paths);
    assert.deepEqual(result.winner_indices, winners);
    assert.deepEqual(result.winners, winners.map(i => poll.definition.choices[i]));
    assert.deepEqual(result.winners, expectedWinners ? expectedWinners.split(';') : []);
  }
  console.log(JSON.stringify({key, state: poll.state, counted: counted.length, abstained: abstained.length,
    winners: poll.result.winners ?? [], roots_verified: true, tally_reconstructed: true, result_verified: expectedState !== 'OPEN'}));
} catch (error) {
  console.error(error.code === 'ERR_ASSERTION' ? error.message : error.shortMessage ?? 'Poll verification failed');
  process.exitCode = 1;
}
