# Validation — 2026-09-29

## Completed locally

- APK native library SHA256: `2352799c07c1451b17ecf2bd6cb4e2e90e56ca65c0de45f741fc96837aa524fd`.
- Metadata SHA256: `f5d076f2c48f3abd6ff8daecedde77896241f0bd4ef779741ea6bcd033a4764a`.
- Re-extracted all 2,117 protocol constants from metadata v31. Compared every name/ID with the supplied historical catalog: exact agreement.
- Verified 36 selected method names/declaring types against raw metadata and 43 instruction assertions against the exact ARM64 library. Included request serialization, bulk bitfields, sequence, transport frame boundaries, TCP constants, minimap request and guest response dispatch. Native addresses initially came from the historical handoff, not a new general IL2CPP symbol resolver.
- Ran all 18 Python decoder tests successfully. After simplifying an equivalent bulk format string, reran the seven affected bulk/transport tests successfully; the other 11 test results remain applicable.
- Tests cover literal synthetic city/march data, 64-bit values, every truncation of the sample, maximum count bitfields, continuation widths, unsupported records, failed-message context rollback, opaque fields, extensions and frame boundaries.
- Compiled the original C reference `RequestMapData` function in isolation with a local send stub. Its 49 output bytes exactly match the Python body plus header/sequence. The stub performs no networking or encryption. Reference commit: `7edf561bae136e918d7d2c0322b780a249da1ed8`.
- Inspected LordsAPI1.0.8 as .NET metadata using dnfile0.18.0; did not execute the DLL. Checked its NuGet metadata and linked repository separately. Findings are in LORDSAPI-ASSESSMENT.md.

Runtime: Python3.9.25, Capstone5.0.9, pyelftools0.32, GNU C compiler for the isolated reference comparison. Decoder/inspector code uses Python standard library only.

## Unverified

No live game/server session is available in this sandbox. No login, request transmission, encryption interoperability, complete map response, current server limits or six-second scan has been tested. Synthetic parsing success is not a coverage benchmark. The server API/client integration remains unfinished.

CodeRabbit review was attempted; the task configuration reports review disabled. No review findings were produced.

## Provenance

The map request and selected incremental/shield decoders plus their original tests derive from the user's supplied `lords-mobile-protocol-sdk` handoff. Bulk decoding, envelope inspection and reproducible extraction were added in this task. Archived inputs were left unchanged.

The version31 metadata structure layout was checked against [Il2CppDumper's MetadataClass.cs](https://github.com/Perfare/Il2CppDumper/blob/master/Il2CppDumper/Il2Cpp/MetadataClass.cs). No extractor code was copied from it. The C reference was used in a local comparison; its source is not included in this package. NuGet DLLs, APK binaries, real packets and account/session data are excluded.
