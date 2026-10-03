const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(require('path').join(__dirname, 'agent.js'), 'utf8');
function run(change = () => {}, scheduled = false) {
  const events = []; let tick, interval, immediate, enumerations = 0;
  const memory = new Map(), reads = new Map();
  let hook = () => {};
  const put = (a, n, size) => { n = BigInt(n); for(let i=0;i<size;i++) memory.set(a+i, Number((n >> BigInt(8*i)) & 255n)); };
  const bytes = (a, b) => Buffer.from(b).forEach((v,i)=>memory.set(a+i,v));
  const get = (a, size) => { hook(a, size); let n=0n; for(let i=0;i<size;i++) { assert(memory.has(a+i), 'Uninitialized mock address '+a.toString(16)); n |= BigInt(memory.get(a+i)) << BigInt(8*i); } return n; };
  class P {
    constructor(n) { this.n=Number(n); }
    add(n){return new P(this.n+n)} isNull(){return this.n===0}
    compare(p){return Math.sign(this.n-p.n)} equals(p){return this.n===p.n}
    toString(){return '0x'+this.n.toString(16)}
    readPointer(){return new P(get(this.n,8))} readU8(){return Number(get(this.n,1))}
    readU16(){return Number(get(this.n,2))} readS32(){return Number(BigInt.asIntN(32,get(this.n,4)))}
    readU64(){const n=get(this.n,8);return {compare: x=>n<x?-1:n>x?1:0,toNumber:()=>Number(n),toString:()=>n.toString()}}
    readByteArray(size){return Uint8Array.from({length:size},(_,i)=>Number(get(this.n+i,1))).buffer}
  }
  const base=0x10000000, slot=0x20000000, klass=0x20001000, statics=0x20002000;
  const data=0x20003000, map=0x20004000, mapClass=0x20005000, zones=0x20006000, layout=0x20007000, players=0x20008000;
  bytes(base, Buffer.from('7f454c460201','hex')); put(base+18,183,2);
  for(const m of source.matchAll(/\[(0x[0-9a-f]+), '([0-9a-f]+)'\]/g)) bytes(base+Number(m[1]),Buffer.from(m[2],'hex'));
  put(base+0x81e3360,slot,8); put(slot,klass,8);put(klass+0xb8,statics,8);put(statics+0x18,data,8);put(data,klass,8);put(statics+0x20,map,8);
  put(data+0x20,0x2000b000,8); put(0x2000b000,0x2000c000,8); put(0x2000c010,0x2000d000,8); bytes(0x2000d000,Buffer.from("CExternalTableWithWordKey`1\0"));
  put(map,mapClass,8);put(klass+0x10,0x20009000,8);bytes(0x20009000,Buffer.from('DataManager\0'));
  put(mapClass+0x10,0x2000a000,8);bytes(0x2000a000,Buffer.from('MapManager\0'));
  put(map+0x19,2,1);put(map+0x20,zones,8);put(map+0x68,layout,8);put(map+0x80,1364,2);put(map+0xa0,players,8);put(map+0x1ee,1364,2);put(map+0x1f0,1,1);
  put(zones+0x18,4,8);put(layout+0x18,4,8);put(players+0x18,1000,8);put(zones+0x20,18,2);put(zones+0x22,19,2);
  // Explicit native layout fixture: 3-byte MapPoint and 80-byte unboxed PlayerPoint.
  bytes(layout+0x20,Buffer.from([0,0,8, 1,0,0, 0,0,8, 1,0,9]));
  bytes(players+0x20,Buffer.alloc(160));
  put(players+0x20+0x18,25,1);put(players+0x20+0x14,1364,2);
  put(players+0x20+0x30,0x2000e000,8);
  put(0x2000e000,0x2000e400,8);put(0x2000e010,5,4);put(0x2000e014,16,4);put(0x2000e018,0x2000e100,8);
  put(0x2000e100,0x2000e500,8);put(0x2000e110,5,4);bytes(0x2000e114,Buffer.from('Alice','utf16le'));
  put(0x2000e410,0x2000e600,8);bytes(0x2000e600,Buffer.from('CString\0'));
  put(0x2000e510,0x2000e700,8);bytes(0x2000e700,Buffer.from('String\0'));
  const ranges=[{base:new P(base),size:0x9000000,protection:'r--',file:{offset:0,path:'/lib/arm64/libil2cpp.so'}},{base:new P(slot),size:0x10000,protection:'rw-'}];
  change({put,bytes,base,slot,klass,statics,data,map,zones,layout,players,ranges,setHook:h=>hook=h,reads});
  let output;
  output=JSON.parse(JSON.stringify(vm.runInNewContext(source+';readSnapshot()',{ ...(scheduled ? {COLLECTOR_OPTIONS:{intervalMs:2000},send:e=>events.push(e),setImmediate:fn=>{immediate=fn},setTimeout:(fn,ms)=>{tick=fn;interval=ms}} : {}), Process:{arch:'x64',pointerSize:8,enumerateRanges:()=>{enumerations++;return ranges},findRangeByAddress:()=>{throw new Error('Unexpected per-read range lookup')}},uint64:BigInt,console:{log:s=>output=JSON.parse(s)}})));
  if (scheduled) { assert.equal(events.length,1); assert.equal(events[0].type,'ready'); assert.equal(tick,undefined); immediate(); tick(); return {events, interval}; }
  assert.equal(enumerations,1);
  return output;
}
let result=run();assert.equal(result.status,'cache-readable');assert.equal(result.focusedKingdom,1364);assert.deepEqual(result.zoneIDs,[18,19]);assert.equal(result.tableCapacities.players,1000);
const cases=[
  ['bad class', c=>c.bytes(0x20009000,Buffer.from('WrongClass\0')), /class validation/],
  ['null singleton',c=>c.put(c.statics+0x18,0,8),/not initialized/],
  ['unreadable map',c=>c.put(c.statics+0x20,0x30000000,8),/Unreadable/],
  ['oversized capacity',c=>c.put(c.players+0x18,2n**63n,8),/capacity exceeds/],
  ['zone count overflow',c=>c.put(c.map+0x19,5,1),/Zone count/],
  ['uninitialized focus',c=>c.put(c.map+0x1f0,0,1),/focus not initialized/],
  ['wrong signature',c=>c.put(c.base+0x4f94474,0,1),/matching build/],
  ['changing focus',c=>{let count=0;c.setHook((a)=>{if(a===c.map+0x1ee && ++count===2)c.put(a,1365,2)})},/Map changed/],
  ['truncated read',c=>{c.ranges[1].size=0x4001},/Unreadable/]
];
for(const [name,change,pattern] of cases){result=run(change);assert.equal(result.status,'not-confirmed',name);assert.match(result.reason + ' ' + JSON.stringify(result.diagnostics),pattern,name)}
console.log('PASS: valid map header and 9 rejection/consistency fixtures');

