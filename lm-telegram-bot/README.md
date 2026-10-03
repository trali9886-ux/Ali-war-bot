# Simple Lords Tracker

A small Telegram interface based on the October 1 reference video:
one player card, four actions, short screens. No AI subscription is required.

## Start in three steps

1. Extract the entire ZIP into **C:\Users\ahmad\lm-frida**.
2. In Telegram, open **@BotFather**, send **/newbot**, and create your bot.
3. Double-click **START-BOT.cmd**. Paste the bot token in its private prompt,
   then open the Telegram link printed in that window.

After the first setup, just double-click START-BOT.cmd and open your bot.
Your existing Python environment works. The bot needs no extra Python packages.
Keep the window open for the bot to respond. Ctrl+C stops it.
Never paste your bot token into a chat or send it with diagnostic files.

## What you see

**Menu:** Find player · Players · Following · Status

**Player:** name/guild, saved coordinates, Might and kills, observation time.

**Buttons:** Track · Info · Equipment · Activity

Track follows the saved location/record. Notifications summarize recorded changes.
Activity shows the last five recorded changes. Lists show five names at a time.
Back/Menu buttons keep navigation short. Unknown values appear as a dash.
Your symbol guide is used: ✊ means Might and ⚔️ means Kills. Labels stay visible
so you do not need to memorize symbols. Castle level in Info is not leader level.
Shield, burning, rally and movement icons are hidden until their data is verified.
Equipment shows a short empty state until equipment data is available.

## Game data

The bot reads your existing `runs/**/observations.jsonl` and
`runs/**/messages.jsonl` files automatically. Leave them under the existing `runs`
folder. No need to upload logs to Telegram. Initial imports may take a few polling
cycles for a large folder. Files and database offsets persist across restarts.

**CAPTURE-GAME.cmd** runs the v7 60-second message collector using your existing
LDPlayer/Frida setup. Open the game and move to a few known locations during this
trial. Newly captured, supported records become searchable automatically.

The v3 cache collector's successful saved runs can populate cards now. Those values
have unknown server age. V7 packet candidates show only decoded castle baseline
records; coordinates and current kingdom are not guessed from home kingdom/zone IDs.
Advanced location-only deltas are retained in raw capture, not assigned to a possibly
different player. Future validated identity/transport work can expand this adapter.

This interface does not yet independently scan the kingdom. Equipment, shield expiry,
Fury, online/sleep status, troop estimates and army actions from other bots in the
video are not provided by our validated data. They are not fabricated.

## Privacy and groups

The one-time link pairs your own account to the bot. Unpaired strangers receive no
player data. Local bot state lives in `runs/telegram/`; keep that folder private.
The token is saved in config.json on your PC. Do not share that file/database.

Optional group use: add the bot to your group, then send **/allowgroup** in that
group from the paired owner's account. Group members can then use its cards and
follow list. **/removegroup** from the owner turns group access off and clears the
group follows. Private access remains restricted to the paired owner.

To replace a bot token, run `.venv\Scripts\python.exe lm-telegram-bot\run.py --setup`.
A different bot identity resets chat permissions and follows, preserving observations.
Only one process can use a bot state directory at a time. Delivery retries can repeat
an alert if Telegram accepted it before a connection failed; exactly-once delivery
cannot be guaranteed by Telegram's sendMessage API.

## Verification

See VALIDATION.md. Local tests use synthetic identities and fixture messages.
Production Telegram delivery requires your bot token and internet access. Windows
launcher execution and the actual LDPlayer capture need a device trial.
