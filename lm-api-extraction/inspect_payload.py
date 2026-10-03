"""Decode a bounded local binary file; select the known plaintext boundary."""
import argparse
import json
from pathlib import Path
from protocol import DecodeError, decode_map_request, decode_map_updates
from transport import decode_frames


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=['map', 'request', 'frames'])
    parser.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        with args.file.open('rb') as source:
            payload = source.read(65536)
        if len(payload) > 65535:
            raise DecodeError('input exceeds 65535 bytes')
        value = {'map': decode_map_updates, 'request': decode_map_request, 'frames': decode_frames}[args.kind](payload)
    except (OSError, ValueError) as exc:
        print(json.dumps(dict(status='unsupported_or_invalid', reason=str(exc))))
        return 2
    print(json.dumps(dict(status='decoded', data=value), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
