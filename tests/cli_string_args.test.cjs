const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');

test('CLI compatibility preserves explicit strings without editing the CLI', () => {
  let hooks;
  const source = fs.readFileSync(require.resolve('../scripts/cli_string_args.cjs'), 'utf8');
  vm.runInNewContext(source, {Buffer, require: name => {
    assert.equal(name, 'node:module');
    return {registerHooks: value => {hooks = value;}};
  }});
  const original = 'function parseScalar(value) { return "coerced"; }';
  const loaded = {format: 'module', source: original};
  assert.equal(hooks.load('file:///other/index.js', {}, () => loaded), loaded);
  const patched = hooks.load('file:///node_modules/genlayer/dist/index.js', {}, () => loaded);
  assert.equal(loaded.source, original);
  const parse = vm.runInNewContext('(' + patched.source + ')');
  const address = '0x' + 'a'.repeat(40);
  assert.equal(parse('text#' + address), address);
  assert.equal(parse(address), 'coerced');
  assert.throws(() => hooks.load('file:///node_modules/genlayer/dist/index.js', {},
    () => ({source: 'different parser'})), /Unsupported CLI parser/);
});
