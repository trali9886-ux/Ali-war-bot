import copy
import io
import json
from pathlib import Path
import queue
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from contextlib import redirect_stdout
from quality import normalize, Comparer
import collect


def payload(index=3, might='0', name='Example'):
    return {'status':'cache-readable', 'cachedKingdom':1364, 'tableCapacities':{'layout':262144},
            'records':[{'layoutIndex':index, 'tableID':4, 'playerName':name, 'guildTag':'', 'guildName':'',
                        'rawLevel':30, 'coordinates':{'kingdom':1364,'x':6,'y':0},
                        'might':might, 'troopsKilled':'0'}]}


class QualityTests(unittest.TestCase):
    def test_unknown_zero_and_raw_preserved(self):
        raw=payload(); out=normalize(raw); r=out['records'][0]
        self.assertIsNone(r['might']); self.assertEqual(r['mightRaw'],'0')
        self.assertIsNone(r['guildName']); self.assertEqual(raw['records'][0]['might'],'0')
        self.assertEqual(r['freshness'],'unknown'); self.assertIsNone(r['stablePlayerId'])

    def test_precision_and_invalid_numbers(self):
        n='18446744073709551615'
        self.assertEqual(normalize(payload(might=n))['records'][0]['might'],n)
        for value in ('-1','1.5','18446744073709551616', '1'*100, 12):
            with self.subTest(value=value), self.assertRaises(ValueError): normalize(payload(might=value))

    def test_duplicates_are_locations_not_slot_identity(self):
        raw=payload(); second=copy.deepcopy(raw['records'][0]);second['layoutIndex']=4;raw['records'].append(second)
        self.assertEqual(len(normalize(raw)['records']),2)
        raw['records'][1]['layoutIndex']=3
        with self.assertRaises(ValueError): normalize(raw)

    def test_cache_changes_never_claim_teleport_or_identity(self):
        c=Comparer();self.assertEqual(c.compare(normalize(payload()),1)[0]['type'],'baseline')
        change=c.compare(normalize(payload(might='123')),1)
        self.assertEqual(change[0]['type'],'cache_fields_changed')
        change=c.compare(normalize(payload(index=7)),1)
        self.assertEqual({x['type'] for x in change},{'cache_entry_not_observed','cache_entry_observed'})
        self.assertEqual(c.compare(normalize(payload(index=7)),2)[0]['type'],'baseline')
        c.reset();self.assertEqual(c.compare(normalize(payload()),2)[0]['type'],'baseline')

    def test_slot_change_alone_is_not_entity_change(self):
        c=Comparer();a=normalize(payload());c.compare(a,1)
        b=copy.deepcopy(a);b['records'][0]['tableID']=400
        self.assertEqual(c.compare(b,1),[])

    def test_kingdom_change_resets_baseline(self):
        c=Comparer();c.compare(normalize(payload()),1)
        raw=payload();raw['cachedKingdom']=1365
        self.assertEqual(c.compare(normalize(raw),1)[0]['type'],'baseline')


