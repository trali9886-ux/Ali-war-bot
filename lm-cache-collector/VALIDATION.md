# Collector v3 validation

Actual user trials: v1 saved zero snapshots after64.53 seconds; v2 attached and produced two consistency rejections, then startup expired and cleanup blocked until Ctrl+C. No successful sustained run is claimed.

V3 replaces per-read range queries with one sorted inventory per snapshot, retains read exceptions and all consistency safeguards, records exact changed header fields and rejected-read duration, schedules the next read after completion, and bounds Python cleanup waiting to3 seconds. Cleanup failure is explicit and prevents another attachment; a pending device operation is not assumed cancelled.

Local tests use mocked game memory/Frida and actual local thread/event synchronization. Python3.9.25 and Node24.14.1. Final26 Python tests pass; JavaScript syntax and memory/scheduling fixtures pass. A new range-hole fixture initially expected the underlying error at the top level; corrected it to inspect the existing per-class diagnostic. Production rejection was already correct. No measured emulator speed or live consistency success yet. Native build offsets/signatures remain unchanged; prior static evidence reused.

CodeRabbit review returned disabled-for-task; no actual review or findings were produced. User emulator retest and full game-state/Telegram integration remain outstanding.
