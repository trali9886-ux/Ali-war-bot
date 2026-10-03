import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
from bot import Bot, card, location
from data import Store
from telegram import Telegram, TelegramError
from run import RunLock, save_config

AT='2026-10-01T10:00:00+00:00'
LATER='2026-10-01T10:01:00+00:00'

def event(name='Alice', might='1000000', at=AT, index=2):
    return dict(type='snapshot',observedAt=at,snapshot=dict(cachedKingdom=1364,
        records=[dict(playerName=name,guildTag='ABC',layoutIndex=index,might=might,troopsKilled='100',
                      coordinates=dict(kingdom=1364,x=4,y=0))]))


def packet(name='Bob', home=42, socket=1):
    return dict(type='map_frame',observedAt=AT,direction='incoming',opcode=2220,
        decodeStatus='parsed_candidate',socket=socket,decoded=dict(complete_parse=True,events=[
        dict(type='bulk_baseline',points=[dict(player_name=name,alliance_tag='XYZ',point_kind_raw=8,
            zone=2,point=3,kingdom_id=home,castle_level=25)])]))


class FakeAPI:
    def __init__(self):self.calls=[]
    def call(self, method, **payload):
        self.calls.append((method,payload))
        return {'message_id':1}


class Base(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.store=Store(self.root/'test.sqlite3')
    def tearDown(self): self.store.db.close();self.temp.cleanup()
    def add(self, e=None, source='synthetic'):
        with self.store.db:self.store.import_event(e or event(),source)
        return self.store.search()[0][0]


class ImportTests(Base):
    def test_cache_uint64_unknown_and_older_data(self):
        identifier=self.add(event(might=str(2**64-1)))
        self.assertEqual(self.store.get(identifier)['might'],2**64-1)
        self.add(event(might='7',at='2026-09-01T00:00:00Z'))
        self.assertEqual(self.store.get(identifier)['might'],2**64-1)
        self.add(event(might='0',at=LATER));self.assertIsNone(self.store.get(identifier)['might'])

    def test_packet_home_kingdom_is_not_map_location(self):
        identifier=self.add(packet())
        data=self.store.get(identifier)
        self.assertIsNone(data['kingdom']);self.assertIsNone(data['location'])
        self.assertEqual(data['home_kingdom'],42);self.assertIsNone(data['might'])
        self.assertNotIn('K42',card(data))
        self.assertEqual(data['map_position'],{'zone':2,'point':3})
        self.assertEqual(data['location_quality'],'raw-zone-point-only')
        self.assertEqual(data['coverage_scope'],'observed-point-record')
        self.assertFalse(data['world_state_complete'])
        self.assertIn('Zone 2 · point 3 · world coordinates unverified',card(data))

    def test_packet_location_hint_requires_bounded_integer_zone_and_point(self):
        self.assertEqual(location(dict(map_position={'zone':'2','point':3})),
                         'Location not verified')
        self.assertEqual(location(dict(map_position={'zone':2,'point':True})),
                         'Location not verified')
        self.assertEqual(location(dict(map_position={'zone':65536,'point':3})),
                         'Location not verified')

    def test_sessions_and_duplicate_names_are_separate(self):
        self.add(packet(), 'one');self.add(packet(), 'two');self.add(packet(socket=2),'one')
        self.assertEqual(self.store.stats()[0],3)

    def test_history_follow_alert_and_name_replacement(self):
        identifier=self.add();self.store.follow(10,identifier,True)
        self.add(event(might='2000000',at=LATER))
        self.assertIn('Might:',self.store.history(identifier)[0]['label'])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM alerts').fetchone()[0],1)
        self.add(event(name='Different',might='3',at='2026-10-01T10:02:00Z'))
        self.assertIn('Record at this location changed',self.store.history(identifier)[0]['label'])
        self.assertNotIn('Might:',self.store.history(identifier)[0]['label'])
        self.store.follow(10,identifier,False)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM alerts').fetchone()[0],0)

    def test_tail_and_restart_offsets_and_bad_lines(self):
        run=self.root/'runs'/'capture';run.mkdir(parents=True);p=run/'observations.jsonl'
        p.write_bytes((json.dumps(event())+'\n{bad}\n'+json.dumps(event(might='2000000',at=LATER))).encode())
        self.store.sync(self.root/'runs');self.assertEqual(self.store.stats()[0],1)
        identifier=self.store.search()[0][0];self.assertEqual(self.store.get(identifier)['might'],1000000)
        with p.open('ab') as f:f.write(b'\n')
        self.store.sync(self.root/'runs');self.assertEqual(self.store.get(identifier)['might'],2000000)
        self.store.sync(self.root/'runs');self.assertEqual(len(self.store.history(identifier)),1)
        self.store.db.close();self.store=Store(self.root/'test.sqlite3')
        self.store.sync(self.root/'runs');self.assertEqual(len(self.store.history(identifier)),1)

    def test_file_replaced_and_truncated(self):
        run=self.root/'r';run.mkdir();p=run/'observations.jsonl'
        p.write_text(json.dumps(event())+'\n');self.store.sync(run)
        p.unlink();p.write_text(json.dumps(event(name='New',at=LATER))+'\n');self.store.sync(run)
        self.assertEqual(self.store.get(self.store.search()[0][0])['name'],'New')

    def test_advanced_delta_does_not_assign_wrong_occupant(self):
        self.add(packet())
        delta=packet();delta['decoded']['events']=[dict(type='player_advance',zone=2,point=3,might=99,kills=88)]
        self.add(delta)
        self.assertIsNone(self.store.get(self.store.search()[0][0])['might'])


class FlowTests(Base):
    def setUp(self):
        super().setUp();self.api=FakeAPI();self.bot=Bot(self.store,self.api,'local-pair-code')
        self.identifier=self.add()
    def message(self, text, user=10, chat=10, kind='private'):
        return dict(message=dict(chat=dict(id=chat,type=kind),text=text,from_user=None,**{'from':{'id':user}}))
    def callback(self,data,user=10,chat=10,kind='private'):
        return dict(callback_query=dict(id='synthetic-query',data=data,**{'from':{'id':user}},
            message=dict(message_id=5,chat=dict(id=chat,type=kind))))
    def pair(self):self.bot.handle(self.message('/start local-pair-code'))

    def test_pairing_access_control_and_four_buttons(self):
        self.bot.handle(self.message('/menu',user=20,chat=20));self.assertEqual(self.api.calls,[])
        self.pair();self.bot.handle(self.callback('player:'+str(self.identifier)))
        self.assertEqual(self.api.calls[-2][0],'answerCallbackQuery')
        method,payload=self.api.calls[-1];self.assertEqual(method,'editMessageText')
        labels=[b['text'] for row in payload['reply_markup']['inline_keyboard'][:2] for b in row]
        self.assertEqual(labels,['🔔 Track','ℹ️ Info','🛡 Equipment','📊 Activity'])
        rows=payload['reply_markup']['inline_keyboard']
        self.assertEqual([rows[0][0]['style'],rows[0][1]['style'],rows[1][1]['style']],['danger','primary','success'])
        count=len(self.api.calls);self.bot.handle(self.callback('player:1',20,20))
        self.assertEqual(len(self.api.calls),count+1);self.assertEqual(self.api.calls[-1][0],'answerCallbackQuery')

    def test_search_pagination_and_unknown_fields(self):
        self.pair()
        for i in range(6): self.add(event(name='Alice'+str(i),index=i+3))
        self.bot.handle(self.message('alice'))
        self.assertIn('1–5 of 7',self.api.calls[-1][1]['text'])
        self.bot.handle(self.callback('list:1'));self.assertIn('6–7 of 7',self.api.calls[-1][1]['text'])
        self.bot.handle(self.callback('gear:'+str(self.identifier)))
        self.assertIn('No equipment',self.api.calls[-1][1]['text'])

    def test_tracking_is_idempotent_and_alerts_persist(self):
        self.pair()
        for _ in range(2):self.bot.handle(self.callback('track:{}:1'.format(self.identifier)))
        self.assertEqual(len(self.store.following(10)),1)
        self.add(event(might='2000000',at=LATER));self.bot.alerts()
        self.assertIn('Update',self.api.calls[-1][1]['text'])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM alerts').fetchone()[0],0)

    def test_groups_require_owner_opt_in(self):
        self.pair();before=len(self.api.calls)
        self.bot.handle(self.message('/allowgroup',20,-10,'group'));self.assertEqual(len(self.api.calls),before)
        self.bot.handle(self.message('/allowgroup',10,-10,'group'))
        self.bot.handle(self.callback('player:1',20,-10,'group'))
        self.assertEqual(self.api.calls[-1][0],'editMessageText')
        self.bot.handle(self.callback('search',20,-10,'group'))
        self.assertEqual(self.api.calls[-1][0],'sendMessage')
        self.assertTrue(self.api.calls[-1][1]['reply_markup']['force_reply'])
        self.bot.handle(self.message('/removegroup',10,-10,'group'));self.assertEqual(self.store.setting('groups'),[])

    def test_escaped_card_and_no_fake_shield_status(self):
        identifier=self.add(event(name='<b>&Alice',index=7))
        self.pair();self.bot.handle(self.callback('info:'+str(identifier)))
        value=self.api.calls[-1][1]['text']
        self.assertIn('&lt;b&gt;&amp;Alice',value);self.assertIn('Shield: unavailable',value)
        self.assertNotIn('Shield: down',value)
        self.assertIn('✊ Might',value);self.assertIn('⚔️ Kills',value)

    def test_rate_limit_keeps_alert_for_retry(self):
        self.pair();self.store.follow(10,self.identifier,True);self.add(event(might='2',at=LATER))
        with patch.object(self.api,'call',side_effect=TelegramError(429,9)):
            with self.assertRaises(TelegramError):self.bot.alerts()
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM alerts').fetchone()[0],1)


class TransportTests(unittest.TestCase):
    def test_json_contract_and_token_not_in_error(self):
        api=Telegram('test-fixture','http://127.0.0.1:9999')
        response=io.BytesIO(b'{"ok":true,"result":{"message_id":1}}')
        with patch.object(api.opener,'open',return_value=response) as call:
            self.assertEqual(api.call('sendMessage',chat_id=10,text='hello')['message_id'],1)
            req=call.call_args.args[0]
            self.assertEqual(json.loads(req.data)['text'],'hello')
        error=urllib.error.HTTPError(api.url,429,'private error',{},io.BytesIO(b'{"parameters":{"retry_after":7}}'))
        with patch.object(api.opener,'open',side_effect=error):
            with self.assertRaises(TelegramError) as caught:api.call('getMe')
            self.assertEqual(caught.exception.retry_after,7)
            self.assertNotIn('test-fixture',str(caught.exception))

    def test_no_real_key_to_local_and_no_remote_override(self):
        with self.assertRaises(ValueError):Telegram('123:real-looking-token','http://127.0.0.1:9999')
        with self.assertRaises(ValueError):Telegram('test-fixture','https://example.com')

    def test_config_atomic_and_single_instance_lock(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            save_config(p/'config.json',{'token':'synthetic-fixture'})
            self.assertFalse((p/'config.tmp').exists())
            with RunLock(p/'bot.lock'):
                with self.assertRaises(RuntimeError):
                    with RunLock(p/'bot.lock'):pass


class RunnerTests(unittest.TestCase):
    def test_start_poll_process_and_persist_offset(self):
        import run
        with tempfile.TemporaryDirectory() as td:
            state=Path(td)/'telegram';state.mkdir()
            s=Store(state/'tracker.sqlite3');s.set_setting('owner',10);s.db.close()
            class API(FakeAPI):
                polls=0
                def call(self,method,**payload):
                    super().call(method,**payload)
                    if method=='getMe':return {'id':123,'username':'synthetic_bot'}
                    if method=='getWebhookInfo':return {'url':''}
                    if method=='getUpdates':
                        self.polls+=1
                        if self.polls>1:raise KeyboardInterrupt
                        return [{'update_id':7,'message':{'chat':{'id':10,'type':'private'},'from':{'id':10},'text':'/menu'}}]
                    return {'message_id':1}
            api=API()
            with patch.object(run,'Telegram',return_value=api),patch.dict('os.environ',{'TELEGRAM_BOT_TOKEN':'123:'+'x'*25}),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run.main(['--runs',td]),0)
            s=Store(state/'tracker.sqlite3')
            self.assertEqual(s.setting('telegram_offset'),8);s.db.close()
            self.assertTrue(any(method=='sendMessage' for method,_ in api.calls))

if __name__=='__main__':unittest.main()
