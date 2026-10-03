# Current package: kingdom scanner v6 trial

Start with [KINGDOM-SCAN.md](KINGDOM-SCAN.md) for the v7 socket message collector. The original `collect.py` below remains a separate stationary cache diagnostic.

The user's uploaded JSONL now confirms v3 passed its stationary trial:26 snapshots,99 cached entries,zero errors,complete cleanup. The user completed three automated v4 views; v5 sampled six zones successfully; v6 screenshot/OCR optimization still needs its device trial. All Might/kills in that supplied run were unknown-zero.

## Historical v3 instructions

The following text records the original v3 delivery. Its statement that the first v3 trial is pending is superseded by the result above.

# Lords Mobile cache collector — read diagnostics and cleanup repair v3

This extends the verified one-shot readers into a periodic local collector. It uses the already running Frida server on the user's rooted LDPlayer14 Android14 emulator, attaches in the native x64 realm, and reads the ARM64 Lords Mobile2.201/build692 cache. It does not require the failed emulated-realm or JDWP startup methods.

## What changed in v3

The v2 user run attached but rejected two snapshots with “Map changed during read”, then expired its startup allowance. Cleanup stalled in Frida detach and was interrupted, preventing the final summary. A still camera does not guarantee a stable client cache. The specific changing fields and actual read times were not present in the supplied console output.

- A sorted readable-memory range index is now built once per snapshot. This replaces repeated Frida range queries for every pointer/character read. Actual reads can still fail if memory mappings change; every snapshot rebuilds the index. All signature, bounds and consistency checks remain. This reduces range-query calls; actual LDPlayer speed improvement has not been measured.
- Failed snapshots now include agentReadMs, diagnostics and specific root/header/zone/capacity changes in observations.jsonl. The console also prints read time and changed field names.
- Each read schedules the next after completion, so slow reads do not accumulate interval work.
- Host cleanup waits at most3 seconds per close attempt and catches a Ctrl+C during that wait. If cleanup fails or remains pending, the collector writes an incomplete summary and stops without another attachment. A background Frida call may still be pending; device-side cleanup is not claimed. Native teardown may have its own behavior beyond the bounded Python wait.
- A reported process termination/replacement needs no further remote unload. Other cleanup failures stay visible.

Before this retest, close and reopen Lords Mobile once to clear the previously interrupted game session, then leave the map still. Do not reinstall the emulator or start a second Frida server. After a cleanup-incomplete result, restart the game before trying again.

