'use strict';
// Incremental envelope parser. Never searches inside arbitrary bytes for a header.
class MessageStream {
  constructor(emit, known) {
    this.emit = emit; this.known = known; this.states = new Map(); this.serial = 0;
    this.bytes = 0; this.frames = 0; this.stopped = false;
  }
  reset(fd, reason) {
    if (this.states.has(fd)) {
      const state = this.states.get(fd);
      this.emit({type: 'stream_end', socket: state.id, reason,
        pendingBytes: state.incoming.buffer.length + state.outgoing.buffer.length, mapTrafficObserved: state.map});
      this.states.delete(fd);
    }
  }
  gap(fd, reason) {
    const state = this.states.get(fd);
    if (state && !state.failed) {
      state.failed = true;
      state.incoming.buffer = state.outgoing.buffer = new Uint8Array(0);
      this.emit({type: state.map ? 'capture_gap' : 'stream_rejected', socket: state.id, reason});
    }
  }
  feed(fd, direction, chunk) {
    if (this.stopped || !chunk.length) return;
    this.bytes += chunk.length;
    if (this.bytes > 64 * 1024 * 1024) {
      this.stopped = true;
      this.emit({type: 'agent_error', reason: '64 MiB socket observation limit reached'}); return;
    }
    let state = this.states.get(fd);
    if (!state) {
      if (this.states.size >= 32) {
        this.stopped = true;
        this.emit({type: 'agent_error', reason: '32 concurrent socket limit reached'}); return;
      }
      state = {id: ++this.serial, failed: false, map: false,
        incoming: {buffer: new Uint8Array(0)}, outgoing: {buffer: new Uint8Array(0)}};
      this.states.set(fd, state);
      this.emit({type: 'stream_start', socket: state.id,
        alignment: 'first-observed-byte-assumed; not live-verified'});
    }
    if (state.failed) return;
    if (chunk.length > 262144) { this.gap(fd, 'socket call exceeds capture limit'); return; }
    const stream = state[direction];
    const data = new Uint8Array(stream.buffer.length + chunk.length);
    data.set(stream.buffer); data.set(chunk, stream.buffer.length);
    let offset = 0;
    while (data.length - offset >= 4) {
      const size = data[offset] | (data[offset + 1] << 8);
      const opcode = data[offset + 2] | (data[offset + 3] << 8);
      if (size < 4 || size > 4096 || !this.known.has(opcode)) {
        this.gap(fd, 'Unknown frame boundary/protocol; reopen game connection while capture is active'); return;
      }
      if (data.length - offset < size) break;
      this.frames++;
      const selected = direction === 'incoming' ? [2220, 2242, 2245] : [2201, 2233, 2241];
      if (selected.includes(opcode)) {
        state.map = true;
        const body = data.subarray(offset + 4, offset + size);
        this.emit({type: 'map_frame', socket: state.id, direction, opcode,
          frameBytes: size, bodyHex: Array.from(body, b => b.toString(16).padStart(2, '0')).join('')});
      } else if (opcode >= 2200 && opcode < 2300) {
        // Map/channel transitions invalidate decoder widths; discard unrelated payloads.
        this.emit({type: 'map_context_reset', socket: state.id, opcode, direction});
      }
      offset += size;
    }
    stream.buffer = data.slice(offset);
  }
}
if (typeof module !== 'undefined') module.exports = {MessageStream};
