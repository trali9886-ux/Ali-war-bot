"""Observe Lords Mobile map messages through native sockets (no clicks or OCR)."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='emulator-5554', help='Existing Frida device ID')
    parser.add_argument('--seconds', type=int, default=60, help='Capture duration after hooks are ready (5..3600)')
    parser.add_argument('--check-only', action='store_true', help='Check hook attachment; does not prove traffic capture')
    parser.add_argument('--output-dir', type=Path, default=Path('runs'))
    args = parser.parse_args(argv)
    if not 5 <= args.seconds <= 3600:
        parser.error('seconds must be 5..3600')
    try:
        import frida
        from message_capture import capture
        args.output_dir.mkdir(parents=True, exist_ok=True)
        destination = Path(tempfile.mkdtemp(prefix='messages-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-', dir=str(args.output_dir)))
        print('Output directory: {}'.format(destination.resolve()), flush=True)
        return capture(frida, args.device, args.seconds, destination, args.check_only)
    except ImportError as exc:
        print('Use your existing Frida .venv and extract both package folders: {}'.format(exc), file=sys.stderr)
        return 2
    except Exception as exc:
        print('Capture failed: {}'.format(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
