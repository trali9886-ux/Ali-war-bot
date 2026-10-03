"""Lords Mobile 2.201 application-payload decoders recovered from ARM64 code.

Inputs are plaintext payloads at the named client handler, NOT socket frames.
No authentication, network I/O or server calls. Unsupported formats fail closed.
"""
import struct

BUILD = 'com.igg.android.lordsmobile/2.201/692/arm64'


class DecodeError(ValueError):
    pass


class UnsupportedKind(DecodeError):
    def __init__(self, kind, offset):
        self.kind, self.offset = kind, offset
        super().__init__(f'unsupported map record kind {kind} at payload offset {offset}; no complete result emitted')


class Reader:
    def __init__(self, data):
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise DecodeError('payload must be bytes-like')
        size = data.nbytes if isinstance(data, memoryview) else len(data)
        if size > 65535:
            raise DecodeError('payload exceeds the supported 65535-byte bound')
        self.data = bytes(data)
        self.offset = 0

    def take(self, n):
        if n < 0 or n > len(self.data) - self.offset:
            raise DecodeError(f'truncated or invalid field at payload offset {self.offset}')
        result = self.data[self.offset:self.offset+n]
        self.offset += n
        return result

    def unpack(self, fmt):
        return struct.unpack('<' + fmt, self.take(struct.calcsize('<' + fmt)))

    def integer(self, fmt):
        return self.unpack(fmt)[0]

    def text(self, size):
        raw = self.take(size).split(b'\0', 1)[0]
        try:
            return raw.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise DecodeError(f'invalid UTF-8 field ending at {self.offset}') from exc

    def finish(self):
        if self.offset != len(self.data):
            raise DecodeError(f'unconsumed bytes at payload offset {self.offset}')


def decode_shield_log(payload):
    """ShieldLogManager.RecvShieldLogList: count:u8, entries:(u16,i64,i64).

    IsActive/IsEmpty are computed by the client, not extra wire fields.
    Time values retain their original units; this decoder does not infer expiry.
    The handler has ten slots. No claim is made about other players' access.
    """
    r = Reader(payload)
    count = r.integer('B')
    if count > 10:
        raise DecodeError('shield log count exceeds the ten slots in this build')
    entries = []
    for _ in range(count):
        item, begin, end = r.unpack('Hqq')
        entries.append(dict(item_id=item, begin_time_raw=begin, end_time_raw=end))
    r.finish()
    return dict(build=BUILD, handler='ShieldLogManager.RecvShieldLogList',
                scope='session shield log; arbitrary enemy access unverified', entries=entries)


def encode_map_request(zone_count_raw, zones, revisions, renew=False):
    """Build only the 41-byte application payload; never sends a request."""
    def bounded(value, upper):
        return type(value) is int and 0 <= value <= upper
    if not bounded(zone_count_raw, 255):
        raise DecodeError('zone_count_raw must fit one byte')
    if len(zones) != 4 or any(not bounded(x, 65535) for x in zones):
        raise DecodeError('exactly four uint16 zone slots required')
    if len(revisions) != 4 or any(not bounded(x, 2**64-1) for x in revisions):
        raise DecodeError('exactly four uint64 revision slots required')
    if type(renew) is not bool:
        raise DecodeError('renew must be boolean')
    return struct.pack('<B4H4Q', zone_count_raw, *zones, *([0]*4 if renew else revisions))


def decode_map_request(payload):
    r = Reader(payload)
    count, *slots = r.unpack('B4H4Q')
    r.finish()
    return dict(zone_count_raw=count, zone_slots=slots[:4], revision_slots=slots[4:])


def decode_map_updates(payload, *, bulk_context=None):
    """Decode the verified subset of MapManager.RecvMapInfoPlus records.

    A packet may mix kinds. Unsupported kinds reject the entire packet. This
    prevents a partially decoded stream from being advertised as complete.
    Bulk baseline kinds 22/23 use a captured width context. Point additions
    preserve an opaque body. Unknown record kinds reject the whole payload.
    Zone/point IDs stay raw; instance/custom map geometry must be established.
    """
    r = Reader(payload)
    context = dict(bulk_context or {})
    events = []
    supported = {1, 2, 6, 7, 8, 9, 12, 15, 16, 17, 24}
    while True:
        start = r.offset
        kind = r.integer('B')
        if kind == 0:
            r.finish()
            if bulk_context is not None:
                bulk_context.update(context)
            return dict(build=BUILD, handler='MapManager.RecvMapInfoPlus',
                        complete_parse=True, complete_world_state=False, events=events)
        if kind in (22, 23):
            from bulk import decode_bulk
            event = decode_bulk(r, kind, context)
            event['payload_offset'] = start
            events.append(event)
            continue
        if kind not in supported:
            raise UnsupportedKind(kind, start)
        event = dict(kind=kind, payload_offset=start)
        if kind == 24:
            event.update(type='zone_none', zone=r.integer('H'))
            events.append(event)
            continue
        event['revision_raw'] = r.integer('Q')
        if kind in (1, 12):
            size = r.integer('h')
            if size < 3:
                raise DecodeError(f'invalid record size {size} at offset {start}')
            body = Reader(r.take(size))
            event['zone'], event['point'] = body.unpack('HB')
            if kind == 1:
                event.update(type='point_add_opaque', point_kind_raw=body.integer('B'),
                             fields_decoded=False)
                event['opaque_hex'] = body.take(len(body.data)-body.offset).hex()
            else:
                event.update(type='player_advance', alliance_name=body.text(20))
                vip, rank, portrait, bounty, might, kills, skin = body.unpack('BBHIQQH')
                event.update(vip=vip, alliance_rank=rank, portrait_id=portrait,
                             bounty=bounty, might=might, kills=kills, leader_skin=skin)
                event['extension_hex'] = body.take(len(body.data)-body.offset).hex()
            body.finish()
        else:
            event['zone'] = r.integer('H')
            if kind in (15, 16, 17):
                event['line_id'] = r.integer('I')
                if kind == 15:
                    event['type'] = 'line_delete'
                elif kind == 16:
                    event.update(type='line_owner_name', owner_name=r.text(13))
                else:
                    event.update(type='line_owner_tag', owner_tag=r.text(3))
            else:
                event['point'] = r.integer('B')
                if kind == 2:
                    event['type'] = 'point_delete'
                elif kind == 6:
                    event.update(type='player_name', name=r.text(13))
                elif kind == 7:
                    event.update(type='player_tag', guild=r.text(3))
                elif kind == 8:
                    event.update(type='player_level', castle_level=r.integer('B'))
                elif kind == 9:
                    event.update(type='player_capital_flag', capital_flag_raw=r.integer('B'))
        events.append(event)