Implementation reference: [Frida JavaScript API](https://frida.re/docs/javascript-api/) documents that enumerateRanges with r-- includes readable ranges, including those with additional permissions.

## What is implemented

- One Frida session reused for periodic observations; default delay2 seconds after each completed read and recording window60 seconds, starting with the first valid snapshot. Startup gets a separate120-second allowance (`--startup-timeout`,10..300). Reconnection does not restart the recording timer.
- All kind8 layout references in the readable cache, capped at4096 entries, instead of the first ten. Kind8 includes observed Dark.nest entries, so entity classification remains unverified.
- UTC host collection timestamps, epoch/PID, zone IDs, raw data and measured agent read duration in a JSONL log.
- Zero Might/kills become `null` with quality `unknown-zero`; the original value remains in `mightRaw`/`troopsKilledRaw`. Empty guild/name fields likewise remain available as raw values, with interpreted value null. Genuine zeros/empty guilds are possible; no availability flag is yet decoded.
- Nonzero values remain decimal strings (including uint64 values beyond JavaScript exact integers), labelled `cached-value-age-unknown`.
- Every record has freshness `unknown`, dataAgeSeconds remains null at snapshot level, and rawLevel remains meaning-unverified. A collection timestamp does not establish server freshness.
- Comparison by kingdom and layout index, with descriptive cache observations only. Table IDs are not permanent identities. Slot sharing does not drop a location. No teleport/attack/shield alert is inferred.
- Failed reads reset the comparison baseline. Detachment, agent errors, queue overflow or an unresponsive agent cause an attachment retry; the game must be running normally. A new session uses a new baseline.
- New output directory per run; existing captures are preserved. JSONL is flushed after each event. A64MiB log limit stops the run, reserving space for a final summary.

This is still a client-cache experiment. Coordinates are calibrated only for kingdom1364 with layout capacity262144. Other maps have null coordinates. No automatic map movement, popup opening, Telegram integration or shield/army/equipment decoding is added in this package.

## Existing PC setup

Expected workspace `C:\Users\ahmad\lm-frida`; existing venv already has Frida17.19.0. LDPlayer/game/Frida server should already be running. This package does not install or restart them.

Download `lm-cache-collector-v3.zip` to Downloads. In PowerShell run each command separately:

```powershell
Set-Location C:\Users\ahmad\lm-frida
```

```powershell
Expand-Archive -LiteralPath C:\Users\ahmad\Downloads\lm-cache-collector-v3.zip -DestinationPath C:\Users\ahmad\lm-frida -Force
```

```powershell
& .\.venv\Scripts\python.exe .\lm-cache-collector\collect.py --seconds 60 --interval 2
```

PID lookup is automatic. The run creates `runs\cache-<UTC time>-<unique suffix>\observations.jsonl` and `summary.json` under the PowerShell working directory. The exact directory is printed. The original trial attached but saved zero snapshots after64.53 seconds. Version1 started the timer before attachment; version2 fixed this confirmed timing defect (retained in v3) and defers the initial agent read until after script load. The exact cause of the device run awaits its journal. Startup and recording limits are checked between blocking Frida operations, which can overrun them; Ctrl+C requests cleanup and writes an interrupted summary. The game/emulator is not stopped.

## First v3 retest

Keep the map still for the whole60-second recording window. Send observations.jsonl and summary.json from the printed run folder even if the result is incomplete. The earlier v2 journal can also be supplied; it was flushed before cleanup failed, so it may still exist despite the missing summary.

## Later controlled experiment (after the still-map retest passes)

Wait for **First valid snapshot received. Recording for60 seconds.** before starting the following movements. Keep the game open on the kingdom map while connecting.

1. Begin at the familiar kingdom1364 area and keep the map still for about15 seconds.
2. Open a castle popup whose details were not recently viewed. Leave the popup open about15 seconds.
3. Close it and move a short distance on the map for about15 seconds.
4. Return to the original area for the rest of the run.

These are approximate manual timings, not commands the collector sends. Send back `summary.json` and `observations.jsonl`, plus the popup screenshot if a statistic comparison is wanted. Do not send your .env file or Telegram token.

We will look for: successful repeated snapshots, fields changing from unknown to a value after inspection, changing cached references during movement, gaps/retries, and measured read duration. This experiment does not prove old cache records have been invalidated correctly.

## Interpreting output

`summary.json` gives collectorVersion3, snapshot/error/attachment counts, total elapsed time, startupSeconds, recordingSeconds, cleanupStatus and cleanupReason. Recording time includes any later observation gaps or reconnection delays; it is not guaranteed uninterrupted coverage. `complete` means the collector recorded at least one snapshot and saw no logged errors during its run; it does not mean full map coverage or current game data. `incomplete` may still contain useful snapshots; `interrupted` means Ctrl+C during recording/startup; Ctrl+C during cleanup is instead reported as cleanup incomplete. Both return exit2; clean completion returns0.

`observations.jsonl` has one JSON object per line:

- run_start / run_end: limits and totals.
- connection_attempt / attached / agent_ready: session events with elapsed timestamps; attached includes connectionSeconds.
- recording_start: first valid snapshot accepted and recording timer started.
- startup_timeout: no valid snapshot within the startup allowance.
- snapshot: collected cache, field quality and descriptive cacheChanges.
- snapshot_unavailable: the memory reader rejected a changing/unreadable layout.
- observation_gap / connection_error: comparison cannot safely span this interval.

A cache entry disappearing can result from eviction or changing map views. A changed name at a location is not proof of a permanent player identity change. Both shield status and detail availability remain unverified. Snapshots use repeated consistency checks; they are not atomic.

The connection attempts are read-only apart from Frida instrumentation needed to load the observation agent. The reader does not call ARM functions, modify game data, send game requests or navigate the game.

## Tests and review

Local tests use mocked memory and Frida/device lifecycles. They do not replace a successful multi-snapshot emulator trial. The first actual trial failed with zero snapshots; version2 also failed its user trial; version3 awaits a device retest. The script derives from successful one-shot probes on this user's PC. Node24.14.1/Python3.9.25 were used locally; the user's Python3.14.7 runtime still needs the new collector trial.

From this package directory, optional developer checks:

```text
node --check agent.js
node test_agent.cjs
python -m unittest discover -s . -v
python collect.py --help
```

Files: `agent.js` (bounded memory reader and periodic sends), `collect.py` (session and journal), `quality.py` (unknown values and descriptive comparisons), `test_agent.cjs`, `test_collector.py`. The original standalone probes and full conversation handoff remain available separately.

After this trial: refine loaded-data markers, stable identity and classifying player/NPC records; then build the bot observation adapter. Existing screenshot survey/navigation and Telegram source have not yet been wired to this collector.
