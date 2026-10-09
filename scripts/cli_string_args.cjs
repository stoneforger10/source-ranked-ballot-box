// Process-local compatibility for genlayer 0.39.2's automatic address coercion.
// text#VALUE explicitly means a string, even when VALUE is an EVM address.
// Does not modify the installed CLI or touch wallet/signing code. Node 24+.
const {registerHooks} = require('node:module');
registerHooks({
  load(url, context, nextLoad) {
    const loaded = nextLoad(url, context);
    if (!url.replaceAll('\\', '/').endsWith('/genlayer/dist/index.js')) return loaded;
    const source = typeof loaded.source === 'string' ? loaded.source : Buffer.from(loaded.source).toString('utf8');
    const marker = 'function parseScalar(value) {';
    if (source.split(marker).length !== 2) throw Error('Unsupported CLI parser: require genlayer 0.39.2');
    return {...loaded, source: source.replace(marker,
      marker + '\n  if (value.startsWith("text#")) return value.slice(5);')};
  },
});
