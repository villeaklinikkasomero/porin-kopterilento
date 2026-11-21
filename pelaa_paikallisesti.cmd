@echo off
rem Porin kopterilento paikallisesti ilman Pythonia: tuplaklikkaa. Peli aukeaa osoitteeseen http://localhost:8000/
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\palvelin.ps1"
pause
