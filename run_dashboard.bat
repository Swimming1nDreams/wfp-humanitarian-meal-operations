@echo off
title WFP & Partner MEAL Data Portfolio Dashboard
echo ========================================================
echo   WFP & Partner Humanitarian MEAL Operations System
echo   Interactive Portfolio Dashboard Launcher
echo ========================================================
echo.
echo Activating Virtual Environment...
call .venv\Scripts\activate.bat
echo Starting Streamlit Dashboard on http://localhost:8501 ...
streamlit run app.py --server.port 8501
pause
