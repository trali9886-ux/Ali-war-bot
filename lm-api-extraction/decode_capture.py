"""Convert handler capture JSONL to decoded JSONL; unsupported records are explicit errors."""
import argparse
import base64
import binascii
import json
from pathlib import Path
import sys
from protocol import BUILD, DecodeError, decode_map_updates, decode_shield_log


def decode_record(raw):
    if not isinstance(raw, dict) or raw.get('format') != 'lm-handler-capture-v1' or raw.get('build') != BUILD:
        raise DecodeError('capture format/build mismatch')
    encoded = raw.get('payload_b64')
    if not isinstance(encoded, str) or len(encoded) > 90000:
        raise DecodeError('missing or oversized payload_b64')
    try:
        payload = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise DecodeError('invalid base64') from exc
    consumed = raw.get('consumed')
    if type(consumed) is not int or consumed != len(payload):
        raise DecodeError('capture consumed length mismatch')
    if raw.get('handler') == 'MapManager.RecvMapInfoPlus':
        decoded = decode_map_updates(payload)
    elif raw.get('handler') == 'ShieldLogManager.RecvShieldLogList':
        decoded = decode_shield_log(payload)
    else:
        raise DecodeError('unsupported handler')
    return dict(observed_at=raw.get('observed_at'), protocol=raw.get('protocol'),
                synthetic=raw.get('synthetic') is True, decoded=decoded)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    args = p.parse_args(argv)
    failures = 0
    try:
        with args.input.open(encoding='utf-8') as source:
            number = 0
            while True:
                line = source.readline(100001)
                if not line:
                    break
                number += 1
                if len(line) > 100000:
                    raise DecodeError(f'capture line {number} exceeds 100000 characters')
                try:
                    result = decode_record(json.loads(line))
                    print(json.dumps(dict(line=number, status='decoded', **result)))
                except (ValueError, KeyError, TypeError) as exc:
                    failures += 1
                    print(json.dumps(dict(line=number, status='unsupported_or_invalid', error=str(exc))))
    except (OSError, UnicodeError, DecodeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2
    return 2 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