result=run(c=>c.bytes(0x20009000,Buffer.from('UnexpectedType\0')));
assert.equal(result.diagnostics.expectedDataClass.name,'UnexpectedType');
assert.equal(result.diagnostics.actualMapClass.name,'MapManager');
assert.equal(result.diagnostics.checks.actualMapClassName,true);
assert.equal(result.diagnostics.checks.expectedDataClassName,false);
assert.equal(result.tableCapacities,undefined);
result=run(c=>c.put(c.data,0x30000000,8));
assert.equal(result.diagnostics.checks.singletonClassIdentity,false);
assert.match(result.diagnostics.actualDataClass.error,/Unreadable/);
assert.equal(result.diagnostics.actualMapClass.name,'MapManager');
assert.equal(result.tableCapacities,undefined);
result=run(c=>c.bytes(0x2000a000,Buffer.from('OtherMap\0')));
assert.equal(result.diagnostics.actualMapClass.name,'OtherMap');
assert.equal(result.diagnostics.checks.actualMapClassName,false);
assert.equal(result.tableCapacities,undefined);
console.log('PASS: independent class diagnostics, unreadable class, and no header after mismatch');

// Regression: instance AITable is not a map; static field must be used.
result=run(); assert.equal(result.status,'cache-readable');
result=run(c=>c.put(c.statics+0x20,0x2000b000,8));
assert.equal(result.status,'not-confirmed');
assert.equal(result.diagnostics.actualMapClass.name,'CExternalTableWithWordKey`1');
result=run(c=>c.put(c.statics+0x20,0,8));
assert.equal(result.status,'not-confirmed'); assert.match(result.reason,/MapManager not initialized/);
console.log('PASS: static map storage regression and null static field');

