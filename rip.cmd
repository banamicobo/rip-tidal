@echo off
REM streamrip z venv projektu — bez ruszania globalnego PATH-a.
REM Uzycie: rip.cmd url https://tidal.com/playlist/...
"%~dp0.venv\Scripts\rip.exe" %*
