@echo off
echo 🤖 DESARROLLO COMPLETAMENTE AUTÓNOMO
echo =====================================
echo.
echo Claude desarrollará de forma independiente
echo Sin intervención humana requerida
echo.

echo 📦 Verificando dependencias...
venv_mercado_laboral\Scripts\pip.exe install selenium webdriver-manager >nul 2>&1

echo 📁 Creando directorios...
if not exist screenshots mkdir screenshots
if not exist analysis mkdir analysis

echo 🤖 Ejecutando análisis autónomo...
echo.
echo ⏳ Esto puede tomar unos minutos...
echo - Iniciando Streamlit automáticamente
echo - Abriendo Chrome en modo headless
echo - Capturando screenshots de todas las pestañas
echo - Analizando contenido automáticamente
echo - Generando reportes completos
echo.

venv_mercado_laboral\Scripts\python.exe autonomous_viewer.py

echo.
echo 📊 RESULTADOS DISPONIBLES:
echo - Screenshots: carpeta screenshots/
echo - Análisis: carpeta analysis/
echo - Logs: salida de consola arriba
echo.
echo ✅ Desarrollo autónomo completado
pause