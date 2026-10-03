"""Saved observations and follow lists. Never infers online/shield/army status."""
import hashlib
import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

MAX_LINE = 1024 * 1024


def text(value, limit=100):
    return value.strip()[:limit] if isinstance(value, str) else ''


def number(value, maximum=2**64-1):
    if type(value) is int and 0 <= value <= maximum:
        return value
    if isinstance(value, str) and value.isascii() and value.isdecimal() and len(value) <= 20:
        n = int(value)
        return n if n <= maximum else None
    return None


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('Missing observation time')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Observation time needs a timezone')
    return dt.astimezone(timezone.utc).isoformat(timespec='seconds')


class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY, identity TEXT UNIQUE NOT NULL,
          data TEXT NOT NULL, observed TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, player INTEGER NOT NULL REFERENCES players(id),
          observed TEXT NOT NULL, label TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS follows(chat INTEGER NOT NULL, player INTEGER NOT NULL REFERENCES players(id),
          PRIMARY KEY(chat,player));
        CREATE TABLE IF NOT EXISTS alerts(chat INTEGER NOT NULL, player INTEGER NOT NULL REFERENCES players(id),
          label TEXT NOT NULL, observed TEXT NOT NULL, PRIMARY KEY(chat,player));
        CREATE TABLE IF NOT EXISTS imports(path TEXT PRIMARY KEY, generation TEXT NOT NULL, offset INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        ''')
        self.skipped = 0

    def setting(self, key, default=None):
        row = self.db.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_setting(self, key, value):
        self.db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)', (key, json.dumps(value)))
        self.db.commit()

    def get(self, player):
        row = self.db.execute('SELECT * FROM players WHERE id=?', (player,)).fetchone()
        return dict(json.loads(row['data']), id=row['id'], observed=row['observed']) if row else None

    def search(self, query='', chat=None, page=0):
        rows = self.db.execute('SELECT id,data FROM players ORDER BY observed DESC,id DESC').fetchall()
        followed = self.following(chat) if chat is not None else None
        needle = query.casefold().strip()
        found = []
        for row in rows:
            if followed is not None and row['id'] not in followed:
                continue
            data = json.loads(row['data'])
            if needle and needle not in (data['name']+' '+data['guild']).casefold():
                continue
            found.append(row['id'])
        return found[page*5:page*5+5], len(found)

    def following(self, chat):
        return {r[0] for r in self.db.execute('SELECT player FROM follows WHERE chat=?', (chat,))}

    def follow(self, chat, player, enabled):
        with self.db:
            if enabled:
                self.db.execute('INSERT OR IGNORE INTO follows VALUES(?,?)', (chat, player))
            else:
                self.db.execute('DELETE FROM follows WHERE chat=? AND player=?', (chat, player))
                self.db.execute('DELETE FROM alerts WHERE chat=? AND player=?', (chat, player))

    def history(self, player):
        return [dict(r) for r in self.db.execute('SELECT observed,label FROM history WHERE player=? ORDER BY id DESC LIMIT 5', (player,))]

    def save(self, identity, data, at):
        old = self.db.execute('SELECT * FROM players WHERE identity=?', (identity,)).fetchone()
        if old and old['observed'] > at:
            return
        # A changed name at a location is not proof that a player renamed.
        labels = []
        if old:
            previous = json.loads(old['data'])
            if previous['name'] != data['name']:
                labels = ['Record at this location changed: {} → {}'.format(previous['name'], data['name'])]
            else:
                for field, title in [('might','Might'), ('kills','Kills'), ('guild','Guild')]:
                    before, after = previous.get(field), data.get(field)
                    if before is not None and after is not None and before != after:
                        labels.append('{}: {} → {}'.format(title, before, after))
        self.db.execute('INSERT INTO players(identity,data,observed) VALUES(?,?,?) '
                        'ON CONFLICT(identity) DO UPDATE SET data=excluded.data,observed=excluded.observed',
                        (identity, json.dumps(data), at))
        player = self.db.execute('SELECT id FROM players WHERE identity=?', (identity,)).fetchone()[0]
        for label in labels:
            self.db.execute('INSERT INTO history(player,observed,label) VALUES(?,?,?)', (player, at, label))
        if labels:
            self.db.execute('DELETE FROM history WHERE player=? AND id NOT IN '
                            '(SELECT id FROM history WHERE player=? ORDER BY id DESC LIMIT 100)', (player, player))
            for row in self.db.execute('SELECT chat FROM follows WHERE player=?', (player,)).fetchall():
                self.db.execute('INSERT OR REPLACE INTO alerts VALUES(?,?,?,?)', (row[0], player, '\n'.join(labels), at))

    def import_event(self, event, source):
        if not isinstance(event, dict):
            return
        kind = event.get('type')
        if kind not in ('snapshot', 'map_frame'):
            return
        at = timestamp(event.get('observedAt'))
        if kind == 'snapshot':
            snapshot = event.get('snapshot', {})
            if not isinstance(snapshot, dict): return
            kingdom = number(snapshot.get('cachedKingdom'), 65535)
            rows = snapshot.get('records', [])
            if kingdom is None or not isinstance(rows, list) or len(rows)>4096: return
            for row in rows:
                if not isinstance(row, dict): continue
                name = text(row.get('playerName'))
                index = number(row.get('layoutIndex'), 262143)
                if not name or index is None: continue
                c = row.get('coordinates')
                location = None
                if isinstance(c, dict) and c.get('kingdom') == kingdom:
                    x, y = number(c.get('x'), 1023), number(c.get('y'), 1023)
                    if x is not None and y is not None: location = [x, y]
                self.save('cache:{}:{}'.format(kingdom,index), dict(name=name,
                    guild=text(row.get('guildTag'), 30), kingdom=kingdom, location=location,
                    might=number(row.get('might')) or None, kills=number(row.get('troopsKilled')) or None,
                    source='cache', castle_level=None), at)
        elif event.get('direction') == 'incoming' and event.get('opcode') == 2220 and event.get('decodeStatus') == 'parsed_candidate':
            decoded = event.get('decoded')
            socket = number(event.get('socket'), 1000000)
            if socket is None or not isinstance(decoded, dict) or decoded.get('complete_parse') is not True: return
            changes = decoded.get('events', [])
            if not isinstance(changes, list) or len(changes)>4096: return
            for change in changes:
                if not isinstance(change, dict): continue
                if change.get('type') != 'bulk_baseline':
                    # Deltas have location but no stable player ID. Keep raw capture for
                    # later validation rather than attach advanced fields to a wrong occupant.
                    continue
                points = change.get('points', [])
                if not isinstance(points, list) or len(points)>63: continue
                for point in points:
                    if not isinstance(point, dict) or point.get('point_kind_raw') != 8: continue
                    name = text(point.get('player_name'))
                    zone, pos = number(point.get('zone'),65535), number(point.get('point'),255)
                    if not name or zone is None or pos is None: continue
                    self.save('packet:{}:{}:{}:{}'.format(source,socket,zone,pos),dict(
                        name=name, guild=text(point.get('alliance_tag'),30), kingdom=None,
                        location=None, map_position={'zone':zone,'point':pos},
                        location_quality='raw-zone-point-only',
                        identity_scope='capture-socket-zone-point',
                        coverage_scope='observed-point-record', world_state_complete=False,
                        home_kingdom=number(point.get('kingdom_id'),65535),
                        might=None, kills=None, source='packet', castle_level=number(point.get('castle_level'),255)),at)

    def sync(self, root, limit=500):
        """Commit event changes and byte offset together. Incomplete last lines wait."""
        count = 0
        root = Path(root)
        if not root.exists(): return count
        paths = sorted(set(root.rglob('messages.jsonl')) | set(root.rglob('observations.jsonl')),
                       key=lambda p: (p.stat().st_mtime, str(p)))
        for path in paths:
            if count >= limit: break
            stat = path.stat()
            with path.open('rb') as stream:
                first = stream.readline(MAX_LINE+1)
                if not first.endswith(b'\n'): continue
                generation = '{}:{}:{}'.format(stat.st_dev,stat.st_ino,hashlib.sha256(first).hexdigest())
                key = str(path.resolve())
                state = self.db.execute('SELECT generation,offset FROM imports WHERE path=?', (key,)).fetchone()
                offset = state['offset'] if state and state['generation']==generation and state['offset']<=stat.st_size else 0
                stream.seek(offset)
                with self.db:
                    while count < limit:
                        raw = stream.readline(MAX_LINE+1)
                        if not raw: break
                        if len(raw)>MAX_LINE:
                            # A malformed oversized record is skipped through its newline.
                            while raw and not raw.endswith(b'\n'): raw=stream.readline(MAX_LINE+1)
                            self.skipped += 1
                            offset=stream.tell();count+=1;continue
                        if not raw.endswith(b'\n'): break
                        self.db.execute('SAVEPOINT event_import')
                        try:
                            event=json.loads(raw)
                            self.import_event(event,hashlib.sha256((key+generation).encode()).hexdigest()[:20])
                        except (ValueError,TypeError,KeyError,OverflowError):
                            self.db.execute('ROLLBACK TO event_import')
                            self.skipped += 1
                        finally:
                            self.db.execute('RELEASE event_import')
                        offset=stream.tell();count+=1
                    self.db.execute('INSERT OR REPLACE INTO imports VALUES(?,?,?)',(key,generation,offset))
        return count

    def stats(self):
        row=self.db.execute('SELECT count(*),max(observed) FROM players').fetchone()
        return row[0],row[1]
