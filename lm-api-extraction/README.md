# Lords Mobile APK map API extraction

Target: `com.igg.android.lordsmobile`, version 2.201, build 692, ARM64.

## Result

This package extracts the binary map interface from the supplied APK. It contains a reproducible protocol-ID extractor, native instruction evidence, request payload builder, and offline map-response decoders. **It is not yet an authenticated game-server client. No six-second kingdom scan has been demonstrated.**

The new work adds bulk baseline records (kinds 22/23), city/camp fields, march fields, context handling for chunked responses, and inspection of the main-channel frame envelope. The earlier SDK handled selected incremental changes only.

- `evidence/protocols.json`: all 2,117 `Protocol` enum constants freshly extracted from metadata. Names/IDs are a catalog; most message bodies are not decoded.
- `API-SPEC.md`: map requests, bulk responses, transport boundaries, address references, and remaining requirements.
- `extract_api.py`: verifies exact input hashes, checks metadata method identities and selected ARM64 instructions, regenerates the evidence.
- `protocol.py`, `bulk.py`: map-request builder and response decoding, Python standard library only.
- `transport.py`: envelope parsing for complete main-channel frames; body bytes remain opaque.
- `inspect_payload.py`: inspect a local binary file at a known boundary.
- `decode_capture.py`: legacy JSONL decoder, with each record decoded independently. Headerless continuations require the library context interface below; this CLI will reject them.
- `LORDSAPI-ASSESSMENT.md`: inspection of the NuGet package you supplied and its linked source.

## Use the extraction offline

Extract this ZIP into a separate directory. It does not replace the scanner or its checkpoint.

```powershell
python -m unittest discover -v
python inspect_payload.py map captured-handler-payload.bin
python inspect_payload.py request map-request-body.bin
python inspect_payload.py frames complete-main-channel-frames.bin
```

The three inputs are different boundaries. `map` expects plaintext bytes at `MapManager.RecvMapInfoPlus` entry, ending at its zero record terminator. `request` expects exactly the 41 bytes after the sequence prefix. `frames` expects complete transport frames and leaves their bodies uninterpreted. It does not reassemble TCP chunks.

Build a request body without sending it:

```python
from protocol import encode_map_request
body = encode_map_request(4, [0, 1, 2, 3], [0, 0, 0, 0], renew=True)
assert len(body) == 41
```

For consecutive, gap-free plaintext map messages from the **same session, channel and map**, retain the negotiated width context:

```python
from protocol import decode_map_updates
context = {}
result = decode_map_updates(first_message_bytes, bulk_context=context)
next_result = decode_map_updates(next_message_bytes, bulk_context=context)
```

Reset this context on reconnect, map/channel changes or capture gaps. Unsupported/truncated messages do not commit context changes. A new header is needed after loss of context. Do not assume that a successfully parsed packet is a complete zone or kingdom; batch completion and coverage need a state reducer tied to live requests.

Bulk city records do not supply Might, kills or a permanent account identifier. These are `None`, never guessed zero values. Selected incremental kind-12 updates expose Might/kills. Flag meanings such as shield status remain raw. Other point categories retain opaque bodies. Many incremental kinds and kingdom-info kind 25 remain unsupported; unknown records reject the entire message.

## Reproduce the APK extraction

Only extraction needs the pinned analysis libraries:

```powershell
python -m pip install -r requirements-extraction.txt
python extract_api.py --library "path\libil2cpp.so" --metadata "path\global-metadata.dat" --output evidence
```

The inputs come from your supplied APK/APKS. They are not redistributed here. Exact SHA256 checks prevent these offsets from being silently applied to another game build. Method addresses originate in the supplied historical handoff; the extractor rechecks their metadata names and the exact native library before using the addresses.

## Next step toward a direct scanner

A live client connection must provide the negotiated server/channel, authenticated session, sequence handling and matching transport transformation. The Android x64 Frida attachment currently used for memory reads does not establish that ARM64 methods can be called through Houdini. The code in this package performs no live login, calls or requests.

Next validation: obtain a matching request and full response batch from your own game session, compare it with this specification, implement session transport and response state tracking, then measure one zone and one four-zone batch before attempting a kingdom. The request serializer has four slots; 1,024 standard zones would require at least 256 such requests under that approach. Completing those requests in six seconds would require about 42.7 requests/second plus all response processing. Neither server acceptance at that rate nor completeness is established by the APK.

## Verification

See `VALIDATION.md`. Local tests use synthetic data. The package contains no APK, game DLL, NuGet DLL, live account data, credentials, or user screenshots.
