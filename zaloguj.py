"""Autoryzacja Tidala przez tidalapi + zapis tokenów do configu streamripa.

    .venv\\Scripts\\python.exe zaloguj.py

Skrypt wypisze link — otwierasz go w przeglądarce, logujesz się i zatwierdzasz.
Tokeny lądują w %APPDATA%\\streamrip\\config.toml (NIGDY w repo).
Token żyje ok. tygodnia — po wygaśnięciu puszczasz skrypt ponownie.
"""

import os
import re
from pathlib import Path

import tidalapi

CONFIG = Path(os.environ["APPDATA"]) / "streamrip" / "config.toml"


def wstaw(sekcja: str, klucz: str, wartosc: str, tekst: str) -> str:
    """Podmienia klucz w danej sekcji TOML-a, zachowując resztę pliku."""
    naglowek = re.search(rf"^\[{re.escape(sekcja)}\]\s*$", tekst, re.M)
    if not naglowek:
        raise SystemExit(f"Brak sekcji [{sekcja}] w {CONFIG}")
    nastepna = re.search(r"^\[", tekst[naglowek.end():], re.M)
    koniec = naglowek.end() + (nastepna.start() if nastepna else len(tekst))
    blok = tekst[naglowek.end():koniec]
    nowa_linia = f'{klucz} = "{wartosc}"'
    if re.search(rf"^{re.escape(klucz)}\s*=", blok, re.M):
        blok = re.sub(rf"^{re.escape(klucz)}\s*=.*$", nowa_linia, blok, count=1, flags=re.M)
    else:
        blok = blok.rstrip("\n") + f"\n{nowa_linia}\n"
    return tekst[:naglowek.end()] + blok + tekst[koniec:]


def main() -> None:
    if not CONFIG.exists():
        raise SystemExit(f"Brak {CONFIG} — odpal najpierw `rip config path`")

    session = tidalapi.Session()
    print("Otwórz link poniżej w przeglądarce, zaloguj się i zatwierdź:\n")
    session.login_oauth_simple()

    if not session.check_login():
        raise SystemExit("Logowanie nieudane — nic nie zapisuję.")

    tekst = CONFIG.read_text(encoding="utf-8")
    for klucz, wartosc in (
        ("user_id", str(session.user.id)),
        ("country_code", session.country_code),
        ("access_token", session.access_token),
        ("refresh_token", session.refresh_token),
        ("token_expiry", str(int(session.expiry_time.timestamp()))),
    ):
        tekst = wstaw("tidal", klucz, wartosc, tekst)
    CONFIG.write_text(tekst, encoding="utf-8")

    print(f"\nOK — tokeny zapisane w {CONFIG}")
    print(f"Ważne do: {session.expiry_time}")
    print("Pobieranie:  rip.cmd url <link_tidal>")


if __name__ == "__main__":
    main()
