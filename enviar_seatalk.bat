@echo off
echo ============================================================
echo  Capturando Dashboard e Enviando para SeaTalk
echo ============================================================
echo.
echo IMPORTANTE: O dashboard deve estar rodando!
echo (Execute primeiro: iniciar_dashboard.bat)
echo.
echo ============================================================
echo.

python enviar_dashboard_seatalk.py

echo.
echo ============================================================
pause
