'use strict';

// Read-only probe for Lords Mobile 2.201 / build 692 / ARM64 via native x64 Frida.
// No native function calls, hooks, writes, or network requests.
function readSnapshot() {
  let stage = 'library identification';
  let readableRanges = [];
  const readStarted = Date.now();
  const diagnostics = {probeVersion: 'cache-collector-3'};
  const expected = [
    [0x4f8ee54, 'fe0f1ef8f44f01a9b3b401f0b49201b06842553994b241f928010037a09201b0'],
    [0x43fa3a8, 'ffc306d1ef3b116ded33126deb2b136de923146dfd7b15a9fc6f16a9fa6717a9'],
    [0x3c0d5a8, 'fe6fbba9fa6701a9f85f02a9f65703a9f44f04a9955002b0f40301aaf30300aa'],
    [0x4f94474, 'fe0f1ef8f44f01a993b401b0749201f0683e553994b241f9c8000037609201f000b041f9742c859728008052683e1539']
  ];
  function checked(address, size) {
    // One range inventory per snapshot; actual reads still throw if mappings change.
    let lo = 0, hi = readableRanges.length - 1, range = null;
    while (lo <= hi) {
      const mid = (lo + hi) >>> 1;
      if (readableRanges[mid].base.compare(address) <= 0) {
        range = readableRanges[mid]; lo = mid + 1;
      } else hi = mid - 1;
    }
    if (address.isNull() || !range || !range.protection.startsWith('r') ||
        address.add(size).compare(range.base.add(range.size)) > 0) {
      throw new Error('Unreadable memory at ' + address);
    }
    return address;
  }
  const pointer = a => checked(a, 8).readPointer();
  const u8 = a => checked(a, 1).readU8();
  const u16 = a => checked(a, 2).readU16();
  function hex(a, size) {
    return Array.from(new Uint8Array(checked(a, size).readByteArray(size)),
      n => n.toString(16).padStart(2, '0')).join('');
  }
  function className(klass) {
    const address = pointer(klass.add(0x10));
    let name = '';
    for (let i = 0; i < 64; i++) {
      const c = u8(address.add(i));
      if (c === 0) return name;
      if (c < 32 || c > 126) throw new Error('Invalid class name');
      name += String.fromCharCode(c);
    }
    throw new Error('Class name exceeds limit');
  }
  function arrayLength(array, cap) {
    if (array.isNull()) throw new Error('Map array not initialized; open the kingdom map');
    const value = checked(array.add(0x18), 8).readU64();
    if (value.compare(uint64(cap)) > 0) throw new Error('Array capacity exceeds probe limit');
    return value.toNumber();
  }
  const i32 = a => checked(a, 4).readS32();
  function cstring(object) {
    if (object.isNull()) return null;
    if (className(pointer(object)) !== 'CString') throw new Error('Expected CString for cached text');
    const length = i32(object.add(0x10));
    const capacity = i32(object.add(0x14));
    const string = pointer(object.add(0x18));
    if (length < 0 || length > 128 || capacity < length || capacity > 4096) {
      throw new Error('Cached text length outside probe limits');
    }
    if (string.isNull()) {
      if (length === 0) return '';
      throw new Error('Missing cached text backing string');
    }
    if (className(pointer(string)) !== 'String') throw new Error('Expected managed String');
    const backingLength = i32(string.add(0x10));
    if (backingLength < length || backingLength > 4096) throw new Error('Invalid backing string length');
    const text = Array.from({length}, (_, i) => String.fromCharCode(u16(string.add(0x14 + i * 2)))).join('');
    if (!pointer(object.add(0x18)).equals(string) || i32(object.add(0x10)) !== length ||
        i32(object.add(0x14)) !== capacity || i32(string.add(0x10)) !== backingLength) {
      throw new Error('Cached text changed during read; retry');
    }
    return text;
  }
  function mapCoordinates(layoutIndex, kingdom, layoutCapacity) {
    // Calibrated against two screenshots in kingdom 1364 only.
    if (kingdom !== 1364 || layoutCapacity !== 262144) return null;
    const y = Math.floor(layoutIndex / 256);
    const x = 2 * (layoutIndex % 256) + (y & 1);
    return {kingdom, x, y};
  }
  function sampleCastles(state, layoutCapacity, playerCapacity) {
    if (state.focusedKingdom !== state.cachedKingdom) throw new Error('Focused and cached kingdoms differ; wait for map loading');
    // Copy the bounded cache layout once. Entries may be from earlier views.
    const start = state.layout.add(0x20);
    const bytes = new Uint8Array(checked(start, layoutCapacity * 3).readByteArray(layoutCapacity * 3));
    const seen = new Set(), selected = [];
    let cachedCityEntries = 0;
    for (let index = 0; index < layoutCapacity; index++) {
      const offset = index * 3;
      if (bytes[offset + 2] !== 8) continue;
      cachedCityEntries++;
      const tableID = bytes[offset] | (bytes[offset + 1] << 8);
      if (tableID >= playerCapacity) throw new Error('City references a player table slot outside capacity');
      if (selected.length >= 4096) throw new Error('Cache entry limit exceeded');
      selected.push({layoutIndex: index, tableID});
      seen.add(tableID);
    }
    function readRecord(item) {
      const entry = start.add(item.layoutIndex * 3);
      if (u8(entry.add(2)) !== 8 || u16(entry) !== item.tableID) throw new Error('City reference changed; retry');
      const record = state.players.add(0x20 + item.tableID * 0x50);
      const before = hex(record, 0x50);
      const result = {...item, playerName: cstring(pointer(record.add(0x30))),
        rawLevel: u8(record.add(0x18)), playerKingdomRaw: u16(record.add(0x14)),
        coordinates: mapCoordinates(item.layoutIndex, state.cachedKingdom, layoutCapacity),
        guildTag: cstring(pointer(record.add(0x20))), guildName: cstring(pointer(record.add(0x28))),
        might: checked(record, 8).readU64().toString(),
        troopsKilled: checked(record.add(8), 8).readU64().toString()};
      if (hex(record, 0x50) !== before) throw new Error('Player record changed during read; retry');
      return result;
    }
    const records = selected.map(readRecord);
    return {records, cachedCityEntries, uniqueReferencedSlots: seen.size,
      verify: () => {
        const after = new Uint8Array(checked(start, bytes.length).readByteArray(bytes.length));
        if (after.some((value, i) => value !== bytes[i]) ||
            JSON.stringify(records) !== JSON.stringify(selected.map(readRecord))) {
          throw new Error('Castle sample changed during read; retry');
        }
      }};
  }
  function chain(base) {
    const slot = pointer(base.add(0x81e3360));
    const klass = pointer(slot);
    const statics = pointer(klass.add(0xb8));
    const data = pointer(statics.add(0x18));
    if (data.isNull()) throw new Error('DataManager not initialized; open the kingdom map');
    // mapDataController is static; instance + 0x20 is AITable.
    const map = pointer(statics.add(0x20));
    if (map.isNull()) throw new Error('MapManager not initialized; open the kingdom map');
    return {slot, klass, statics, data, map};
  }
  function header(map) {
    return {
      zoneCount: u8(map.add(0x19)),
      zones: pointer(map.add(0x20)),
      layout: pointer(map.add(0x68)),
      cachedKingdom: u16(map.add(0x80)),
      players: pointer(map.add(0xa0)),
      focusedKingdom: u16(map.add(0x1ee)),
      initialized: u8(map.add(0x1f0))
    };
  }
  try {
    if (Process.arch !== 'x64' || Process.pointerSize !== 8) {
      throw new Error('Use the native x64 realm');
    }
    readableRanges = Process.enumerateRanges({protection: 'r--', coalesce: false})
      .filter(r => r.protection.startsWith('r')).sort((a, b) => a.base.compare(b.base));
    diagnostics.rangeInventoryMs = Date.now() - readStarted;
    diagnostics.readableRangeCount = readableRanges.length;
    const candidates = readableRanges.filter(r => r.file && r.file.offset === 0 && r.file.path.endsWith('/libil2cpp.so'));
    if (candidates.length > 16) throw new Error('Too many library mappings');
    const matches = candidates.filter(r => {
      try {
        return hex(r.base, 6) === '7f454c460201' && u16(r.base.add(18)) === 183 &&
          expected.every(([offset, bytes]) => hex(r.base.add(offset), bytes.length / 2) === bytes);
      } catch (_) { return false; }
    });
    if (matches.length !== 1) throw new Error('Expected one matching build; found ' + matches.length);
    const base = matches[0].base;
    stage = 'DataManager and MapManager pointers';
    const roots = chain(base);
    diagnostics.libraryBase = String(base);
    diagnostics.chain = Object.fromEntries(Object.entries(roots).map(([key, value]) => [key, String(value)]));
    // Collect each result independently: one mismatch must not hide the others.
    function inspectClass(klass) {
      try { return {address: String(klass), name: className(klass)}; }
      catch (error) { return {address: String(klass), error: String(error.message || error)}; }
    }
    function inspectObject(object) {
      try { return inspectClass(pointer(object)); }
      catch (error) { return {error: String(error.message || error)}; }
    }
    diagnostics.expectedDataClass = inspectClass(roots.klass);
    diagnostics.actualDataClass = inspectObject(roots.data);
    diagnostics.actualMapClass = inspectObject(roots.map);
    const checks = {
      singletonClassIdentity: diagnostics.actualDataClass.address === String(roots.klass),
      expectedDataClassName: diagnostics.expectedDataClass.name === 'DataManager',
      actualDataClassName: diagnostics.actualDataClass.name === 'DataManager',
      actualMapClassName: diagnostics.actualMapClass.name === 'MapManager'
    };
    diagnostics.checks = checks;
    if (!Object.values(checks).every(Boolean)) {
      throw new Error('Object class validation failed: ' +
        Object.keys(checks).filter(key => !checks[key]).join(', '));
    }
    stage = 'map cache header';
    const state = header(roots.map);
    if (state.initialized !== 1) throw new Error('Map focus not initialized; open the kingdom map');
    const zoneCapacity = arrayLength(state.zones, 256);
    const layoutCapacity = arrayLength(state.layout, 1048576);
    const playerCapacity = arrayLength(state.players, 65536);
    if (state.zoneCount > zoneCapacity) throw new Error('Zone count exceeds array capacity');
    const readZones = () => Array.from({length: state.zoneCount},
      (_, i) => u16(state.zones.add(0x20 + i * 2)));
    const zoneIDs = readZones();
    stage = 'cached castle sample';
    const sample = sampleCastles(state, layoutCapacity, playerCapacity);
    stage = 'snapshot consistency';
    sample.verify();
    const finalRoots = chain(base), finalState = header(roots.map);
    const finalZones = readZones();
    const finalCapacities = {
      zones: arrayLength(state.zones, 256), layout: arrayLength(state.layout, 1048576),
      players: arrayLength(state.players, 65536)
    };
    const changes = [];
    const compareFields = (prefix, before, after) => {
      for (const key of Object.keys(before)) {
        if (String(before[key]) !== String(after[key])) {
          changes.push({field: prefix + '.' + key, before: String(before[key]), after: String(after[key])});
        }
      }
    };
    compareFields('roots', roots, finalRoots);
    compareFields('header', state, finalState);
    compareFields('capacities', {zones: zoneCapacity, layout: layoutCapacity, players: playerCapacity}, finalCapacities);
    if (JSON.stringify(zoneIDs) !== JSON.stringify(finalZones)) {
      changes.push({field: 'zoneIDs', before: zoneIDs, after: finalZones});
    }
    if (changes.length) {
      diagnostics.consistencyChanges = changes;
      throw new Error('Map changed during read: ' + changes.map(c => c.field).join(', '));
    }
    return {
      probeVersion: 'cache-collector-3', status: 'cache-readable', architecture: Process.arch, libraryBase: String(base),
      focusedKingdom: state.focusedKingdom, cachedKingdom: state.cachedKingdom,
      focusInitialized: true, zoneIDs,
      recordLimit: 4096, records: sample.records,
      cachedCityEntries: sample.cachedCityEntries, uniqueReferencedSlots: sample.uniqueReferencedSlots,
      tableCapacities: {zones: zoneCapacity, layout: layoutCapacity, players: playerCapacity},
      scope: 'Bounded client cache references only; entries may be stale or from earlier map views. Coordinate conversion is calibrated for kingdom1364 with layout capacity262144 only; other layouts return null. Counts cover cached references, not the full kingdom. Might, kills and guild fields need comparison with the game. rawLevel semantics are unresolved; it is not a verified profile or castle level. Shields, freshness and full coverage remain unverified. Reads are not an atomic snapshot.'
    };
  } catch (error) {
    diagnostics.readMs = Date.now() - readStarted;
    return {status: 'not-confirmed', stage,
      reason: String(error.message || error), diagnostics};
  }
}

// Config is injected by collect.py from validated numeric arguments.
if (typeof COLLECTOR_OPTIONS !== 'undefined') {
  const emit = () => {
    const started = Date.now();
    const payload = readSnapshot();
    send({type: 'snapshot', agentReadMs: Date.now() - started, payload});
    setTimeout(emit, COLLECTOR_OPTIONS.intervalMs);
  };
  send({type: 'ready', version: 'cache-collector-3'});
  // Return from script.load before the potentially slow initial memory read.
  setImmediate(emit);
}
