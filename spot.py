"""Pobieranie muzyki z linków Spotify przez spotDL — odpowiednik rip.cmd dla Tidala.

    spot.cmd <link Spotify> [...więcej linków] [dodatkowe opcje spotdl]

Spotify daje tylko metadane (tagi, okładka, kolejność); dźwięk spotDL ściąga
z YouTube Music i dopasowuje po tytule/artyście/długości. Wynik: MP3 320 kbps
z pełnymi tagami ID3 i okładką, w tym samym katalogu co pobrania streamripa.

Album/utwór  -> StreamripDownloads\\{album-artist} - {album} ({year}) [Spotify]\\{nr} - {title}.mp3
Playlista    -> StreamripDownloads\\{list-name} [Spotify]\\{poz} - {artists} - {title}.mp3
"""

import shutil
import subprocess
import sys
from pathlib import Path

KATALOG_POBRAN = Path.home() / "StreamripDownloads"
SZABLON_ALBUM = "{album-artist} - {album} ({year}) [Spotify]/{track-number} - {title}.{output-ext}"
SZABLON_PLAYLISTA = "{list-name} [Spotify]/{list-position} - {artists} - {title}.{output-ext}"


def znajdz_ffmpeg() -> str:
    sciezka = shutil.which("ffmpeg")
    if sciezka:
        return sciezka
    # winget instaluje do Links albo do Packages — poszukaj tam
    baza = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet"
    for kandydat in list((baza / "Links").glob("ffmpeg.exe")) + list(
        (baza / "Packages").glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe")
    ):
        return str(kandydat)
    raise SystemExit("Nie znalazłem ffmpeg — zainstaluj: winget install Gyan.FFmpeg")


def main() -> int:
    argumenty = sys.argv[1:]
    if not argumenty or argumenty[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    linki = [a for a in argumenty if "spotify.com" in a]
    if not linki:
        raise SystemExit("Podaj przynajmniej jeden link open.spotify.com")

    szablon = SZABLON_PLAYLISTA if any("/playlist/" in link for link in linki) else SZABLON_ALBUM
    python = Path(sys.executable)
    cmd = [
        str(python), "-m", "spotdl",
        "--ffmpeg", znajdz_ffmpeg(),
        "--format", "mp3",
        "--bitrate", "320k",
        "--output", str(KATALOG_POBRAN / szablon),
        "--overwrite", "skip",
        "--print-errors",
        "download", *argumenty,
    ]
    print(f"-> {KATALOG_POBRAN}\n")
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