class LifecycleTests(unittest.TestCase):
    def trial(self, batches, close_error=None):
        made=[]
        def factory(_f,_d,_s,inbox,_overflow):
            obj=Mock();obj.pid=123+len(made);made.append(obj)
            if close_error is not None: obj.close.side_effect=close_error
            for event in batches[min(len(made)-1,len(batches)-1)]:inbox.put_nowait(event)
            return obj
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            code=collect.collect(None,'emulator-5554',0.02,1,Path(tmp),factory)
            rows=[json.loads(x) for x in (Path(tmp)/'observations.jsonl').read_text().splitlines()]
            summary=json.loads((Path(tmp)/'summary.json').read_text())
        return code,rows,summary,made

    def test_journal_and_cleanup(self):
        code,rows,summary,made=self.trial([[{'type':'snapshot','payload':payload(),'agentReadMs':4}]])
        self.assertEqual(code,0);self.assertEqual(summary['snapshots'],1)
        snapshot=next(r for r in rows if r['type']=='snapshot')
        self.assertIn('observedAt',snapshot);self.assertEqual(snapshot['agentReadMs'],4)
        self.assertIsNone(snapshot['snapshot']['records'][0]['might'])
        made[0].close.assert_called_once()

    def test_failed_snapshot_breaks_comparison(self):
        code,rows,summary,_=self.trial([[{'type':'snapshot','payload':payload()},
            {'type':'snapshot','payload':{'status':'not-confirmed','reason':'changed'}},
            {'type':'snapshot','payload':payload(index=7)}]])
        snapshots=[r for r in rows if r['type']=='snapshot']
        self.assertEqual(code,2);self.assertEqual(summary['errors'],1)
        self.assertEqual(snapshots[-1]['cacheChanges'][0]['type'],'baseline')

    def test_detachment_reattaches_without_cross_session_diff(self):
        code,rows,summary,made=self.trial([
            [{'type':'snapshot','payload':payload()},{'type':'detached','reason':'process-terminated'}],
            [{'type':'snapshot','payload':payload(index=9)}]])
        self.assertEqual(code,2);self.assertEqual(summary['attachments'],2)
        snapshots=[r for r in rows if r['type']=='snapshot']
        self.assertEqual([r['epoch'] for r in snapshots],[1,2])
        self.assertEqual(snapshots[-1]['cacheChanges'][0]['type'],'baseline')
        for obj in made: obj.close.assert_called_once()

    def test_rejected_snapshot_diagnostics_are_journaled(self):
        diagnostic = {'consistencyChanges':[{'field':'header.zoneCount','before':'2','after':'4'}]}
        _,rows,_,_=self.trial([[{'type':'snapshot','payload':payload()},
            {'type':'snapshot','agentReadMs':42000,'payload':{'status':'not-confirmed',
             'reason':'Map changed','stage':'snapshot consistency','diagnostics':diagnostic}}]])
        row=next(r for r in rows if r['type']=='snapshot_unavailable')
        self.assertEqual(row['agentReadMs'],42000)
        self.assertEqual(row['diagnostics'],diagnostic)

    def test_cleanup_failure_preserves_summary(self):
        code,rows,summary,made=self.trial([[{'type':'snapshot','payload':payload()}]], RuntimeError('detach failed'))
        self.assertEqual(code,2)
        self.assertEqual(summary['cleanupStatus'],'incomplete')
        self.assertIn('detach failed',summary['cleanupReason'])
        self.assertEqual(rows[-1]['type'],'run_end')
        made[0].close.assert_called_once()

    def test_cleanup_timeout_preserves_summary(self):
        release=threading.Event()
        original=collect.close_connection
        try:
            with patch.object(collect,'close_connection',side_effect=lambda c:original(c,timeout=0.01)):
                code,rows,summary,_=self.trial([[{'type':'snapshot','payload':payload()}]], lambda:release.wait(2))
            self.assertEqual(code,2)
            self.assertEqual(summary['cleanupStatus'],'incomplete')
            self.assertIn('exceeded',summary['cleanupReason'])
            self.assertEqual(rows[-1]['type'],'run_end')
        finally:
            release.set()

    def test_cleanup_failure_stops_reattachment(self):
        code,rows,summary,made=self.trial([[{'type':'detached','reason':'test'}]], RuntimeError('detach failed'))
        self.assertEqual(code,2)
        self.assertEqual(len(made),1)
        self.assertEqual(summary['cleanupStatus'],'incomplete')
        made[0].close.assert_called_once()

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'observations.jsonl';p.write_text('existing')
            with self.assertRaises(FileExistsError):collect.collect(None,'x',0.01,1,Path(tmp))
            self.assertEqual(p.read_text(),'existing')

    def test_native_attach_and_failed_load_cleanup(self):
        frida=Mock();dev=frida.get_device.return_value
        app=Mock(identifier=collect.PACKAGE,pid=77);dev.enumerate_applications.return_value=[app]
        session=dev.attach.return_value;script=session.create_script.return_value
        script.load.side_effect=RuntimeError('load failed')
        with self.assertRaises(RuntimeError):collect.Connection(frida,'emulator-5554','source',queue.Queue(8),threading.Event())
        dev.attach.assert_called_once_with(77,realm='native')
        script.unload.assert_called_once();session.detach.assert_called_once()

    def test_terminated_process_needs_no_remote_cleanup(self):
        frida=Mock();dev=frida.get_device.return_value
        dev.enumerate_applications.return_value=[Mock(identifier=collect.PACKAGE,pid=77)]
        session=dev.attach.return_value;script=session.create_script.return_value
        connection=collect.Connection(frida,'test','source',queue.Queue(8),threading.Event())
        connection.detached('process-terminated')
        collect.close_connection(connection)
        script.unload.assert_not_called();session.detach.assert_not_called()
        self.assertIsNone(connection.session)

    def test_log_size_limit_closes_session(self):
        raw=payload();raw['scope']='x'*10000
        with patch.object(collect, 'MAX_OUTPUT_BYTES', 10000):
            code,rows,summary,made=self.trial([[{'type':'snapshot','payload':raw}]])
        self.assertEqual(code,2);self.assertEqual(summary['snapshots'],0)
        self.assertEqual(rows[-1]['type'],'run_end');made[0].close.assert_called_once()

    def test_overflow_is_signalled(self):
        c=collect.Connection.__new__(collect.Connection);c.closed=False;c.inbox=queue.Queue(1);c.overflow=threading.Event()
        c.enqueue({'a':1});c.enqueue({'a':2});self.assertTrue(c.overflow.is_set())


