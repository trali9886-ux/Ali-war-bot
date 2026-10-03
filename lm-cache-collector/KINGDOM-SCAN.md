# Socket message collection — v7

The old click/OCR scanner is replaced. `scan.py` attaches to your running game and
observes native TCP socket reads/writes. It saves selected map message bodies and
tries the APK-derived decoder on incoming opcode 2220. It does not click, take
screenshots, invoke ARM64 game methods, replay requests, or authenticate separately.

## Install on your Windows PC

Stop an old collector with Ctrl+C and wait for its cleanup summary. Download
`lm-message-scanner-v7.zip`, then in PowerShell:

```powershell
Set-Location C:\Users\ahmad\lm-frida
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\lm-message-scanner-v7.zip" -DestinationPath . -Force
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-message-scanner.ps1
```

The installer removes only obsolete visual scanner code/tests. It keeps `runs`,
SQLite checkpoints, your `.venv`, the stationary collector and unrelated files.
Extract BOTH included folders; the collector loads the adjacent `lm-api-extraction`
decoders and message catalog. Keep your existing matching Frida client/server.
Tesseract, Pillow and ADB screen controls are not used.

## Short capture

Use the same running frida-server and LDPlayer instance as your working collector.
Open Lords Mobile normally, then:

```powershell
& .\.venv\Scripts\python.exe .\lm-cache-collector\scan.py --seconds 60
```

Wait for **Socket hooks ready**. Open the kingdom map and manually move to two or
three known locations during the 60 seconds. This manual action creates reference
traffic for validating the new capture; the program performs no input automation.
Stay in one kingdom during the trial. Note the coordinates you visited.

Send `summary.json` and `messages.jsonl` from the printed `runs\messages-...`
directory. These contain selected map messages and may contain in-game names.
Unrelated login/chat/payment message bodies are discarded by the agent before
sending events to Python. There is no need to share your password or session keys.

Optional attachment check:

```powershell
& .\.venv\Scripts\python.exe .\lm-cache-collector\scan.py --check-only
```

`hooks_ready` confirms hooks attached; it does not confirm traffic. `capture_complete`
means the timed observation ended with at least one parsed candidate, not a complete
kingdom inventory. `observedPointRecords` includes repeats, not unique players.
Ctrl+C flushes saved observations and unloads the hooks. Each run starts a separate log.
Old `--fast`, `--full`, `--minutes`, `--max-views`, and resume flags are rejected.

## Output and troubleshooting

- `map_frame`: incoming 2220 is decoded where supported. Outgoing 2201/2233/2241
  and incoming minimap 2242/2245 remain opaque. Raw selected bodies are retained.
- `parsed_candidate`: schema parsed; compare against known in-game locations before
  trusting it. First observed socket byte is assumed to start a frame. No speculative
  byte-by-byte resynchronization or encryption guessing occurs.
- `stream_rejected`: a socket did not match the catalog/framing before any map message
  was seen. This is expected for unrelated HTTPS sockets; its body is discarded.
- `capture_gap`: framing/bounds loss disables that socket until close/reconnect.
  If attach caught a partial message, reopen the game's connection while the collector
  remains attached (if game restart detaches it, rerun the collector). Never assume a
  gap-free result after a reported gap.
- `unsupported_or_misaligned`: preserve the selected raw frame for analysis; it could
  be an unsupported record, a different build/channel, or transformation/framing mismatch.
- Zero socket bytes: the game may be idle or Houdini may bypass the hooked libc exports.
  This backend is verified only against a synthetic local Linux process until your trial.
- TCP calls through read/write, recv/send, vectored I/O and msg variants are covered.
  Raw syscalls, io_uring, SSL plaintext hooks, duplicated/shared descriptors and arbitrary
  concurrent reads of one socket are not established on the emulator.

Memory, queue and output limits stop or invalidate capture instead of dropping data
silently. No complete-zone or complete-kingdom claim is made. Native server request
scheduling, authentication/sequence/cipher handling and coverage tracking remain future
work requiring validated live messages. Six-second kingdom scanning is unverified.
