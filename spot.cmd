@echo off
REM spotDL z venv projektu — odpowiednik rip.cmd dla Spotify.
REM Uzycie: spot.cmd https://open.spotify.com/album/...
"%~dp0.venv\Scripts\python.exe" "%~dp0spot.py" %*
