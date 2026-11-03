@echo off
title Push WFP MEAL Project to GitHub
cd /d "%~dp0"
set "GH_PATH=C:\Program Files\GitHub CLI\gh.exe"

"%GH_PATH%" auth status
if %errorlevel% neq 0 (
    echo [!] Logging in to GitHub...
    "%GH_PATH%" auth login -p https -w -h github.com
)

echo [*] Creating and pushing repository to GitHub...
"%GH_PATH%" repo create wfp-humanitarian-meal-operations --public --source=. --remote=origin --push --description "WFP & Partner Humanitarian MEAL Operations Platform (CARI 4-point scale, Enumerator Forensics, Benford's Law, UN OCHA 4Ws, CFRM, LogFrame ITT)"
pause
