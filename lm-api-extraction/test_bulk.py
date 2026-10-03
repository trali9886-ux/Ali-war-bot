import struct
import unittest
from protocol import DecodeError, UnsupportedKind, decode_map_updates
from transport import decode_frames

# Literal synthetic fields independent of decoder packing formats.
PLAYER = bytes.fromhex('0200 03 08') + b'Alice' + bytes(8) + b'ABC' + bytes.fromhex(
    '5405 1e 04 02 03 5505 01 02 03 04 05 06 07 08 09 0a 0b 3412')
LINE = bytes.fromhex('04030201') + b'Bob' + bytes(10) + b'XYZ' + bytes.fromhex(
    '5405 0200 03 0400 05 0100000000000080 06000000 07000000 08000000 '
    '09 0a 0b00 0c 0d00 0e 0f000000')


def chunk(kind=23, points=PLAYER, lines=LINE, point_count=1, line_count=1, sizes=(41,60), header=True):
    packed = ((1 if header else 0) << 12) | (point_count << 6) | line_count
    prefix = bytes([kind]) + struct.pack('<H', packed)
    if header:
        prefix += bytes.fromhex('0200 0100000000000080') + bytes(sizes)
    return prefix + points + lines


class BulkTests(unittest.TestCase):
    def test_literal_bulk_fields_and_completion(self):
        self.assertEqual((len(PLAYER), len(LINE)), (41, 60))
        result = decode_map_updates(chunk()+b'\0')
        bulk = result['events'][0]
        self.assertEqual(bulk['zone_revisions'], [dict(zone=2, revision_raw=2**63+1)])
        self.assertTrue(bulk['ends_zone_batch'])
        self.assertFalse(result['complete_world_state'])
        p = bulk['points'][0]
        self.assertEqual((p['player_name'],p['alliance_tag'],p['castle_level']), ('Alice','ABC',30))
        self.assertEqual(p['city_attributes_raw'], [6,7,8,9,10])
        self.assertEqual((p['base_flag_raw'],p['emoji_id']), (11,0x1234))
        self.assertIsNone(p['might'])
        self.assertIsNone(p['kills'])
        self.assertIsNone(p['player_id'])
        line = bulk['lines'][0]
        self.assertEqual((line['line_id'],line['begin_raw']), (0x01020304,2**63+1))
        self.assertEqual((line['start_zone'],line['end_point'],line['destination_alliance_id']), (2,5,15))
        self.assertEqual((line['base_flag_raw'],line['emoji_id'],line['troop_skin_level']), (10,11,14))

    def test_continuation_context_and_transactional_failure(self):
        context = {}
        first = chunk(kind=22, lines=b'', line_count=0)+b'\0'
        self.assertFalse(decode_map_updates(first, bulk_context=context)['events'][0]['ends_zone_batch'])
        self.assertEqual(context, {'point_size':41,'line_size':60})
        continuation = chunk(header=False)+b'\0'
        self.assertTrue(decode_map_updates(continuation, bulk_context=context)['complete_parse'])
        with self.assertRaises(DecodeError): decode_map_updates(continuation)
        before = dict(context)
        with self.assertRaises(UnsupportedKind):
            decode_map_updates(chunk(points=b'',lines=b'',point_count=0,line_count=0,sizes=(50,70))+b'\xff', bulk_context=context)
        self.assertEqual(context, before)

    def test_opaque_points_and_extension_boundaries(self):
        opaque = PLAYER[:3]+b'\x0a'+PLAYER[4:]
        extension = PLAYER[:-3]+b'\xaa\xbb'+PLAYER[-3:]
        result = decode_map_updates(chunk(points=extension,lines=LINE+b'\xcc',sizes=(43,61))+b'\0')['events'][0]
        self.assertEqual(result['points'][0]['extension_hex'], 'aabb')
        self.assertEqual(result['points'][0]['emoji_id'], 0x1234)
        self.assertEqual(result['lines'][0]['extension_hex'], 'cc')
        result = decode_map_updates(chunk(points=opaque)+b'\0')['events'][0]
        self.assertFalse(result['points'][0]['fields_decoded'])
        self.assertEqual(result['points'][0]['opaque_hex'], PLAYER[4:].hex())

    def test_every_truncation_and_extra_bytes(self):
        raw = chunk()+b'\0'
        for n in range(len(raw)):
            with self.subTest(n=n), self.assertRaises(DecodeError): decode_map_updates(raw[:n])
        with self.assertRaises(DecodeError): decode_map_updates(raw+b'\0')

    def test_invalid_widths_and_text(self):
        for sizes in [(0,60),(40,60),(129,60),(41,49),(41,59),(41,129)]:
            with self.subTest(sizes=sizes), self.assertRaises(DecodeError): decode_map_updates(chunk(sizes=sizes)+b'\0')
        with self.assertRaises(DecodeError): decode_map_updates(chunk(points=PLAYER[:4]+b'\xff'+PLAYER[5:])+b'\0')

    def test_maximum_counts_and_multiple_chunks(self):
        a = chunk(kind=22, points=PLAYER*63,lines=b'',point_count=63,line_count=0)
        b = chunk(header=False,points=b'',lines=LINE*63,point_count=0,line_count=63)
        events = decode_map_updates(a+b+b'\0')['events']
        self.assertEqual((len(events[0]['points']),len(events[1]['lines'])), (63,63))

    def test_main_channel_envelope(self):
        raw = bytes.fromhex('0700 ac08 aabbcc 0400 9908')
        frames = decode_frames(raw)
        self.assertEqual([f['protocol'] for f in frames], [2220,2201])
        self.assertEqual(frames[0]['body_hex'], 'aabbcc')
        self.assertEqual(len(decode_frames(struct.pack('<HH',4096,2220)+bytes(4092))),1)
        for bad in [raw[:n] for n in (1,2,3,4,5,6,8,9,10)] + [bytes.fromhex('0300 ac08'),struct.pack('<HH',4097,2220)+bytes(4093)]:
            with self.subTest(size=len(bad)), self.assertRaises(DecodeError): decode_frames(bad)


if __name__ == '__main__': unittest.main()
