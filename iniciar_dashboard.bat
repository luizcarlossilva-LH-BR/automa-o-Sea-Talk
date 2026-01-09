@echo off
echo ============================================================
echo  Iniciando Dashboard de Performance 3PL
echo ============================================================
echo.
echo O dashboard sera aberto em: http://localhost:8501
echo.
echo Para enviar para o SeaTalk, execute em outro terminal:
echo    python enviar_dashboard_seatalk.py
echo.
echo ============================================================
echo.

streamlit run dashboard_performance.py
