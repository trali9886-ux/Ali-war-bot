"""Bounded live message observations; no input automation or server requests."""
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import sys
import threading
import time
from collect import Connection, close_connection, CleanupIncomplete

API_DIR = Path(__file__).resolve().parent.parent / 'lm-api-extraction'
sys.path.insert(0, str(API_DIR))
from protocol import DecodeError, decode_map_updates

MAX_LOG_BYTES = 64 * 1024 * 1024


def agent_source():
    catalog = json.loads((API_DIR / 'evidence' / 'protocols.json').read_text(encoding='utf-8'))
    options = {'protocols': sorted({row['id'] for row in catalog['protocols'] if row['id']})}
    base = Path(__file__).parent
    return 'const CAPTURE_OPTIONS = ' + json.dumps(options) + ';\n' + '\n'.join(
        (base / name).read_text(encoding='utf-8') for name in ('message_stream.js', 'message_agent.js'))


class CaptureConnection(Connection):
    def stop(self):
        self.script.post({'type': 'stop'})


class Decoder:
    def __init__(self):
        self.contexts = {}
        self.frames = self.decoded = self.failures = self.gaps = self.points = 0
        self.rejected = 0

    def process(self, event):
        event = dict(event)
        kind, socket = event.get('type'), event.get('socket')
        if kind in ('stream_start', 'stream_end', 'capture_gap', 'map_context_reset', 'stream_rejected'):
            self.contexts.pop(socket, None)
            if kind == 'stream_rejected':
                self.rejected += 1
            if kind == 'capture_gap' or (kind == 'stream_end' and event.get('pendingBytes') and event.get('mapTrafficObserved')):
                self.gaps += 1
            return event
        if kind != 'map_frame':
            return event
        self.frames += 1
        body = bytes.fromhex(event['bodyHex'])
        if len(body) > 4092 or len(body) + 4 != event['frameBytes']:
            raise ValueError('Invalid agent frame size')
        if event['direction'] == 'incoming' and event['opcode'] == 2220:
            try:
                result = decode_map_updates(body, bulk_context=self.contexts.setdefault(socket, {}))
                event.update(decodeStatus='parsed_candidate', decoded=result,
                             validation='socket framing and schema only; live game comparison required')
                self.decoded += 1
                self.points += sum(len(x.get('points', [])) for x in result['events'])
            except DecodeError as exc:
                self.contexts.pop(socket, None)
                self.failures += 1
                event.update(decodeStatus='unsupported_or_misaligned', reason=str(exc))
        else:
            # Outgoing sequences/ciphertext and minimap layouts are not guessed.
            self.contexts.pop(socket, None)
            event.update(decodeStatus='opaque', reason='Outgoing transformation or minimap schema unverified')
        return event


