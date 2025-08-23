# ⚙️ Configuración del Entorno - Dashboard Mercado Laboral USA

## 🎯 Stack Tecnológico
- **Lenguaje**: Python 3.9+
- **Frontend**: Streamlit 1.28+
- **Visualizaciones**: Plotly 5.17+
- **Datos**: pandas 2.1+, requests 2.31+
- **Base de Datos**: SQLite3 (nativo Python)
- **APIs**: BLS API + FRED API (Federal Reserve)

## 📋 Prerequisitos
- Python 3.9 o superior instalado
- pip (gestor de paquetes Python)
- Conexión a internet para APIs
- Editor de código (VS Code recomendado)

## 🚀 Instrucciones de Configuración

### 1. Verificar instalación de Python
```bash
python --version
# Debe mostrar Python 3.9+ 
```

### 2. Crear entorno virtual
```bash
# Crear entorno virtual
python -m venv venv_mercado_laboral

# Activar entorno (Windows)
venv_mercado_laboral\Scripts\activate

# Activar entorno (Linux/Mac)
source venv_mercado_laboral/bin/activate
```

### 3. Instalar dependencias principales
```bash
# Instalar librerías core
pip install streamlit plotly pandas requests sqlite3

# Librerías adicionales para análisis
pip install numpy datetime pytz

# Para desarrollo y testing
pip install jupyter ipython
```

### 4. Crear archivo requirements.txt
```txt
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
requests>=2.31.0
numpy>=1.24.0
pytz>=2023.3
```

### 5. Instalar desde requirements
```bash
pip install -r requirements.txt
```

## 🔑 Configuración de APIs

### Bureau of Labor Statistics (BLS) API
- **URL Base**: https://api.bls.gov/publicAPI/v2/timeseries/data/
- **Límites**: 25 queries por día (gratis), 500 series por query
- **Registro**: https://www.bls.gov/developers/api_signature_v2.html (opcional pero recomendado)

### FRED API (Federal Reserve)
- **URL Base**: https://api.stlouisfed.org/fred/
- **API Key**: Requerida (gratuita)
- **Registro**: https://fred.stlouisfed.org/docs/api/api_key.html

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
# APIs Keys
BLS_API_KEY=tu_api_key_aqui_opcional
FRED_API_KEY=tu_api_key_aqui_requerida

# Configuración de datos
DATA_UPDATE_HOUR=9
CACHE_DURATION_HOURS=24
```

## ▶️ Cómo Ejecutar

### Desarrollo
```bash
# Asegurar que el entorno virtual esté activo
# venv_mercado_laboral\Scripts\activate (Windows)

# Ejecutar dashboard principal
streamlit run dashboard.py

# El dashboard estará disponible en: http://localhost:8501
```

### Testing de APIs
```bash
# Probar conectividad FRED
python test_apis.py --fred

# Probar conectividad BLS
python test_apis.py --bls

# Probar ambas
python test_apis.py --all
```

### Actualización de datos
```bash
# Actualización manual de datos
python update_data.py

# Actualización con logging detallado
python update_data.py --verbose
```

## 📁 Estructura del Proyecto
```
Mercado laboral/
├── vibe_docs/           # Documentación
├── dashboard.py         # Aplicación principal Streamlit
├── data_collector.py    # Módulo de extracción de datos
├── data_processor.py    # Procesamiento y análisis
├── config.py           # Configuración general
├── test_apis.py        # Tests de conectividad
├── update_data.py      # Script de actualización
├── requirements.txt    # Dependencias
├── .env               # Variables de entorno
└── data/              # Cache local SQLite
    └── labor_market.db
```

## 🔧 Comandos de Desarrollo

### Instalar en modo desarrollo
```bash
# Para desarrollo activo con recarga automática
pip install streamlit --upgrade

# Ejecutar con recarga automática
streamlit run dashboard.py --server.runOnSave true
```

### Verificar instalación
```bash
# Verificar Streamlit
streamlit --version

# Verificar Plotly
python -c "import plotly; print(plotly.__version__)"

# Verificar pandas
python -c "import pandas; print(pandas.__version__)"
```

## 🚨 Solución de Problemas Comunes

### Error: "streamlit: command not found"
```bash
# Reinstalar Streamlit
pip uninstall streamlit
pip install streamlit

# Verificar PATH
echo $PATH
```

### Error de permisos en Windows
```bash
# Ejecutar como administrador o usar:
python -m streamlit run dashboard.py
```

### Error de conectividad API
- Verificar conexión a internet
- Confirmar API keys en archivo `.env`
- Revisar límites de rate limiting

### Error de dependencias
```bash
# Limpiar e instalar de nuevo
pip freeze > installed_packages.txt
pip uninstall -r installed_packages.txt -y
pip install -r requirements.txt
```

## 📊 Variables de Entorno Requeridas
- `FRED_API_KEY`: Clave API de FRED (OBLIGATORIA)
- `BLS_API_KEY`: Clave API de BLS (opcional, pero recomendada)
- `DATA_UPDATE_HOUR`: Hora de actualización diaria (default: 9)
- `CACHE_DURATION_HOURS`: Duración del caché (default: 24)

## ⚡ Verificación Final
```bash
# Test completo del entorno
python -c "
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import sqlite3
print('✅ Entorno configurado correctamente')
"
```