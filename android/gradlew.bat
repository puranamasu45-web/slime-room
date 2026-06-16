@echo off
REM Lightweight Gradle launcher for local Windows builds.
WHERE gradle >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
  gradle %*
  EXIT /B %ERRORLEVEL%
)
ECHO Gradle is not installed. Install Gradle 8.10.2 or run the GitHub Actions build. 1>&2
EXIT /B 1
