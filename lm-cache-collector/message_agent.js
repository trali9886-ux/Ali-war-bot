'use strict';
// Native libc hooks: observes successful socket I/O; never changes bytes or calls game methods.
const streams = new MessageStream(event => send(event), new Set(CAPTURE_OPTIONS.protocols));
const active = new Map(), inFlight = new Map(), listeners = [], installed = [], addresses = new Set();
let libc;
try { libc = Process.getModuleByName('libc.so'); }
catch (_) { libc = Process.getModuleByName('libc.so.6'); }
function tcp(fd) {
  try { return ['tcp', 'tcp6'].includes(Socket.type(fd)); } catch (_) { return false; }
}
function vectors(pointer, count) {
  if (count < 0 || count > 64) throw new Error('iov count exceeds 64');
  const result = [];
  for (let i = 0; i < count; i++) {
    const item = pointer.add(i * Process.pointerSize * 2);
    const size = Process.pointerSize === 8 ? item.add(8).readU64().toNumber() : item.add(4).readU32();
    if (!Number.isSafeInteger(size) || size < 0 || size > 262144) throw new Error('iov length exceeds bound');
    result.push([item.readPointer(), size]);
  }
  return result;
}
function gather(parts, count) {
  if (count > 262144 || count < 0) throw new Error('socket call exceeds 256 KiB');
  const out = new Uint8Array(count); let at = 0;
  for (const [pointer, size] of parts) {
    const length = Math.min(size, count - at);
    if (length) out.set(new Uint8Array(pointer.readByteArray(length)), at);
    at += length;
    if (at === count) break;
  }
  if (at !== count) throw new Error('socket returned more bytes than supplied buffers');
  return out;
}
function install(name, direction, kind) {
  const address = libc.findExportByName(name);
  if (!address || addresses.has(address.toString())) return;
  addresses.add(address.toString());
  listeners.push(Interceptor.attach(address, {
    onEnter(args) {
      this.thread = this.threadId;
      const depth = active.get(this.thread) || 0;
      active.set(this.thread, depth + 1);
      this.outer = depth === 0;
      if (!this.outer) return;
      this.fd = args[0].toInt32();
      if (!tcp(this.fd)) return;
      this.socket = true;
      try {
        const flags = kind === 'msg' ? args[2].toInt32() : kind === 'flags' ? args[3].toInt32() : 0;
        // MSG_PEEK doesn't consume bytes and must not enter stream reassembly.
        if (direction === 'incoming' && (flags & 2)) { this.socket = false; return; }
        this.flightKey = this.fd + ':' + direction;
        const flights = inFlight.get(this.flightKey) || 0;
        inFlight.set(this.flightKey, flights + 1);
        if (flights) {
          streams.feed(this.fd, direction, new Uint8Array([0]));
          streams.gap(this.fd, 'Concurrent same-direction socket calls; order uncertain');
          throw new Error('Overlapping socket calls');
        }
        if (kind === 'msg') {
          this.msg = args[1];
          const off = Process.pointerSize === 8 ? 16 : 8;
          const count = Process.pointerSize === 8 ? this.msg.add(off + 8).readU64().toNumber() : this.msg.add(off + 4).readU32();
          this.parts = vectors(this.msg.add(off).readPointer(), count);
        } else if (kind === 'vec') {
          this.parts = vectors(args[1], args[2].toInt32());
        } else {
          this.parts = [[args[1], args[2].toUInt32()]];
        }
        if (direction === 'outgoing') {
          const size = this.parts.reduce((sum, p) => sum + p[1], 0);
          this.copy = gather(this.parts, size);
        }
      } catch (error) { this.failure = String(error); }
    },
    onLeave(retval) {
      const depth = (active.get(this.thread) || 1) - 1;
      if (depth) active.set(this.thread, depth); else active.delete(this.thread);
      if (this.flightKey) {
        const flights = (inFlight.get(this.flightKey) || 1) - 1;
        if (flights) inFlight.set(this.flightKey, flights); else inFlight.delete(this.flightKey);
      }
      if (!this.outer || !this.socket || streams.stopped) return;
      const count = retval.toInt32();
      if (count < 0) return;
      if (count === 0) {
        if (direction === 'incoming' && this.parts && this.parts.some(p => p[1] > 0)) streams.reset(this.fd, 'receive EOF');
        return;
      }
      try {
        // Create stream before recording a first-call failure, so the gap is visible.
        if (this.failure) {
          streams.feed(this.fd, direction, new Uint8Array([0]));
          streams.gap(this.fd, this.failure); return;
        }
        if (this.msg && direction === 'incoming' && (this.msg.add(Process.pointerSize === 8 ? 48 : 24).readU32() & 32)) {
          throw new Error('MSG_TRUNC: data lost');
        }
        const bytes = direction === 'outgoing' ? this.copy.subarray(0, count) : gather(this.parts, count);
        if (bytes.length !== count) throw new Error('partial capture');
        streams.feed(this.fd, direction, bytes);
      } catch (error) {
        streams.feed(this.fd, direction, new Uint8Array([0]));
        streams.gap(this.fd, String(error));
      }
    }
  }));
  installed.push(name);
}
try {
  for (const [name, direction, kind] of [
    ['recv', 'incoming', 'flags'], ['recvfrom', 'incoming', 'flags'], ['read', 'incoming', 'plain'],
    ['recvmsg', 'incoming', 'msg'], ['readv', 'incoming', 'vec'],
    ['send', 'outgoing', 'flags'], ['sendto', 'outgoing', 'flags'], ['write', 'outgoing', 'plain'],
    ['sendmsg', 'outgoing', 'msg'], ['writev', 'outgoing', 'vec']]) install(name, direction, kind);
  for (const name of ['close', 'connect', 'shutdown']) {
    const address = libc.findExportByName(name);
    if (address) listeners.push(Interceptor.attach(address, {
      onEnter(args) { this.fd = args[0].toInt32(); },
      onLeave(retval) {
        if (name === 'connect' || retval.toInt32() === 0) streams.reset(this.fd, name);
      }
    }));
  }
  if (!installed.some(x => ['recv', 'recvfrom', 'read'].includes(x)) ||
      !installed.some(x => ['send', 'sendto', 'write'].includes(x))) throw new Error('Required native socket hooks unavailable');
  send({type: 'ready', backend: 'native-libc-sockets', arch: Process.arch, hooks: installed});
  const timer = setInterval(() => send({type: 'heartbeat', socketBytes: streams.bytes, framedMessages: streams.frames}), 1000);
  recv('stop', () => {
    streams.stopped = true;
    clearInterval(timer);
    for (const listener of listeners) listener.detach();
    for (const fd of Array.from(streams.states.keys())) streams.reset(fd, 'capture stopped');
    send({type: 'capture_stopped', socketBytes: streams.bytes, framedMessages: streams.frames});
  });
} catch (error) { send({type: 'agent_error', reason: String(error)}); }
