"""Describe cache observations without inventing server freshness or player identity."""
from copy import deepcopy


def normalize(payload):
    if payload.get('status') != 'cache-readable':
        raise ValueError('snapshot is not readable')
    records = payload.get('records')
    if not isinstance(records, list) or len(records) > 4096:
        raise ValueError('invalid record count')
    result = deepcopy(payload)
    keys = set()
    for row in result['records']:
        index = row['layoutIndex']
        if type(index) is not int or not 0 <= index < payload['tableCapacities']['layout']:
            raise ValueError('invalid layout index')
        key = '{}:{}'.format(payload['cachedKingdom'], index)
        if key in keys:
            raise ValueError('duplicate cache location')
        keys.add(key)
        row['cacheKey'] = key
        row['entityType'] = 'unverified-kind-8'
        row['freshness'] = 'unknown'
        row['stablePlayerId'] = None
        row['fieldQuality'] = {}
        for field in ('might', 'troopsKilled'):
            raw = row[field]
            if not isinstance(raw, str) or not raw.isascii() or not raw.isdecimal() or len(raw) > 20 or int(raw) > 2**64-1:
                raise ValueError('invalid unsigned 64-bit statistic')
            row[field + 'Raw'] = raw
            unknown = int(raw) == 0
            row[field] = None if unknown else raw
            row['fieldQuality'][field] = 'unknown-zero' if unknown else 'cached-value-age-unknown'
        for field in ('playerName', 'guildTag', 'guildName'):
            raw = row[field]
            if raw is not None and not isinstance(raw, str):
                raise ValueError('invalid cached text')
            row[field + 'Raw'] = raw
            row[field] = raw if raw else None
            row['fieldQuality'][field] = 'cached-value-age-unknown' if raw else 'unknown-empty'
        row['fieldQuality']['rawLevel'] = 'meaning-unverified'
        row['fieldQuality']['coordinates'] = 'calibrated-map' if row.get('coordinates') else 'unsupported-map'
    result['dataAgeSeconds'] = None
    result['coverage'] = 'client-cache-only'
    return result


class Comparer:
    def __init__(self):
        self.previous = None
        self.context = None

    def reset(self):
        self.previous = None
        self.context = None

    def compare(self, snapshot, epoch):
        context = (epoch, snapshot['cachedKingdom'])
        current = {r['cacheKey']: r for r in snapshot['records']}
        if self.previous is None or context != self.context:
            changes = [{'type': 'baseline', 'cachedEntries': len(current)}]
        else:
            changes = []
            for key in sorted(self.previous.keys() - current.keys()):
                changes.append({'type': 'cache_entry_not_observed', 'cacheKey': key})
            for key in sorted(current.keys() - self.previous.keys()):
                changes.append({'type': 'cache_entry_observed', 'cacheKey': key})
            for key in sorted(current.keys() & self.previous.keys()):
                old, new = self.previous[key], current[key]
                changed = sorted(k for k in new if k != 'tableID' and old.get(k) != new[k])
                if changed:
                    changes.append({'type': 'cache_fields_changed', 'cacheKey': key, 'fields': changed})
        self.previous, self.context = current, context
        return changes
