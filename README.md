# rip-tidal

Kompletny przewodnik instalacji **streamrip** do pobierania muzyki z Tidal na Windows — ze wszystkimi problemami, które po drodze napotkaliśmy.

---

## Stack

- Python 3.12
- [streamrip](https://github.com/nathom/streamrip) 2.1.0
- [tidalapi](https://github.com/tamland/python-tidal) — do autoryzacji

---

## Historia zmagań

### 1. Pierwsze podejście — tidal-dl

Zaczęliśmy od `tidal-dl` (2022.10.31.1). Instalacja poszła gładko, ale logowanie przez device flow kończyło się błędem:

```
[ERR] Login failed. Expecting value: line 1 column 1 (char 0)
```

Przyczyna: Tidal zmienił API od 2022 roku. Stare klucze API w tidal-dl są zablokowane — endpoint `https://auth.tidal.com/v1/oauth2/token` zwraca 403 z pustym body zamiast JSON.

### 2. Python 3.14 — za nowy

Próba instalacji `streamrip` na Pythonie 3.14 (najnowszym dostępnym) zakończyła się:

```
RuntimeWarning: Pillow 10.4.0 does not support Python 3.14
RequiredDependencyException: zlib
```

Rozwiązanie: zainstalować Python 3.12 obok 3.14 i używać launchera `py -3.12`.

### 3. streamrip — problem z PATH

Po instalacji przez `py -3.12 -m pip install streamrip` plik `rip.exe` wylądował w:

```
C:\Users\banam\AppData\Local\Programs\Python\Python312\Scripts
```

…który nie był w PATH. Trzeba go dodać ręcznie przez Environment Variables.

### 4. Autoryzacja Tidal — 403 na token refresh

streamrip ma własne klucze API (client_id/client_secret zakodowane w base64). Tidal blokuje te kredencjale — każda próba odświeżenia tokena kończyła się:

```
ContentTypeError: 403, message='Attempt to decode JSON with unexpected mimetype: text/html',
url='https://auth.tidal.com/v1/oauth2/token'
```

### 5. Rozwiązanie — tidalapi do autoryzacji

`tidalapi` używa innych, działających kredencjali. Autoryzacja:

```python
import tidalapi
session = tidalapi.Session()
session.login_oauth_simple()
# → otwiera link w przeglądarce, czeka na potwierdzenie

print(session.access_token)
print(session.refresh_token)
print(session.user.id)
print(session.country_code)
```

Tokeny wklejamy ręcznie do `config.toml` streamrip.

### 6. Patch #1 — podmiana CLIENT_ID w streamrip

streamrip nie mógł odświeżać tokenu bo używał własnych zablokowanych kredencjali. Patch w `tidal.py`:

```python
# Przed:
CLIENT_ID = base64.b64decode("elU0WEhWVmtjMnREUG80dA==").decode("iso-8859-1")
CLIENT_SECRET = base64.b64decode("VkpLaERGcUpQcXZzUFZOQlY2dWtYVEptd2x2YnR0UDd3bE1scmM3MnNlND0=").decode("iso-8859-1")

# Po (kredencjale z tidalapi):
CLIENT_ID = base64.b64decode(
    base64.b64decode(b"WmxneVNuaGtiVzUw")
    + base64.b64decode(b"V2xkTE1HbDRWQT09")
).decode("utf-8")
CLIENT_SECRET = base64.b64decode(
    base64.b64decode(b"TVU1dU9VRm1SRUZxZUhKblNrWktZa3RPVjB4bFFY")
    + base64.b64decode(b"bExSMVpIYlVsT2RWaFFVRXhJVmxoQmRuaEJaejA9")
).decode("utf-8")
```

### 7. Patch #2 — lyrics crashują download

streamrip próbuje pobrać teksty piosenek z `https://listen.tidal.com/v1/tracks/{id}/lyrics`. Endpoint zwraca 401. Kod łapał tylko `TypeError`, więc 401 propagował się w górę i crashował cały download tracka.

Patch w `tidal.py`:

```python
# Przed:
except TypeError as e:
    logger.warning(f"Failed to get lyrics for {item_id}: {e}")

# Po:
except Exception as e:
    logger.warning(f"Failed to get lyrics for {item_id}: {e}")
```

---

## Instalacja aktualna — laptop `Miko`, 29.08.2026

Wersja odtworzona od zera na nowym laptopie. Różni się od pierwotnej trzema rzeczami:
**Python 3.13 wystarczy** (3.12 nie jest potrzebny), **wszystko siedzi w venv projektu**
zamiast w globalnym Pythonie, a **patche nakłada skrypt**, nie ręczna edycja.

Powód venv: streamrip przypina `Pillow 10.4.0`, co przy instalacji globalnej cofa Pillow
i wywala `pdfplumber` używany w innych projektach IOMJB.

```cmd
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install streamrip tidalapi
.venv\Scripts\python.exe patch.py
.venv\Scripts\rip.exe config path
.venv\Scripts\python.exe zaloguj.py
```

| plik | co robi |
|---|---|
| `patch.py` | nakłada oba patche na `streamrip\client\tidal.py`; idempotentny — puszczasz po każdej aktualizacji streamripa. CLIENT_ID/SECRET bierze dynamicznie z tidalapi |
| `zaloguj.py` | OAuth przez tidalapi i zapis tokenów prosto do `%APPDATA%\streamrip\config.toml` — koniec ręcznego przeklejania |
| `rip.cmd` | streamrip z venv, bez ruszania globalnego PATH-a: `rip.cmd url <link>` |
| `na-mp3.py` | konwersja pobranego albumu na MP3 320 z tagami i okładką (wymaga ffmpeg: `winget install Gyan.FFmpeg`) |

### Czego się nauczyliśmy 29.08.2026

- **FLAC nie wchodzi na tym koncie.** Odpytanie API o jakości 3, 2 i 1 zwraca za każdym razem
  strumień `m4a` — sufitem jest AAC LC 320 kbps. To poziom subskrypcji/kluczy, nie konfiguracji.
  `[16B-44100kHz]` w nazwie katalogu to metadana albumu, nie tego, co przyszło.
- **Patch #2 zarabia na siebie przy każdym albumie** — 10 ostrzeżeń „lyrics 401" na album,
  zero przerwanych tracków.
- **Token z `zaloguj.py` żyje kilka godzin**, nie tydzień jak pisaliśmy pierwotnie; dalej odnawia
  się sam przez `refresh_token` (po to jest patch #1). Ręczne logowanie dopiero przy 401.

---

## Instalacja pierwotna (laptop `banam`, 16.05.2026) — instalacja globalna

Zostaje jako zapis drogi; na nowym laptopie używamy wersji wyżej.

### Wymagania

- Windows 10/11
- Python 3.12: https://www.python.org/downloads/release/python-3129/ → `Windows installer (64-bit)`
  - Podczas instalacji: zaznacz **"Add python.exe to PATH"**

### 1. Instalacja streamrip

```cmd
py -3.12 -m pip install streamrip tidalapi
```

### 2. Dodaj Scripts do PATH

Dodaj do zmiennych środowiskowych użytkownika (Environment Variables → User variables → Path → New):

```
C:\Users\<twoja_nazwa>\AppData\Local\Programs\Python\Python312\Scripts
```

### 3. Zastosuj patche

W pliku `C:\Users\<twoja_nazwa>\AppData\Local\Programs\Python\Python312\Lib\site-packages\streamrip\client\tidal.py`:

**Patch 1** — zamień CLIENT_ID i CLIENT_SECRET (linie ~21-24) na wersję z tidalapi (patrz wyżej).

**Patch 2** — zamień `except TypeError` na `except Exception` przy fetchowaniu lyrics.

### 4. Zaloguj się do Tidal przez tidalapi

```cmd
py -3.12
```

```python
import tidalapi
session = tidalapi.Session()
session.login_oauth_simple()
# Otwórz link z terminala w przeglądarce i zatwierdź
print(session.access_token)
print(session.refresh_token)
print(session.user.id)
print(session.country_code)
```

### 5. Uzupełnij config streamrip

Otwórz `C:\Users\<twoja_nazwa>\AppData\Roaming\streamrip\config.toml` i w sekcji `[tidal]` wklej:

```toml
user_id = "<user.id>"
country_code = "<country_code>"
access_token = "<access_token>"
refresh_token = "<refresh_token>"
token_expiry = "<unix_timestamp_wygaśnięcia>"  # np. 1778956156
```

### 6. Pobieranie

```cmd
rip.exe url <link_tidal>
```

Przykład:
```cmd
rip.exe url https://tidal.com/playlist/8ed34e24-3753-4dfd-882b-5c17edfd5e7a
```

Pliki lądują w `C:\Users\<twoja_nazwa>\StreamripDownloads\`.

---

## Odnawianie tokena

Token wygasa po ok. 1 tygodniu. Żeby odnowić — powtórz krok 4 i 5.

---

## Format plików

Domyślnie streamrip pobiera w M4A (AAC) lub FLAC zależnie od dostępnej jakości. Aby konwertować do MP3, w `config.toml`:

```toml
[conversion]
enabled = true
codec = "MP3"
lossy_bitrate = 320
```
