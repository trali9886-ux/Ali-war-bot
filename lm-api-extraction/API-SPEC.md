# Extracted map protocol, build 692

All multibyte values below are little endian. Addresses are ELF virtual addresses in the exact ARM64 library, not Windows x64 function addresses. `verified.json` ties assertions to the input hashes.

## Request surface

| Symbol | ID / address | Extracted behavior |
|---|---|---|
| `_MSG_REQUEST_MAPDATA` | 2201 (`0x899`) | Normal map request selector |
| `_MSG_REQUEST_INSTANCE_MAPDATA` | 2233 (`0x8b9`) | Instance-map selector in the same serializer |
| `_MSG_RESP_UPDATE_MAPINFO_PLUS` | 2220 | Metadata response ID; inspected guest dispatcher routes eligible foreign-kingdom updates to RecvMapInfoPlus |
| `MapManager.setLastZoneInfo` | `0x44de8dc` | Accepts count, four-slot array, renew boolean; either sends or queues according to current zone state |
| `MapManager.sendRequestMapdataMsg` | `0x44de9d8` | Builds count, four zone IDs and four revisions; selects normal/guest packet based on focused kingdom |
| `MapManager.RecvMapInfoPlus` | `0x43fa3a8` | Parses baseline and incremental records |
| `MessagePacket.AddSeqId` | `0x46c2284` | Increments and appends an int32 sequence while connected |
| `MessagePacket.Send` | `0x46bb598` | Writes frame header and chooses main/guest transport |

The 41-byte map body is:

| Offset | Width | Field |
|---:|---:|---|
| 0 | 1 | zone count raw |
| 1 | 8 | four uint16 zone slots |
| 9 | 32 | four uint64 revision slots |

`renew=true` writes zero to all four revisions. It is not a separate byte on the wire. The kingdom ID is not embedded in these 41 bytes; session/channel/map state matters. The normal caller supports 1–4 active zone slots. The low-level builder preserves the raw byte for inspection and does not validate a server's accepted zone ranges.

The serializer invokes the packet's sequence method before appending these fields. Thus the 41-byte body must not be sent alone as an entire socket frame. On the inspected main connected path, the nominal frame has a 4-byte header, a 4-byte sequence prefix and the 41-byte body, before any transport-specific processing.

At `0x44debe8` the method sets `MapManager.wait` to float 1.5. This is client state, not proof of a server rate limit. `setLastZoneInfo` also checks completion state and can defer a request. A direct implementation needs its own bounded request/response scheduling and measured server behavior.

## Minimap request candidate

`MapManager.requestMinMap(byte)` at `0x44e655c` selects `_MSG_REQUEST_MIN_MAP_PLUS` (2241 / `0x8c1`), appends its byte argument after sequence handling, and sends the packet. The catalog also contains `_MSG_RESP_MIN_MAP_PLUS` (2242) and `_MSG_RESP_UPDATE_MIN_MAPINFO` (2245). Their full response handlers and data coverage are not decoded here. A minimap response must not be assumed to carry a complete named player inventory.

## Bulk records 22 and 23

These take an early branch before the ordinary record/revision switch. Treating them like incremental records would misalign parsing.

```text
kind: u8 (22 or 23)
packed_counts: u16
  bits 12..15: zone-header count
  bits  6..11: point-record count
  bits  0.. 5: march-record count
if zone-header count > 0:
  repeat: zone:u16, revision:u64
  point_record_size:u8
  march_record_size:u8
repeat point count: fixed-width point record
repeat march count: fixed-width march record
```

Widths persist across continuation chunks. Header updates accept point sizes 41–128 and line sizes 50–128; this decoder requires line size at least 60 because the current complete line path consumes 60 bytes. Constructor defaults 40/49 are historical values and are not silently assumed. The implementation rejects a continuation whose required width is unavailable.

Kind 23 notifies the client's accumulated zones and clears the batch list. This is a batch marker, not a guarantee that all kingdom zones have arrived. The packet's zero-kind terminator is a separate boundary. Revision zero is preserved raw even though the client sometimes normalizes it internally to one.

### City/camp point kinds 8 and 9

A point record starts `zone:u16, point:u8, point_kind:u8`. The current city/camp body then reads:

```text
player_name: 13 fixed bytes
alliance_tag: 3 fixed bytes
kingdom_id: u16
castle_level, capital_flag, kingdom_title, world_title: u8 each
alliance_kingdom_id: u16
city_property, city_outward, city_outward_level: u8 each
nobility_title, city_attribute_flag: u8 each
city_attributes: 5 raw bytes
extension/padding: any intervening bytes in the negotiated width
base_flag: u8
emoji_id: u16
```

Minimum total width is 41 bytes. Other point categories are retained as opaque bodies at the negotiated boundaries. Strings are decoded as UTF-8 before the first zero byte, consuming their full fixed width. No shield duration, permanent player ID, Might or kills is present in this baseline path.

### March line records

The 60-byte fixed prefix is:

```text
line_id:u32, player_name:13 bytes, alliance_tag:3 bytes
kingdom_id:u16
start_zone:u16, start_point:u8, end_zone:u16, end_point:u8
begin_raw:u64, during_raw:u32, extra_begin_raw:u32, extra_during_raw:u32
line_flag:u8, base_flag:u8, emoji_id:u16
feature_id:u8, troop_skin_id:u16, troop_skin_level:u8
destination_alliance_id:u32
extension: remaining negotiated bytes
```

These are raw timestamps/durations and flags until checked against a live labeled sample.

## Incremental map records

The inherited decoder supports kinds 1,2,6,7,8,9,12,15,16,17,24. Most begin with a uint64 revision; kind 24 does not. Kind 12 has a signed int16 size, zone:u16 and point:u8 followed by alliance name (20 bytes), VIP:u8, alliance rank:u8, portrait:u16, bounty:u32, Might:u64, kills:u64 and leader skin:u16. Trailing extension bytes are preserved. Unknown kinds reject the entire message, rather than returning an apparently complete partial parse.

## Main transport

The connection path supplies socket type 1 and protocol 6 (stream/TCP). The inspected main-channel frame is:

```text
length:u16 (includes the 4-byte header)
protocol:u16
body:length-4 bytes
```

The inspected receive loop accepts frame lengths 4–4096 and constructs the handler packet from bytes after the header. The envelope inspector supports only this boundary. It does not infer a guest channel format, reassemble TCP chunks, strip outgoing sequences or decrypt arbitrary captures.

`NetworkManager.Cipher` at `0x46c3058` uses a client-configured transform gated by connection state and rounds the processed length down to an 8-byte boundary. Metadata contains `SessionKey`, `DES` and `Crypto` members. A complete standalone cipher initialization implementation has not been recovered or tested here. The inspected main receive caller passes zero to the cipher's guard argument; that particular call skips the transform. Do not assume that all directions or channels share one encryption rule.

## Remaining connection requirements

The APK exposes login and server-selection methods, but there is no verified static public HTTP URL that returns the full player map. Actual host/port selection, authenticated login state, main versus guest channel, sequence lifecycle, cryptographic setup, reconnect behavior and live batch semantics remain integration work. The current package establishes byte layouts and evidence, not unrestricted server access or measured scan speed.
