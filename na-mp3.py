"""Konwersja pobranego albumu na MP3 320 kbps, z tagami i okładką.

    .venv\\Scripts\\python.exe na-mp3.py "<katalog albumu>" [...]

Oryginalne .m4a zostają nietknięte; MP3 lądują w katalogu obok, z sufiksem
[MP3] w nazwie. Wymaga ffmpeg w PATH.
"""

import shutil
import subprocess
import sys
from pathlib import Path

BITRATE = "320k"


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


def konwertuj_album(zrodlo: Path, ffmpeg: str) -> tuple[int, int]:
    cel = zrodlo.parent / (zrodlo.name.replace("[MP4]", "[MP3]") + ("" if "[MP4]" in zrodlo.name else " [MP3]"))
    cel.mkdir(exist_ok=True)

    okladka = zrodlo / "cover.jpg"
    if okladka.exists():
        shutil.copy2(okladka, cel / "cover.jpg")

    ok, bledy = 0, 0
    for plik in sorted(zrodlo.glob("*.m4a")):
        wyjscie = cel / (plik.stem + ".mp3")
        cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(plik)]
        if okladka.exists():
            # okładka jako drugie wejście, wpięta w tag ID3 APIC
            cmd += ["-i", str(okladka), "-map", "0:a", "-map", "1:v", "-c:v", "mjpeg",
                    "-metadata:s:v", "title=Album cover",
                    "-metadata:s:v", "comment=Cover (front)", "-disposition:v", "attached_pic"]
        else:
            cmd += ["-map", "0:a"]
        cmd += ["-map_metadata", "0", "-id3v2_version", "3", "-c:a", "libmp3lame", "-b:a", BITRATE, str(wyjscie)]

        wynik = subprocess.run(cmd, capture_output=True, text=True)
        if wynik.returncode == 0 and wyjscie.exists():
            ok += 1
            print(f"  OK  {wyjscie.name}")
        else:
            bledy += 1
            print(f"  BLAD {plik.name}: {wynik.stderr.strip()[:200]}")

    print(f"-> {cel}")
    return ok, bledy


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ffmpeg = znajdz_ffmpeg()
    print(f"ffmpeg: {ffmpeg}\n")

    razem_ok, razem_bledy = 0, 0
    for arg in sys.argv[1:]:
        zrodlo = Path(arg)
        if not zrodlo.is_dir():
            print(f"POMIJAM (nie ma takiego katalogu): {zrodlo}")
            razem_bledy += 1
            continue
        print(f"[{zrodlo.name}]")
        ok, bledy = konwertuj_album(zrodlo, ffmpeg)
        razem_ok += ok
        razem_bledy += bledy
        print()

    print(f"RAZEM: {razem_ok} plików OK, {razem_bledy} błędów")
    return 1 if razem_bledy else 0


if __name__ == "__main__":
    raise SystemExit(main())
