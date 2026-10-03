# Message collector v7 validation

Replaces the old visual route scanner. Source repository is unborn; content hashes
in the package manifest identify the tested files.

## New checks

- Python `python -m unittest test_messages -v`: decoder context isolation and reset,
  unsupported bodies, opaque outgoing messages, hook-only/no-data/error/interrupt
  status, partial stream stop, unrelated socket rejection, output limits and cleanup failure.
- Node `node test_message_stream.cjs`: every byte split of a synthetic frame,
  combined frames, unrelated-body filtering, bounds, fd reuse and invalid framing.
- `node --check message_agent.js`.
- Real local Frida17.19.0 / Linux x64 integration against a synthetic Python TCP
  process: incoming split header, sendmsg multi-buffer transfer, two map responses
  (baseline and continuation), decoded synthetic player Alice, outgoing request,
  unrelated synthetic login body excluded, stop acknowledgement and cleanup.
  No game server was contacted. This is not an LDPlayer result.
- Extracted package CLI and membership/manifest checks; obsolete route flags rejected.

Unchanged API decoders and stationary collector retain their previous recorded
checks after SHA256 equivalence comparison. No OCR checks apply to this replacement.

## Limits

Real Android/LDPlayer hook reachability, live packet formats, encrypted/other channel
bodies, coverage and throughput require the user's game session. No authenticated
request scheduler or whole-kingdom scan is implemented. First observed frame boundary
is assumed and messages are parsed candidates until compared with the game.
Native ARM64 game-function hooking remains unverified; this backend hooks native libc.

PowerShell installer execution is untested in this Linux sandbox; its exact obsolete
file list and preservation behavior are checked statically during package validation.
CodeRabbit review was attempted and reported disabled; no review findings are available.
