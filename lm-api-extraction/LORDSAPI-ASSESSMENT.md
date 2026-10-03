# Assessment of the supplied LordsAPI link

Inspected on 2026-09-29:

- [NuGet LordsAPI 1.0.8](https://www.nuget.org/packages/LordsAPI/1.0.8): targets .NET Framework 4.7.2; last package update shown as 2020-11-14. Its nuspec describes a Steam API and release notes target game v2.29.118.
- [Linked source](https://github.com/Nekiplay/LordsMobileAPI/tree/e9b7ce5595c6d8b5c0bdf0835e591b4022aff9b2), commit `e9b7ce5595c6d8b5c0bdf0835e591b4022aff9b2` dated 2024-12-03: Windows process access via Process.NET and fixed Steam/PC memory offsets. This source revision is newer than the NuGet package and is not assumed to reproduce its DLL.

The downloaded NuGet DLL was inspected as data, never executed. It imports Windows `ReadProcessMemory`, `WriteProcessMemory` and process/window helpers. Its `Auth` class exposes `IGG_ID`/`IGG_IDAsync`; its `Map` class exposes `TropsSended`. Neither is an authenticated map-request client. The package's only System.Net type reference is WebClient; its constructor and DownloadString references occur in `PromoCodes.get_All`, not map traffic. No socket client type was found in the inspected metadata.

The current repository reads local power/energy/resources from the Windows game. It does not provide the Android zone request transport, full-kingdom player enumeration or evidence of a six-second scan. It can inform a future Windows memory-reading approach, but its offsets cannot be applied to the supplied Android ARM64 library.

The search-result screenshots are useful leads, but the specific suggestion that this package provides session-token login and whole-map polling is not supported by the package/source inspection.

`evidence/lordsapi-audit.json` retains package/DLL hashes, inspected source commit, metadata type/method inventory and native imports. No third-party DLL or source is redistributed. The APK extraction and offline parser remain independent of this package.

## More relevant transport reference

The earlier supplied handoff references [halloweeks/lords-mobile-bot](https://github.com/halloweeks/lords-mobile-bot/tree/7edf561bae136e918d7d2c0322b780a249da1ed8). I inspected that exact current commit. Its C `RequestMapData` in `src/protocol.c` writes a 49-byte packet: length, protocol 2201, sequence, count, four zone slots and 32 zero revision bytes. This agrees with the APK's normal renewal request layout. Its connection/DES/login code is a candidate for future transport work, subject to current-build/session validation. However, `RecvMapInfoPlus` in that source is an empty handler, so the project does not itself provide a complete kingdom decoder/scanner. No live connection was made, and that client was not installed into the scanner.
