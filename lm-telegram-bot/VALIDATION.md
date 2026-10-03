# Validation — 2026-10-01

## Passed locally

- 17 Python tests for importing cache and packet observations, uint64/unknown values,
  source/session isolation, follow alerts, location/name changes, restart offsets,
  partial lines, file replacement, access control, four-button card flow and styles,
  pagination/search, safe HTML, unknown equipment/shield values, rate limits,
  API request construction, token-safe errors, single-instance lock and runner polling.
- Imported the user's supplied v3 observations into a temporary database: 99 records,
  99 saved coordinate pairs, zero recorded changes. No user data is included in ZIP.
- Actual network capture is covered by the previous v7 validation, not retested here.
  Existing collector/API files retain their earlier verification when hashes match.

## Reference review

XRecorder_20261001_01.mp4 from the supplied Drive folder was decoded with PyAV.
Duration120.866 seconds,720x1616. Frames at0,10,...110 seconds were inspected,
covering the cluttered old interface, compact Telegram cards and WhatsApp examples.
This was visual sampling, not continuous playback or an audio transcription.
The four-button Telegram portion drove the design. Telegram's official Bot API
supports the selected danger/primary/success button styles and callback handling.
Reference: https://core.telegram.org/bots/api#inlinekeyboardbutton

## Outstanding

The prescribed CodeRabbit emulate v0.0.1 catalog was installed and inspected.
Telegram is not in its service catalog, so no supported Telegram emulator is
available. Bot API contracts and flows use in-process fakes in tests. Real Telegram
send/edit/getUpdates delivery and Android Telegram display require a bot token on
the user's PC. No live Telegram messages were sent from this task.

Windows CMD launchers/PowerShell installer and actual LDPlayer collection need a
user-device trial. The interface reads observations; it does not make whole-kingdom
requests or provide unobserved equipment, shield timers, online status or army actions.

CodeRabbit review was attempted but is disabled for this task; no review ran.