def capture(frida, device, seconds, destination, check_only=False, connection_factory=CaptureConnection):
    decoder = Decoder()
    inbox, overflow = queue.Queue(maxsize=256), threading.Event()
    started = time.monotonic()
    connection = None
    ready = False
    status, reason = 'incomplete', 'No agent readiness event'
    cleanup, cleanup_reason = 'not-needed', None
    written = 0
    stats = {'socketBytes': 0, 'framedMessages': 0}
    destination = Path(destination)
    with (destination / 'messages.jsonl').open('x', encoding='utf-8') as output:
        def emit(event):
            nonlocal written
            event = {'observedAt': datetime.now(timezone.utc).isoformat(), **event}
            line = json.dumps(event, ensure_ascii=True) + '\n'
            size = len(line.encode('utf-8'))
            if written + size > MAX_LOG_BYTES:
                raise RuntimeError('64 MiB output limit reached')
            output.write(line)
            output.flush()
            written += size
        try:
            emit({'type': 'run_start', 'scannerVersion': 7, 'mode': 'socket-messages',
                  'coverage': 'observed-messages-only', 'wholeKingdomComplete': False})
            connection = connection_factory(frida, device, agent_source(), inbox, overflow)
            print('Attached to PID {}. Waiting for socket hooks.'.format(connection.pid), flush=True)
            deadline = time.monotonic() + 15
            heartbeat = time.monotonic()
            while time.monotonic() < deadline:
                if overflow.is_set():
                    raise RuntimeError('Host queue overflow; capture is incomplete')
                try:
                    raw = inbox.get(timeout=min(.25, max(.001, deadline-time.monotonic())))
                except queue.Empty:
                    if ready and time.monotonic() - heartbeat > 5:
                        raise RuntimeError('Agent heartbeat lost')
                    continue
                kind = raw.get('type')
                if kind == 'heartbeat':
                    heartbeat = time.monotonic()
                    stats = {key: raw[key] for key in stats}
                    continue
                event = decoder.process(raw)
                emit(event)
                if kind == 'ready':
                    ready = True
                    heartbeat = time.monotonic()
                    deadline = heartbeat + seconds
                    print('Socket hooks ready. Open the kingdom map and move manually to a few known locations.', flush=True)
                    if check_only:
                        status, reason = 'hooks_ready', 'Hook attachment only; traffic not validated'
                        break
                elif kind in ('agent_error', 'detached'):
                    raise RuntimeError(raw.get('reason', kind))
                elif kind == 'map_frame':
                    print('{} opcode {}: {}'.format(event['direction'], event['opcode'], event['decodeStatus']), flush=True)
            else:
                if ready:
                    if decoder.decoded:
                        status, reason = 'capture_complete', 'Timed observation finished; kingdom coverage unverified'
                    else:
                        status, reason = 'incomplete', 'No decodable map responses; inspect messages.jsonl and reopen the map during capture'
        except KeyboardInterrupt:
            status, reason = 'interrupted', 'Ctrl+C; flushed observations retained'
        except Exception as exc:
            status, reason = 'incomplete', str(exc)
        finally:
            if connection is not None:
                try:
                    connection.stop()
                    stop_deadline = time.monotonic() + 3
                    stopped = False
                    while time.monotonic() < stop_deadline:
                        try:
                            raw = inbox.get(timeout=.1)
                        except queue.Empty:
                            continue
                        if raw.get('type') in ('heartbeat', 'capture_stopped'):
                            stats = {key: raw[key] for key in stats}
                            if raw['type'] == 'capture_stopped':
                                stopped = True
                                break
                        else:
                            emit(decoder.process(raw))
                            if raw.get('type') in ('agent_error', 'detached'):
                                status, reason = 'incomplete', raw.get('reason', raw['type'])
                    if not stopped:
                        status, reason = 'incomplete', 'Agent stop acknowledgement missing'
                except (Exception, KeyboardInterrupt) as exc:
                    status, reason = 'incomplete', 'Could not drain capture: ' + str(exc)
                try:
                    close_connection(connection)
                    cleanup = 'complete'
                except CleanupIncomplete as exc:
                    cleanup, cleanup_reason = 'incomplete', str(exc)
                    status = 'incomplete'
            # A tail arriving during teardown cannot be silently counted as validated.
            pending = inbox.qsize()
            if overflow.is_set() or (decoder.gaps and status == 'capture_complete'):
                status = 'incomplete'
                reason = 'Capture gaps occurred; only retained messages are usable'
            if pending and status == 'capture_complete':
                status, reason = 'incomplete', 'Messages pending at stop boundary; retained observations only'
    summary = dict(scannerVersion=7, status=status, reason=reason, mode='socket-messages',
                   coverage='observed-messages-only', wholeKingdomComplete=False,
                   mapFrames=decoder.frames, decodedMapMessages=decoder.decoded,
                   undecodedMapMessages=decoder.failures, observedPointRecords=decoder.points,
                   captureGaps=decoder.gaps, rejectedStreams=decoder.rejected, ready=ready, cleanupStatus=cleanup,
                   cleanupReason=cleanup_reason, pendingEventsAtStop=pending,
                   elapsedSeconds=round(time.monotonic()-started, 2), **stats,
                   runDirectory=str(destination.resolve()))
    (destination / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if status in ('capture_complete', 'hooks_ready') else 2
