"""Read local game cache snapshots into JSONL using one native Frida session."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import sys
import tempfile
import threading
import time
from quality import normalize, Comparer

PACKAGE = 'com.igg.android.lordsmobile'
MAX_OUTPUT_BYTES = 64 * 1024 * 1024


class OutputLimit(Exception):
    pass


class CleanupIncomplete(Exception):
    pass


def close_connection(connection, timeout=3):
    """Bound host waiting; a stalled Frida call may still be pending on a daemon thread."""
    done = threading.Event()
    errors = []
    def worker():
        try:
            connection.close()
        except BaseException as exc:
            errors.append(str(exc) or type(exc).__name__)
        finally:
            done.set()
    threading.Thread(target=worker, daemon=True, name='frida-cleanup').start()
    try:
        finished = done.wait(timeout)
    except KeyboardInterrupt:
        raise CleanupIncomplete('Cleanup wait interrupted; device cleanup is unconfirmed') from None
    if not finished:
        raise CleanupIncomplete('Cleanup exceeded {} seconds; device cleanup is unconfirmed'.format(timeout))
    if errors:
        raise CleanupIncomplete('; '.join(errors))


def utc():
    return datetime.now(timezone.utc).isoformat()


class Connection:
    def __init__(self, frida, device_id, source, inbox, overflow):
        self.session = self.script = None
        self.closed = False
        self.detach_reason = None
        self.pid = None
        self.inbox, self.overflow = inbox, overflow
        try:
            device = frida.get_device(device_id, timeout=5)
            apps = [a for a in device.enumerate_applications() if a.identifier == PACKAGE and a.pid]
            if len(apps) != 1:
                raise RuntimeError('Open Lords Mobile normally; expected one running game process')
            self.pid = apps[0].pid
            self.session = device.attach(self.pid, realm='native')
            self.session.on('detached', self.detached)
            self.script = self.session.create_script(source)
            self.script.on('message', self.message)
            self.script.load()
        except (Exception, KeyboardInterrupt):
            close_connection(self)
            raise

    def enqueue(self, item):
        if self.closed:
            return
        try:
            self.inbox.put_nowait(item)
        except queue.Full:
            self.overflow.set()

    def message(self, message, _data):
        if message.get('type') == 'send':
            self.enqueue(message['payload'])
        else:
            self.enqueue({'type': 'agent_error', 'reason': message.get('description', 'Agent error')})

    def detached(self, reason, *_):
        self.detach_reason = str(reason)
        self.enqueue({'type': 'detached', 'reason': str(reason)})

    def close(self):
        self.closed = True
        if self.detach_reason in ('process-terminated', 'process-replaced', 'application-requested'):
            self.script = self.session = None
            return
        errors = []
        for obj, method in ((self.script, 'unload'), (self.session, 'detach')):
            if obj is not None:
                try:
                    getattr(obj, method)()
                except Exception as exc:
                    errors.append('{}: {}'.format(method, exc))
        self.script = self.session = None
        if errors:
            raise CleanupIncomplete('; '.join(errors))


def collect(frida, device_id, seconds, interval, destination, connection_factory=Connection, startup_timeout=120):
    comparer = Comparer()
    counts = {'snapshots': 0, 'errors': 0, 'attachments': 0}
    started = time.monotonic()
    deadline = started + startup_timeout
    recording_started = None
    source = 'const COLLECTOR_OPTIONS = ' + json.dumps({'intervalMs': int(interval * 1000)}) + ';\n'
    source += Path(__file__).with_name('agent.js').read_text(encoding='utf-8')
    connection = None
    epoch = 0
    inbox = queue.Queue(maxsize=8)
    overflow = threading.Event()
    last_message = started
    interrupted = False
    cleanup_status = 'not-needed'
    cleanup_reason = None
    def close_current():
        nonlocal connection, cleanup_status, cleanup_reason
        current, connection = connection, None
        if current is None:
            return
        try:
            close_connection(current)
            cleanup_status = 'complete'
        except CleanupIncomplete as exc:
            cleanup_status, cleanup_reason = 'incomplete', str(exc)
            raise
    # Exclusive creation, flush each event; every run receives a separate directory.
    with (destination / 'observations.jsonl').open('x', encoding='utf-8') as output:
        written = 0
        def emit(kind, **values):
            nonlocal written
            line = json.dumps({'type': kind, 'observedAt': utc(), 'elapsedSeconds': round(time.monotonic()-started, 3), **values}, ensure_ascii=True) + '\n'
            limit = MAX_OUTPUT_BYTES if kind == 'run_end' else MAX_OUTPUT_BYTES - 4096
            if written + len(line.encode('utf-8')) > limit:
                raise OutputLimit('64 MiB log limit reached')
            output.write(line)
            written += len(line.encode('utf-8'))
            output.flush()

        emit('run_start', schemaVersion=2, collectorVersion=3, device=device_id, durationSeconds=seconds,
             startupTimeoutSeconds=startup_timeout, timerStarts='first-valid-snapshot',
             intervalSeconds=interval, dataFreshness='unknown', classification='kind-8-unverified')
        try:
            while time.monotonic() < deadline:
                if connection is None:
                    inbox = queue.Queue(maxsize=8)
                    overflow = threading.Event()
                    try:
                        attempt_started = time.monotonic()
                        emit('connection_attempt', epoch=epoch+1)
                        connection = connection_factory(frida, device_id, source, inbox, overflow)
                        epoch += 1
                        counts['attachments'] += 1
                        comparer.reset()
                        last_message = time.monotonic()
                        emit('attached', epoch=epoch, pid=connection.pid,
                             connectionSeconds=round(time.monotonic()-attempt_started, 3))
                        print('Attached to PID {}. Waiting for a valid cache snapshot.'.format(connection.pid), flush=True)
                    except CleanupIncomplete:
                        raise
                    except Exception as exc:
                        counts['errors'] += 1
                        comparer.reset()
                        emit('connection_error', reason=str(exc))
                        print('Waiting for game/Frida: {}'.format(exc), flush=True)
                        time.sleep(max(0, min(2, deadline - time.monotonic())))
                        continue
                if time.monotonic() >= deadline:
                    break
                if overflow.is_set():
                    counts['errors'] += 1
                    emit('observation_gap', reason='Host queue overflow; restarting observation baseline', epoch=epoch)
                    close_current()
                    connection = None
                    comparer.reset()
                    continue
                try:
                    event = inbox.get(timeout=max(0.001, min(0.5, deadline-time.monotonic())))
                except queue.Empty:
                    if recording_started is not None and time.monotonic()-last_message > max(15, interval*3):
                        counts['errors'] += 1
                        emit('observation_gap', reason='Agent stopped responding', epoch=epoch)
                        close_current()
                        connection = None
                        comparer.reset()
                    continue
                last_message = time.monotonic()
                kind = event.get('type')
                if kind == 'ready':
                    emit('agent_ready', epoch=epoch, version=event.get('version'))
                elif kind in ('detached', 'agent_error'):
                    counts['errors'] += 1
                    emit('observation_gap', epoch=epoch, reason=event.get('reason'))
                    close_current()
                    connection = None
                    comparer.reset()
                elif kind == 'snapshot':
                    raw = event.get('payload', {})
                    try:
                        snapshot = normalize(raw)
                    except (ValueError, TypeError, KeyError) as exc:
                        counts['errors'] += 1
                        comparer.reset()
                        emit('snapshot_unavailable', epoch=epoch, reason=raw.get('reason', str(exc)),
                             stage=raw.get('stage'), agentReadMs=event.get('agentReadMs'),
                             diagnostics=raw.get('diagnostics'))
                        print('Snapshot unavailable ({} ms): {}'.format(event.get('agentReadMs'), raw.get('reason', exc)), flush=True)
                        continue
                    if recording_started is None:
                        recording_started = time.monotonic()
                        deadline = recording_started + seconds
                        emit('recording_start', durationSeconds=seconds, epoch=epoch)
                        print('First valid snapshot received. Recording for {} seconds.'.format(seconds), flush=True)
                    changes = comparer.compare(snapshot, epoch)
                    emit('snapshot', epoch=epoch, pid=connection.pid, agentReadMs=event.get('agentReadMs'),
                         snapshot=snapshot, cacheChanges=changes)
                    counts['snapshots'] += 1
                    print('Snapshot {}: {} cached entries; {} cache changes; read {} ms'.format(
                        counts['snapshots'], len(snapshot['records']), len(changes), event.get('agentReadMs')), flush=True)
                else:
                    counts['errors'] += 1
                    comparer.reset()
                    emit('observation_gap', epoch=epoch, reason='Unexpected agent event')
            if recording_started is None:
                counts['errors'] += 1
                emit('startup_timeout', reason='No valid snapshot within startup allowance')
                print('Startup allowance expired without a valid snapshot. Send observations.jsonl.', flush=True)
        except CleanupIncomplete as exc:
            counts['errors'] += 1
            cleanup_status, cleanup_reason = 'incomplete', str(exc)
            print('Cleanup incomplete; stopping without reattachment: {}'.format(exc), flush=True)
        except OutputLimit:
            counts['errors'] += 1
            print('Log size limit reached; stopping.', flush=True)
        except KeyboardInterrupt:
            interrupted = True
        finally:
            if connection is not None:
                try:
                    close_current()
                except CleanupIncomplete as exc:
                    counts['errors'] += 1
                    print('Cleanup incomplete: {}'.format(exc), flush=True)
        status = 'interrupted' if interrupted else ('complete' if counts['snapshots'] and not counts['errors'] else 'incomplete')
        summary = {'status': status, **counts, 'elapsedSeconds': round(time.monotonic()-started, 2),
                   'recordingSeconds': round(time.monotonic()-recording_started, 2) if recording_started is not None else 0,
                   'startupSeconds': round((recording_started if recording_started is not None else time.monotonic())-started, 2),
                   'collectorVersion': 3, 'cleanupStatus': cleanup_status, 'cleanupReason': cleanup_reason,
                   'dataFreshness': 'unknown', 'file': str(destination/'observations.jsonl')}
        emit('run_end', **summary)
    (destination/'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if status == 'complete' else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='emulator-5554')
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--interval', type=float, default=2)
    parser.add_argument('--startup-timeout', type=int, default=120)
    parser.add_argument('--output-dir', type=Path, default=Path('runs'))
    args = parser.parse_args(argv)
    if not 5 <= args.seconds <= 3600 or not 1 <= args.interval <= 30 or not 10 <= args.startup_timeout <= 300:
        parser.error('seconds must be 5..3600, interval 1..30, startup-timeout 10..300')
    try:
        import frida
        args.output_dir.mkdir(parents=True, exist_ok=True)
        destination = Path(tempfile.mkdtemp(prefix='cache-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-', dir=str(args.output_dir)))
        print('Output directory: {}'.format(destination.resolve()), flush=True)
        return collect(frida, args.device, args.seconds, args.interval, destination, startup_timeout=args.startup_timeout)
    except ImportError:
        print('Run with your existing lm-frida virtual environment, which already contains Frida.', file=sys.stderr)
        return 2
    except Exception as exc:
        print('Collector failed: {}'.format(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
