const test = require('node:test');
const assert = require('node:assert/strict');

test('one-shot bridge caches success and unknown failure, never retries a signed payload', async () => {
  const descriptor = Object.getOwnPropertyDescriptor(process, 'platform');
  const priorFetch = globalThis.fetch;
  const priorError = console.error;
  const priorFlag = process.env.STUDIO_NATIVE_BROADCAST;
  const helper = require.resolve('../scripts/native_http.cjs');
  const shim = require.resolve('../scripts/windows_broadcast_once.cjs');
  const priorModule = require.cache[helper];
  const counts = new Map();
  try {
    Object.defineProperty(process, 'platform', {...descriptor, value: 'win32'});
    process.env.STUDIO_NATIVE_BROADCAST = '1';
    console.error = value => assert.match(value, /^BROADCAST_HASH 0x[0-9a-fA-F]{64}$/);
    globalThis.fetch = async () => new Response('{"result":"ordinary-read"}');
    require.cache[helper] = {exports: {requestOnce: async rpc => {
      const payload = rpc.params[0];
      counts.set(payload, (counts.get(payload) ?? 0) + 1);
      if (payload === '0xbeef') throw Error('unknown broadcast outcome');
      return JSON.stringify({result: '0x' + 'a'.repeat(64)});
    }}};
    delete require.cache[shim];
    require(shim);
    const request = payload => globalThis.fetch('https://studio.genlayer.com/api',
      {body: JSON.stringify({method: 'eth_sendRawTransaction', params: [payload]})});
    const results = await Promise.all([request('0xdead'), request('0xdead')]);
    assert.deepEqual(await results[0].json(), await results[1].json());
    assert.equal(counts.get('0xdead'), 1);
    await assert.rejects(request('0xbeef'), /unknown broadcast outcome/);
    await assert.rejects(request('0xbeef'), /unknown broadcast outcome/);
    assert.equal(counts.get('0xbeef'), 1);
    const read = await globalThis.fetch('https://studio.genlayer.com/api', {body: JSON.stringify({method: 'eth_chainId', params: []})});
    assert.equal((await read.json()).result, 'ordinary-read');
  } finally {
    Object.defineProperty(process, 'platform', descriptor);
    globalThis.fetch = priorFetch;
    console.error = priorError;
    if (priorFlag === undefined) delete process.env.STUDIO_NATIVE_BROADCAST;
    else process.env.STUDIO_NATIVE_BROADCAST = priorFlag;
    if (priorModule) require.cache[helper] = priorModule;
    else delete require.cache[helper];
    delete require.cache[shim];
  }
});
