@echo off
title ANA Varese
echo ========================================
echo  ANA VARESE - VOLONTARIATO
echo  Avvio progetto in locale...
echo ========================================
echo.

cd /d "%~dp0"
echo Cartella: %cd%
echo.

if not exist "app.py" (
    echo ERRORE: app.py non trovato in questa cartella!
    echo.
    echo Devi mettere avvia_ana.bat nella STESSA cartella di app.py
    echo Cartella corretta: Desktop\ANA_Varese\
    echo.
    pause
    exit
)

echo File app.py trovato, controllo Python...
python --version
if errorlevel 1 (
    echo.
    echo ERRORE: Python non installato o non nel PATH!
    echo.
    echo Scarica Python da: https://www.python.org/downloads/
    echo Durante installazione spunta "Add python.exe to PATH"
    echo.
    pause
    exit
)

echo.
echo Installazione librerie in corso...
python -m pip install streamlit pandas openpyxl folium streamlit-folium Pillow requests

echo.
echo Avvio Streamlit...
echo Si aprira' su http://localhost:8501
echo Login: admin / ana2024  oppure  utente / utente2024
echo.
echo NON CHIUDERE QUESTA FINESTRA
echo Per fermare: CTRL+C o chiudi finestra
echo.

python -m streamlit run app.py

echo.
echo Streamlit si e' chiuso
pause