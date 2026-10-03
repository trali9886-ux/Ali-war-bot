import contextlib
import io
import json
from pathlib import Path
import queue
import tempfile
import unittest
from unittest.mock import patch
import message_capture as capture

HEADER = bytes.fromhex('17 0010 0200 0100000000000000 293c 00')
CONTINUATION = bytes.fromhex('17 4000 02000308') + b'Alice'+bytes(8)+b'ABC'+bytes.fromhex('54051e04020355050102030405060708090a0b3412')+b'\0'


def frame(body=HEADER, socket=1, direction='incoming', opcode=2220):
    return dict(type='map_frame', socket=socket, direction=direction, opcode=opcode,
                bodyHex=body.hex(), frameBytes=len(body)+4)


class DecoderTests(unittest.TestCase):
    def test_continuation_and_socket_isolation(self):
        d = capture.Decoder()
        self.assertEqual(d.process(frame())['decodeStatus'], 'parsed_candidate')
        parsed = d.process(frame(CONTINUATION))
        self.assertEqual(parsed['decoded']['events'][0]['points'][0]['player_name'], 'Alice')
        self.assertFalse(parsed['decoded']['complete_world_state'])
        self.assertEqual(d.process(frame(CONTINUATION, socket=2))['decodeStatus'], 'unsupported_or_misaligned')

    def test_context_invalidation(self):
        for reset in [dict(type='capture_gap'), dict(type='stream_end'), dict(type='map_context_reset'),
                      frame(b'unsupported', direction='outgoing', opcode=2201), frame(b'\xff')]:
            d = capture.Decoder(); d.process(frame()); d.process(dict(reset, socket=1))
            self.assertEqual(d.process(frame(CONTINUATION))['decodeStatus'], 'unsupported_or_misaligned')

    def test_failed_message_does_not_commit_context(self):
        d = capture.Decoder(); result = d.process(frame(HEADER[:-1]+b'\xff'))
        self.assertEqual(result['bodyHex'], (HEADER[:-1]+b'\xff').hex())
        self.assertEqual(result['decodeStatus'], 'unsupported_or_misaligned'); self.assertNotIn(1, d.contexts)
        self.assertEqual(d.process(frame(CONTINUATION))['decodeStatus'], 'unsupported_or_misaligned')

    def test_outgoing_is_opaque(self):
        result = capture.Decoder().process(frame(bytes(45), direction='outgoing', opcode=2201))
        self.assertEqual(result['decodeStatus'], 'opaque'); self.assertNotIn('decoded', result)


class FakeConnection:
    events = []
    closed = False
    def __init__(self, frida, device, source, inbox, overflow):
        self.pid = 42; self.inbox = inbox; self.__class__.closed = False
        for event in self.events: inbox.put_nowait(event)
    def stop(self): self.inbox.put_nowait(dict(type='capture_stopped', socketBytes=0, framedMessages=0))
    def close(self): self.__class__.closed = True


class LifecycleTests(unittest.TestCase):
    def run_capture(self, events, check=False):
        class Connection(FakeConnection): pass
        Connection.events = events
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
            code = capture.capture(None, 'synthetic', -.01, Path(td), check, Connection)
            summary = json.loads((Path(td)/'summary.json').read_text())
            records = [json.loads(line) for line in (Path(td)/'messages.jsonl').read_text().splitlines()]
            self.assertTrue(Connection.closed)
            return code, summary, records

    def test_check_only_is_attachment_not_capture(self):
        code, summary, _ = self.run_capture([dict(type='ready')], True)
        self.assertEqual(code, 0); self.assertEqual(summary['status'], 'hooks_ready')
        self.assertFalse(summary['wholeKingdomComplete']); self.assertEqual(summary['decodedMapMessages'], 0)

    def test_no_messages_is_incomplete(self):
        code, summary, _ = self.run_capture([dict(type='ready')])
        self.assertEqual(code, 2); self.assertEqual(summary['status'], 'incomplete')

    def test_decode_and_gap_are_preserved(self):
        code, summary, records = self.run_capture([frame(), dict(type='capture_gap', socket=1, reason='test'), dict(type='ready')])
        self.assertEqual(code, 2); self.assertEqual(summary['decodedMapMessages'], 1)
        self.assertEqual(summary['captureGaps'], 1)
        self.assertTrue(any(x.get('decodeStatus') == 'parsed_candidate' for x in records))

    def test_agent_error_and_detach(self):
        for kind in ['agent_error', 'detached']:
            code, summary, _ = self.run_capture([dict(type=kind, reason='fixture')])
            self.assertEqual(code, 2); self.assertEqual(summary['reason'], 'fixture')

    def test_keyboard_interrupt_flush_and_cleanup(self):
        with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()), patch.object(queue.Queue, 'get', side_effect=[KeyboardInterrupt, dict(type='capture_stopped', socketBytes=0, framedMessages=0)]):
            code = capture.capture(None, 'synthetic', 60, Path(td), connection_factory=FakeConnection)
            summary = json.loads((Path(td)/'summary.json').read_text())
            self.assertEqual(code, 2); self.assertEqual(summary['status'], 'interrupted')
            self.assertEqual(summary['cleanupStatus'], 'complete')

class BoundaryTests(unittest.TestCase):
    run_capture = LifecycleTests.run_capture
    def test_partial_map_stream_at_stop(self):
        code, summary, _ = self.run_capture([frame(), dict(type='stream_end', socket=1,
            pendingBytes=2, mapTrafficObserved=True), dict(type='ready')])
        self.assertEqual(code, 2); self.assertEqual(summary['captureGaps'], 1)

    def test_unrelated_rejection(self):
        code, summary, _ = self.run_capture([dict(type='stream_rejected', socket=2), frame(), dict(type='ready')])
        self.assertEqual(code, 0); self.assertEqual(summary['rejectedStreams'], 1)
        self.assertEqual(summary['captureGaps'], 0)

    def test_output_limit(self):
        with patch.object(capture, 'MAX_LOG_BYTES', 1):
            with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
                code = capture.capture(None, 'synthetic', 1, Path(td), connection_factory=FakeConnection)
                summary = json.loads((Path(td)/'summary.json').read_text())
                self.assertEqual(code, 2); self.assertIn('output limit', summary['reason'])

    def test_cleanup_failure(self):
        with patch.object(capture, 'close_connection', side_effect=capture.CleanupIncomplete('fixture')):
            with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
                class Ready(FakeConnection): events = [dict(type='ready')]
                code = capture.capture(None, 'synthetic', 1, Path(td), True, Ready)
                summary = json.loads((Path(td)/'summary.json').read_text())
                self.assertEqual(code, 2); self.assertEqual(summary['cleanupStatus'], 'incomplete')


if __name__ == '__main__': unittest.main()
