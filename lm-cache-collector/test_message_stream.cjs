'use strict';
const assert = require('node:assert/strict');
const {MessageStream} = require('./message_stream');
function frame(op, body) { const h = Buffer.alloc(4); h.writeUInt16LE(4 + body.length); h.writeUInt16LE(op, 2); return Buffer.concat([h, Buffer.from(body)]); }
const known = new Set([2220, 2201, 2242, 2245, 2202, 201]), packet = frame(2220, [23, 0, 0, 0]);
for (let cut = 0; cut <= packet.length; cut++) {
  const events = [], s = new MessageStream(x => events.push(x), known);
  s.feed(5, 'incoming', packet.subarray(0, cut));
  s.feed(5, 'incoming', Buffer.concat([packet.subarray(cut), packet]));
  assert.equal(events.filter(x => x.type === 'map_frame').length, 2);
  assert.equal(events.find(x => x.type === 'map_frame').bodyHex, '17000000');
}
{
  const events = [], s = new MessageStream(x => events.push(x), known);
  const secret = 'DO_NOT_EXPORT_LOGIN_BODY';
  s.feed(1, 'incoming', frame(201, Buffer.from(secret))); s.feed(1, 'incoming', packet);
  s.feed(2, 'outgoing', frame(2201, [1, 2, 3]));
  assert(!JSON.stringify(events).includes(secret));
  assert.equal(events.filter(x => x.type === 'map_frame').length, 2);
  s.feed(1, 'incoming', Buffer.from([0, 0, 0, 0])); s.feed(1, 'incoming', packet);
  assert.equal(events.filter(x => x.type === 'map_frame').length, 2);
  assert.equal(events.filter(x => x.type === 'capture_gap').length, 1);
  s.reset(1, 'close'); s.feed(1, 'incoming', packet);
  assert.equal(events.filter(x => x.type === 'map_frame').length, 3);
  assert.notEqual(events[0].socket, events.at(-1).socket);
}
{
  const events = [], s = new MessageStream(x => events.push(x), known);
  s.feed(2, 'incoming', packet.subarray(0, 2)); s.reset(2, 'close');
  assert.equal(events.at(-1).pendingBytes, 2);
  s.feed(2, 'incoming', frame(2202, [])); assert.equal(events.at(-1).type, 'map_context_reset');
  s.feed(2, 'incoming', Buffer.alloc(262145)); assert.equal(events.at(-1).type, 'stream_rejected');
}
{
  const events = [], s = new MessageStream(x => events.push(x), known);
  for (let fd = 0; fd < 33; fd++) s.feed(fd, 'incoming', packet);
  assert.equal(events.at(-1).type, 'agent_error'); assert(s.stopped);
}
console.log('Stream tests passed: every split, concatenation, filtering, gaps, fd reuse, truncation and bounds');