result=run();assert.equal(result.records.length,2);assert.equal(result.records[0].playerName,'Alice');assert.equal(result.records[0].rawLevel,25);assert.equal(result.records[0].tableID,0);assert.equal(result.cachedCityEntries,2);assert.equal(result.uniqueReferencedSlots,1);
// Non-city and unreferenced player slots are not returned, duplicate references are preserved by layout location.
const sampleCases=[
 ['invalid slot',c=>c.put(c.layout+0x20,1000,2),/outside capacity/],
 ['bad logical length',c=>c.put(0x2000e010,129,4),/length outside/],
 ['truncated backing',c=>c.put(0x2000e110,3,4),/backing string length/],
 ['wrong CString',c=>c.bytes(0x2000e600,Buffer.from('Other\0')),/Expected CString/],
 ['kingdom mismatch',c=>c.put(c.map+0x80,1,2),/kingdoms differ/],
 ['changing name',c=>{let n=0;c.setHook(a=>{if(a===0x2000e114 && ++n===2)c.put(a,66,2)})},/sample changed/]
];
for(const [name,change,pattern] of sampleCases){result=run(change);assert.equal(result.status,'not-confirmed',name);assert.match(result.reason,pattern,name);assert.equal(result.records,undefined)}
result=run(c=>{c.put(0x2000e010,3,4);c.put(0x2000e110,3,4);c.bytes(0x2000e114,Buffer.from('A🌟','utf16le'))});assert.equal(result.records[0].playerName,'A🌟');
result=run(c=>c.bytes(c.layout+0x20,Buffer.alloc(12)));assert.deepEqual(result.records,[]);assert.equal(result.cachedCityEntries,0);
console.log('PASS: city references, deduplication, non-city filtering, string bounds, mutation, Unicode, empty cache');
result=run(c=>{
 c.put(c.layout+0x18,12,8);
 for(let i=0;i<12;i++){
  c.put(c.layout+0x20+i*3,i,2);c.put(c.layout+0x22+i*3,8,1);
  c.bytes(c.players+0x20+i*80,Buffer.alloc(80));
  c.put(c.players+0x20+i*80+0x30,0x2000e000,8);
 }
});
assert.equal(result.records.length,12);assert.equal(result.cachedCityEntries,12);assert.equal(result.uniqueReferencedSlots,12);
console.log('PASS: all twelve references returned; no ten-record limit');

result=run(c=>{
 c.put(c.players+0x20,9007199254740993n,8);c.put(c.players+0x28,18446744073709551615n,8);
 c.put(c.players+0x40,0x2000e000,8);c.put(c.players+0x48,0x2000e000,8);
});
assert.equal(result.records[0].might,'9007199254740993');assert.equal(result.records[0].troopsKilled,'18446744073709551615');
assert.equal(result.records[0].guildTag,'Alice');assert.equal(result.records[0].guildName,'Alice');
assert.equal(result.records[0].level,undefined);assert.equal(result.records[0].coordinates,null);
result=run();assert.equal(result.records[0].guildTag,null);assert.equal(result.records[0].guildName,null);
// Exercise the actual coordinate helper with independently observed screenshot pairs.
const helper=source.slice(source.indexOf('  function mapCoordinates('),source.indexOf('  function sampleCastles('));
const coordinates=vm.runInNewContext(helper+';mapCoordinates');
for (const [index,x,y] of [[123239,207,481],[123496,208,482]]) {
 const result=coordinates(index,1364,262144);assert.equal(result.x,x);assert.equal(result.y,y);assert.equal(result.kingdom,1364);
}
assert.equal(coordinates(123239,1365,262144),null);assert.equal(coordinates(123239,1364,1024),null);
console.log('PASS: uint64 precision, guild fields, raw-level label, screenshot coordinates and unsupported layout gating');

result=run(c=>{let n=0;c.setHook(a=>{if(a===c.layout+0x20 && ++n===3)c.put(c.layout+0x25,8,1)})});
assert.equal(result.status,'not-confirmed');
console.log('PASS: layout mutation rejected');

const scheduled=run(()=>{},true);
assert.equal(scheduled.interval,2000);assert.equal(scheduled.events[0].type,'ready');
assert.equal(scheduled.events.filter(e=>e.type==='snapshot').length,2);
assert.equal(scheduled.events[1].payload.status,'cache-readable');
assert.equal(typeof scheduled.events[1].agentReadMs,'number');
console.log('PASS: initial and periodic snapshot send contract');

result=run(c=>c.ranges.reverse());assert.equal(result.status,'cache-readable');
result=run(c=>{c.ranges[1].protection='---'});assert.equal(result.status,'not-confirmed');
result=run(c=>{
 const r=c.ranges[1];r.size=0x4000;
 c.ranges.push({base:r.base.add(0x4008),size:0xbff8,protection:'rw-'});
});assert.equal(result.status,'not-confirmed');assert.match(result.diagnostics.actualMapClass.error,/Unreadable/);
result=run(c=>{let n=0;c.setHook(a=>{if(a===c.map+0x1ee && ++n===2)c.put(a,1365,2)})});
assert.equal(result.diagnostics.consistencyChanges[0].field,'header.focusedKingdom');
assert.equal(result.diagnostics.consistencyChanges[0].before,'1364');
assert.equal(result.diagnostics.consistencyChanges[0].after,'1365');
assert.equal(typeof result.diagnostics.readMs,'number');
console.log('PASS: one range inventory, unsorted ranges, unreadable range/hole rejection and precise consistency diagnostics');
