"""Nakłada oba patche streamripa opisane w README (sekcje 6 i 7).

Idempotentny — można puszczać po każdej aktualizacji streamripa:

    .venv\\Scripts\\python.exe patch.py

Patch 1: CLIENT_ID/CLIENT_SECRET streamripa są zablokowane przez Tidala.
         Bierzemy działające kredencjale z tidalapi — dynamicznie, żeby
         nie przepisywać ich ręcznie po każdej aktualizacji tidalapi.
Patch 2: endpoint /lyrics zwraca 401; streamrip łapał tylko TypeError,
         więc 401 wywracał pobieranie całego tracka.
"""

import sys
from pathlib import Path

PATCH_1_OLD = '''CLIENT_ID = base64.b64decode("elU0WEhWVmtjMnREUG80dA==").decode("iso-8859-1")
CLIENT_SECRET = base64.b64decode(
    "VkpLaERGcUpQcXZzUFZOQlY2dWtYVEptd2x2YnR0UDd3bE1scmM3MnNlND0=",
).decode("iso-8859-1")'''

PATCH_1_NEW = '''# PATCH rip-tidal: własne klucze streamripa są zablokowane przez Tidala,
# bierzemy działające kredencjale z tidalapi.
try:
    import tidalapi as _tidalapi

    _tidal_cfg = _tidalapi.Config()
    CLIENT_ID = _tidal_cfg.client_id
    CLIENT_SECRET = _tidal_cfg.client_secret
except Exception:  # fallback: wartości tidalapi zapisane na sztywno
    CLIENT_ID = base64.b64decode(
        base64.b64decode(b"WmxneVNuaGtiVzUw") + base64.b64decode(b"V2xkTE1HbDRWQT09")
    ).decode("utf-8")
    CLIENT_SECRET = base64.b64decode(
        base64.b64decode(b"TVU1dU9VRm1SRUZxZUhKblNrWktZa3RPVjB4bFFY")
        + base64.b64decode(b"bExSMVpIYlVsT2RWaFFVRXhJVmxoQmRuaEJaejA9")
    ).decode("utf-8")'''

PATCH_2_OLD = "            except TypeError as e:\n                logger.warning(f\"Failed to get lyrics for {item_id}: {e}\")"
PATCH_2_NEW = "            except Exception as e:  # PATCH rip-tidal: /lyrics zwraca 401\n                logger.warning(f\"Failed to get lyrics for {item_id}: {e}\")"


def main() -> int:
    target = (
        Path(sys.executable).parent.parent
        / "Lib"
        / "site-packages"
        / "streamrip"
        / "client"
        / "tidal.py"
    )
    if not target.exists():
        print(f"BRAK: {target} — czy streamrip jest zainstalowany w tym Pythonie?")
        return 1

    src = target.read_text(encoding="utf-8")
    for name, old, new in (
        ("Patch 1 (CLIENT_ID/SECRET)", PATCH_1_OLD, PATCH_1_NEW),
        ("Patch 2 (lyrics 401)", PATCH_2_OLD, PATCH_2_NEW),
    ):
        if new in src:
            print(f"{name}: już nałożony")
        elif old in src:
            src = src.replace(old, new)
            print(f"{name}: nałożony")
        else:
            print(f"{name}: NIE ZNALEZIONO wzorca — streamrip zmienił kod, sprawdź ręcznie")
            return 1

    target.write_text(src, encoding="utf-8")
    print(f"OK: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
