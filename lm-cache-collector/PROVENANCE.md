# Source provenance

- `agent.js`, `collect.py`, `quality.py`, `test_agent.cjs`, `test_collector.py`: unchanged from the user-supplied `lm-cache-collector-v3.zip`.
- `README.md` retains original v3 instructions below a current status note; `VALIDATION.md` is the historical v3 validation. The current manifest is regenerated for this package. Current scan instructions and checks are in `KINGDOM-SCAN.md` and `SCAN-VALIDATION.md`.
- `map_navigation.py`: adapted coordinate masks/parser, overview geometry and ADB foreground/frame guards from the supplied `warbot-map-survey.zip` (`warbot/navigation.py`, `kingdom.py`, `adb_bridge.py`, `image_filters.py`). Windows executable selection, standalone diagnostics and scanner integration are new. The UI geometry still requires an LDPlayer trial.
- Route centres reproduce the supplied step-8 kingdom route. Route completion means visited/sampled camera centres, not verified full server data.
- Zone conversion `(x >> 5) + ((y >> 4) << 4)` follows the supplied `warbot/map_codes.py`, itself a port of `halloweeks/lords-mobile-bot`, `src/map_point.c`, revision `7edf561bae136e918d7d2c0322b780a249da1ed8`. Copyright (c) 2026 Hallo Weeks; MIT license retained in `third-party/halloweeks-LICENSE.txt`. The uploaded v3 journal's zones 486/502 agree with its record area X192–222/Y480–510. Presence of a requested zone is a consistency guard, not proof of fresh server data.
- No game APK, user journal, credentials, database, device identifiers beyond the documented default serial, or screenshot fixtures are distributed in the new ZIP.

- V5 fast route: one centre per32x16 coordinate zone. The actual supplied libil2cpp.so hash2352799c07c1451b17ecf2bd6cb4e2e90e56ca65c0de45f741fc96837aa524fd was rechecked with Capstone; MapManager.sendRequestMapdataMsg(bool) at0x44de9d8 reads zone count+0x19/array+0x20, loops over four zone slots, and calls MessagePacket.Send. Static request structure does not establish complete zone loading or usable native calls on the emulator.

## v7 replacement

The visual scanner and map_navigation/scan_store/scan_agent modules were removed.
message_stream.js, message_agent.js, message_capture.py and the new scan.py implement
native socket observation. The adjacent lm-api-extraction package provides the
previously extracted protocol catalog and decoders. The stationary collector and
its original attribution remain unchanged.
