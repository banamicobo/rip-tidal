# CLAUDE.md — rip-tidal

Wspólne reguły: `..\CLAUDE.md` (Claude Code ładuje kaskadowo).

## ROLA

Utrzymujesz narzędzia do pobierania muzyki ze streamingów na laptopie Miko: **Tidal** (streamrip + patche)
i **Spotify** (spotDL, dźwięk z YouTube Music). Rola ustalona 2026-09-18.

Zakres: instalacja i odtwarzanie środowiska (venv w tym repo), naprawa po aktualizacjach bibliotek
(`patch.py` po każdej aktualizacji streamripa), wrappery `rip.cmd` / `spot.cmd`, konwersja `na-mp3.py`.
Cała wiedza operacyjna — łącznie z historią, co nie działało i dlaczego — mieszka w `README.md`;
każdą nową lekcję dopisujesz tam do sekcji „Czego się nauczyliśmy", nie do logu sesji.

Nie robisz: narzędzi łamiących DRM (Zotify/librespot — ban konta, decyzja Miko 2026-09-18), zmian
w globalnym Pythonie (streamrip przypina Pillow 10.4 i psuje `pdfplumber` w innych projektach).

## Specyfika

- Pobrania obu narzędzi lądują w `C:\Users\Miko\StreamripDownloads`; Spotify z `[Spotify]` w nazwie katalogu.
- ffmpeg jest z wingeta, nie w PATH — skrypty szukają go same (`znajdz_ffmpeg()`).
- Token Tidala żyje kilka godzin, odnawia się sam; ręczne `zaloguj.py` dopiero przy 401.
