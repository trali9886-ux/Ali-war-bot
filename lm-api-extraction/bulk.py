"""Static 2.201/692 map baseline layout. No network or game-process access."""
from protocol import DecodeError, Reader


def decode_bulk(reader, kind, context):
    """Consume a kind-22/23 baseline; context is a transaction-local dictionary.

    Point and line widths persist between chunks. Require a captured header or
    explicit verified context; the constructor's old widths (40/49) are too small
    for the complete current player/line field paths, so they are not guessed.
    """
    packed = reader.integer('H')
    zone_count, point_count, line_count = packed >> 12, (packed >> 6) & 63, packed & 63
    zones = []
    if zone_count:
        for _ in range(zone_count):
            zone, revision = reader.unpack('HQ')
            zones.append(dict(zone=zone, revision_raw=revision))
        point_size, line_size = reader.unpack('BB')
        # These are the acceptance conditions in RecvMapInfoPlus, not guesses.
        if 41 <= point_size <= 128:
            context['point_size'] = point_size
        if 50 <= line_size <= 128:
            context['line_size'] = line_size
    point_size, line_size = context.get('point_size'), context.get('line_size')
    if point_count and (type(point_size) is not int or not 41 <= point_size <= 128):
        raise DecodeError('bulk point width unavailable or unsupported; capture the initiating zone header')
    if line_count and (type(line_size) is not int or not 60 <= line_size <= 128):
        raise DecodeError('bulk line width unavailable or unsupported; current line path needs at least 60 bytes')
    points, lines = [], []
    for _ in range(point_count):
        point = Reader(reader.take(point_size))
        zone, point_id, point_kind = point.unpack('HBB')
        item = dict(zone=zone, point=point_id, point_kind_raw=point_kind)
        if point_kind in (8, 9):  # IsCityOrCamp: (kind & 0xfe) == 8
            item.update(type='city_or_camp', fields_decoded=True,
                        player_name=point.text(13), alliance_tag=point.text(3))
            keys = ('kingdom_id', 'castle_level', 'capital_flag_raw', 'kingdom_title_raw',
                    'world_title_raw', 'alliance_kingdom_id', 'city_property_raw',
                    'city_outward_raw', 'city_outward_level', 'nobility_title_raw',
                    'city_attribute_flag_raw')
            item.update(zip(keys, point.unpack('HBBBBHBBBBB')))
            item['city_attributes_raw'] = list(point.take(5))
            item['extension_hex'] = point.take(len(point.data) - point.offset - 3).hex()
            item['base_flag_raw'], item['emoji_id'] = point.unpack('BH')
            # Bulk base records do not carry these advanced values.
            item.update(might=None, kills=None, player_id=None)
        else:
            # Boundary extraction only; do not infer fields for other point kinds.
            item.update(type='point_opaque', fields_decoded=False,
                        opaque_hex=point.take(len(point.data)-point.offset).hex())
        point.finish()
        points.append(item)
    for _ in range(line_count):
        line = Reader(reader.take(line_size))
        item = dict(line_id=line.integer('I'), player_name=line.text(13), alliance_tag=line.text(3))
        keys = ('kingdom_id', 'start_zone', 'start_point', 'end_zone', 'end_point',
                'begin_raw', 'during_raw', 'extra_begin_raw', 'extra_during_raw',
                'line_flag_raw', 'base_flag_raw', 'emoji_id', 'feature_id',
                'troop_skin_id', 'troop_skin_level', 'destination_alliance_id')
        item.update(zip(keys, line.unpack('HHBHBQIIIBBHBHBI')))
        item['extension_hex'] = line.take(len(line.data)-line.offset).hex()
        line.finish()
        lines.append(item)
    return dict(type='bulk_baseline', kind=kind, header_raw=packed,
                zone_revisions=zones, point_size=point_size, line_size=line_size,
                points=points, lines=lines, ends_zone_batch=kind == 23,
                complete_world_state=False)
