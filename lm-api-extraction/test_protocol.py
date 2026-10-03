import base64
import json
import struct
import unittest
from protocol import (BUILD, DecodeError, UnsupportedKind, decode_map_updates,
                      decode_shield_log, encode_map_request, decode_map_request)
from decode_capture import decode_record


def event(kind, body, revision=1):
    return bytes([kind]) + struct.pack('<Q', revision) + body


def capture(handler, payload):
    return dict(format='lm-handler-capture-v1', build=BUILD, handler=handler,
                payload_b64=base64.b64encode(payload).decode(), consumed=len(payload))


class ProtocolTests(unittest.TestCase):
    def test_literal_shield_entry(self):
        raw = bytes.fromhex('01 0201 0100000000000000 0200000000000000')
        self.assertEqual(decode_shield_log(raw)['entries'], [dict(item_id=258, begin_time_raw=1, end_time_raw=2)])

    def test_shield_count_boundaries(self):
        self.assertEqual(decode_shield_log(b'\0')['entries'], [])
        self.assertEqual(len(decode_shield_log(bytes([10])+bytes(180))['entries']), 10)
        for raw in [bytes([11])+bytes(198), b'\0\0']:
            with self.assertRaises(DecodeError): decode_shield_log(raw)

    def test_shield_every_truncation(self):
        raw = bytes([2]) + struct.pack('<Hqq', 1, 2, 3)*2
        for i in range(len(raw)):
            with self.subTest(i=i), self.assertRaises(DecodeError): decode_shield_log(raw[:i])

    def test_literal_name_level_flag_and_termination(self):
        name = bytes.fromhex('06 0100000000000000 0200 03') + b'Alice' + bytes(8)
        level = bytes.fromhex('08 0200000000000000 0200 03 19')
        flag = bytes.fromhex('09 0300000000000000 0200 03 04 00')
        result = decode_map_updates(name+level+flag)
        self.assertEqual(result['events'][0]['name'], 'Alice')
        self.assertEqual(result['events'][1]['castle_level'], 25)
        self.assertEqual(result['events'][2]['capital_flag_raw'], 4)
        self.assertNotIn('shield', result['events'][2])
        self.assertFalse(result['complete_world_state'])

    def test_player_advance_64bit_values_and_extension(self):
        body = struct.pack('<HB', 33, 42) + b'Guild' + bytes(15)
        body += struct.pack('<BBHIQQH', 12, 4, 300, 1234, 2**63+7, 2**53+1, 321)
        body += b'\xaa\xbb'
        result = decode_map_updates(event(12, struct.pack('<h', len(body))+body)+b'\0')['events'][0]
        self.assertEqual(result['might'], 2**63+7)
        self.assertEqual(result['kills'], 2**53+1)
        self.assertEqual(result['leader_skin'], 321)
        self.assertEqual(result['extension_hex'], 'aabb')

    def test_opaque_add_delete_line_records_and_zone_none(self):
        raw = event(1, struct.pack('<hHBB', 6, 1, 2, 8)+b'xx')
        raw += event(2, struct.pack('<HB', 1, 2))
        raw += event(15, struct.pack('<HI', 1, 123))
        raw += event(16, struct.pack('<HI', 1, 123)+b'Bob'+bytes(10))
        raw += event(17, struct.pack('<HI', 1, 123)+b'ABC')
        raw += bytes([24])+struct.pack('<H', 1)+b'\0'
        e = decode_map_updates(raw)['events']
        self.assertFalse(e[0]['fields_decoded'])
        self.assertEqual(e[0]['opaque_hex'], '7878')
        self.assertEqual(e[2]['line_id'], 123)
        self.assertEqual(e[3]['owner_name'], 'Bob')
        self.assertEqual(e[4]['owner_tag'], 'ABC')
        self.assertEqual(e[5]['type'], 'zone_none')

    def test_no_partial_result_on_unsupported_kind(self):
        for kind in [14, 25, 255]:
            raw = event(8, struct.pack('<HBB', 1, 2, 25)) + bytes([kind])
            with self.subTest(kind=kind), self.assertRaises(UnsupportedKind) as cm:
                decode_map_updates(raw)
            self.assertEqual(cm.exception.offset, 13)

    def test_map_truncation_trailing_and_invalid_text(self):
        raw = event(7, struct.pack('<HB', 1, 2)+b'ABC')+b'\0'
        for i in range(len(raw)):
            with self.subTest(i=i), self.assertRaises(DecodeError): decode_map_updates(raw[:i])
        for bad in [raw+b'\0', event(7, struct.pack('<HB', 1, 2)+b'\xffAB')+b'\0',
                    event(12, struct.pack('<h', 2)+b'xx')+b'\0']:
            with self.assertRaises(DecodeError): decode_map_updates(bad)

    def test_request_golden_and_renew(self):
        raw = encode_map_request(4, [1,2,3,16384], [1,2,3,4])
        self.assertEqual(len(raw), 41)
        self.assertEqual(raw[:9].hex(), '040100020003000040')
        self.assertEqual(decode_map_request(raw)['revision_slots'], [1,2,3,4])
        self.assertEqual(decode_map_request(encode_map_request(4,[1,2,3,4],[1,2,3,4],True))['revision_slots'], [0]*4)
        for bad in [raw[:-1], raw+b'\0']:
            with self.assertRaises(DecodeError): decode_map_request(bad)
        with self.assertRaises(DecodeError): encode_map_request(True,[1]*4,[1]*4)
        with self.assertRaises(DecodeError): encode_map_request(4,[1]*3,[1]*4)

    def test_capture_routing_and_rejection(self):
        record = capture('ShieldLogManager.RecvShieldLogList', b'\0')
        self.assertEqual(decode_record(record)['decoded']['entries'], [])
        self.assertTrue(decode_record(dict(record, synthetic=True))['synthetic'])
        for changes in [dict(build='wrong'),dict(consumed=5),dict(payload_b64='??'),dict(handler='Login')]:
            with self.subTest(changes=changes), self.assertRaises(DecodeError): decode_record(dict(record,**changes))

    def test_reject_oversized_payload(self):
        for bad in [bytes(65536), 1000000000, 'text']:
            with self.subTest(type=type(bad)), self.assertRaises(DecodeError): decode_map_updates(bad)


if __name__ == '__main__': unittest.main()