class CleanupTests(unittest.TestCase):
    def test_stalled_cleanup_is_bounded(self):
        release = threading.Event()
        connection = Mock()
        connection.close.side_effect=lambda:release.wait(2)
        try:
            with self.assertRaisesRegex(collect.CleanupIncomplete,'exceeded'):
                collect.close_connection(connection,timeout=0.01)
        finally:
            release.set()

    def test_interruption_inside_cleanup_is_reported(self):
        connection=Mock()
        connection.close.side_effect=KeyboardInterrupt()
        with self.assertRaisesRegex(collect.CleanupIncomplete,'KeyboardInterrupt'):
            collect.close_connection(connection)

    def test_ctrl_c_while_waiting_is_reported(self):
        real_event = threading.Event
        done = real_event()
        release = real_event()
        connection = Mock()
        connection.close.side_effect=lambda:release.wait(2)
        # Only interrupt the host's cleanup wait; Thread.start uses a separate Event.
        with patch.object(done,'wait',side_effect=KeyboardInterrupt()), \
             patch.object(collect.threading,'Event',side_effect=[done,real_event()]):
            try:
                with self.assertRaisesRegex(collect.CleanupIncomplete,'wait interrupted'):
                    collect.close_connection(connection)
            finally:
                release.set()


class StartupTimingTests(unittest.TestCase):
    def run_clock(self, delays, batches, startup_timeout=120):
        clock = [100.0]
        made = []
        attempts = []
        class TimedQueue(queue.Queue):
            def get(self, block=True, timeout=None):
                try:
                    return super().get(block=False)
                except queue.Empty:
                    clock[0] += timeout or 0
                    raise
        def factory(_f, _d, _s, inbox, _overflow):
            index = len(attempts)
            attempts.append(index)
            clock[0] += delays[min(index, len(delays)-1)]
            batch = batches[min(index, len(batches)-1)]
            if isinstance(batch, Exception):
                raise batch
            obj = Mock(pid=42)
            made.append(obj)
            for event in batch:
                inbox.put_nowait(event)
            return obj
        def sleep(seconds):
            clock[0] += seconds
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()), \
                patch.object(collect.time, 'monotonic', side_effect=lambda: clock[0]), \
                patch.object(collect.time, 'sleep', side_effect=sleep), \
                patch.object(collect.queue, 'Queue', TimedQueue):
            code = collect.collect(None, 'test', 60, 30, Path(tmp), factory,
                                   startup_timeout=startup_timeout)
            rows = [json.loads(line) for line in (Path(tmp)/'observations.jsonl').read_text().splitlines()]
            summary = json.loads((Path(tmp)/'summary.json').read_text())
        for obj in made:
            obj.close.assert_called_once()
        return code, rows, summary

    def test_slow_attach_keeps_full_recording_window(self):
        code, rows, summary = self.run_clock([70], [[{'type':'ready'}, {'type':'snapshot','payload':payload()}]])
        self.assertEqual(code, 0)
        self.assertEqual(summary['snapshots'], 1)
        self.assertEqual(summary['startupSeconds'], 70)
        self.assertEqual(summary['recordingSeconds'], 60)
        self.assertEqual(summary['elapsedSeconds'], 130)
        self.assertEqual(next(r for r in rows if r['type']=='attached')['connectionSeconds'],70)

    def test_initial_timeout_retry_does_not_consume_recording(self):
        code, rows, summary = self.run_clock([60, 8], [RuntimeError('timeout'), [{'type':'snapshot','payload':payload()}]])
        self.assertEqual(code, 2)  # The recovered error remains visible.
        self.assertEqual(summary['snapshots'], 1)
        self.assertEqual(summary['errors'], 1)
        self.assertEqual(summary['recordingSeconds'], 60)
        self.assertEqual(summary['startupSeconds'], 70)

    def test_ready_without_snapshot_has_bounded_startup(self):
        code, rows, summary = self.run_clock([1], [[{'type':'ready'}]], startup_timeout=10)
        self.assertEqual(code, 2)
        self.assertEqual(summary['snapshots'], 0)
        self.assertEqual(summary['recordingSeconds'], 0)
        self.assertEqual(summary['elapsedSeconds'], 10)
        self.assertEqual(rows[-2]['type'], 'startup_timeout')

    def test_attach_returning_after_deadline_cannot_start_recording(self):
        code, rows, summary = self.run_clock([15], [[{'type':'snapshot','payload':payload()}]], startup_timeout=10)
        self.assertEqual(code, 2)
        self.assertEqual(summary['snapshots'], 0)
        self.assertFalse(any(r['type']=='recording_start' for r in rows))

    def test_reconnect_does_not_restart_recording_window(self):
        code, rows, summary = self.run_clock([3, 20], [
            [{'type':'snapshot','payload':payload()}, {'type':'detached','reason':'test'}],
            [{'type':'snapshot','payload':payload(index=9)}]])
        self.assertEqual(code, 2)
        self.assertEqual(summary['attachments'], 2)
        self.assertEqual(summary['recordingSeconds'], 60)
        self.assertEqual(summary['elapsedSeconds'], 63)
        self.assertEqual(sum(r['type']=='recording_start' for r in rows), 1)


if __name__ == '__main__':unittest.main()
