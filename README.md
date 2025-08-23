# 📊 Dashboard Mercado Laboral USA

Un dashboard interactivo para monitorear los indicadores clave del mercado laboral de Estados Unidos, con visualizaciones en tiempo real y alertas automáticas para detectar tendencias importantes.

## 🎯 Características Principales

- **9 Métricas Clave**: Tasa de desempleo, vacantes, renuncias, despidos, participación laboral, empleo en nóminas, salarios, y más
- **Visualizaciones Interactivas**: Gráficos de tendencia con Plotly
- **Alertas Automáticas**: Sistema de alertas basado en umbrales configurables
- **Datos en Tiempo Real**: Conexión con APIs oficiales (FRED y BLS)
- **Calendario de Publicaciones**: Fechas programadas de reportes oficiales con enlaces directos
- **Enlaces Directos**: Acceso rápido a PDFs y reportes oficiales
- **Modo Demo**: Datos de muestra para demostración sin APIs
- **Responsive Design**: Compatible con dispositivos móviles

## 🚀 Inicio Rápido

### 1. Activar Entorno Virtual
```bash
# Windows
venv_mercado_laboral\Scripts\activate

# Linux/Mac
source venv_mercado_laboral/bin/activate
```

### 2. Ejecutar Dashboard
```bash
streamlit run dashboard.py
```

### 3. Acceder al Dashboard
Abrir http://localhost:8501 en tu navegador

## ⚙️ Configuración

### APIs Requeridas

#### FRED API (Federal Reserve Economic Data)
1. Obtener API key gratuita: https://fred.stlouisfed.org/docs/api/api_key.html
2. Actualizar en `.env`: `FRED_API_KEY=tu_clave_aqui`

#### BLS API (Bureau of Labor Statistics) - Opcional
1. Obtener API key: https://www.bls.gov/developers/
2. Actualizar en `.env`: `BLS_API_KEY=tu_clave_aqui`

### Variables de Entorno (.env)
```env
# APIs Keys
FRED_API_KEY=tu_api_key_de_fred
BLS_API_KEY=tu_api_key_de_bls

# Configuración
DATA_UPDATE_HOUR=9
CACHE_DURATION_HOURS=24
```

## 📊 Métricas Monitoreadas

### Indicadores Principales
1. **Tasa de Desempleo** - Porcentaje de desempleo de la fuerza laboral
2. **Vacantes de Trabajo** - Número de puestos disponibles (miles)
3. **Tasa de Renuncias** - Indicador de confianza laboral
4. **Ratio Vacantes/Desempleo** - Tensión del mercado laboral

### Indicadores Complementarios
5. **Tasa de Despidos** - Indicador de deterioro económico
6. **Participación Laboral** - Porcentaje de población activa
7. **Empleo en Nóminas** - Total de empleos no agrícolas
8. **Salarios por Hora** - Crecimiento salarial promedio
9. **Fuerza Laboral** - Crecimiento de la población activa

## 🛠️ Comandos Útiles

### Actualizar Datos
```bash
# Actualización manual
python update_data.py

# Forzar actualización desde APIs
python update_data.py --force

# Con logging detallado
python update_data.py --verbose

# Generar reporte de estado
python update_data.py --report
```

### Probar Conectividad
```bash
# Probar todas las conexiones
python test_apis.py --all

# Probar solo FRED
python test_apis.py --fred

# Probar solo BLS
python test_apis.py --bls
```

### Ejecutar en Modo Desarrollo
```bash
# Con recarga automática
streamlit run dashboard.py --server.runOnSave true
```

## 📁 Estructura del Proyecto

```
Mercado laboral/
├── dashboard.py              # Aplicación principal Streamlit
├── data_collector.py         # Módulo de extracción de datos
├── config.py                 # Configuración general
├── test_apis.py              # Tests de conectividad
├── update_data.py            # Script de actualización
├── requirements.txt          # Dependencias Python
├── .env                      # Variables de entorno
├── data/                     # Base de datos SQLite local
│   └── labor_market.db       # Cache de datos
├── vibe_docs/               # Documentación del proyecto
│   ├── tarea_actual.md       # Estado del desarrollo
│   ├── configuracion_entorno.md  # Setup del entorno
│   └── solucion_problemas.md # Troubleshooting
└── venv_mercado_laboral/    # Entorno virtual Python
```

## 🔧 Solución de Problemas

### Dashboard no carga
1. Verificar que el entorno virtual esté activo
2. Ejecutar `pip install -r requirements.txt`
3. Revisar logs en la consola

### Sin datos en el dashboard
1. Activar "Usar datos de muestra" en la barra lateral
2. Configurar API keys en el archivo `.env`
3. Ejecutar `python test_apis.py --all` para verificar conectividad

### Error de encoding en Windows
- Los emojis pueden causar problemas en Windows
- Usar caracteres ASCII en logs si es necesario

### APIs no responden
1. Verificar conexión a internet
2. Confirmar que las API keys sean válidas
3. Revisar límites de rate limiting

## 📈 Dashboard Features

### KPIs Principales
- Valores actuales con cambios mensuales
- Código de colores para alertas
- Comparación con umbrales configurables

### Gráficos Interactivos
- Tendencias históricas de 5 años
- Zoom y pan habilitados
- Tooltips con información detallada
- Múltiples series en gráficos combinados

### Sistema de Alertas
- Alertas automáticas basadas en umbrales
- Indicadores visuales de estado
- Mensajes explicativos para cada alerta

### Calendario de Publicaciones 📅 NUEVA FUNCIONALIDAD
- **Fechas exactas** de publicación de reportes oficiales (Employment Situation, JOLTS, ECI)
- **Alertas de proximidad** para publicaciones en los próximos 7 días
- **Enlaces directos** a reportes actuales y PDFs oficiales
- **Información detallada** sobre horarios y frecuencia de publicación
- **Estado en tiempo real** (publicado vs. programado)

### Enlaces y Recursos
- Acceso directo a fuentes oficiales (BLS, FRED)
- Enlaces a calendarios económicos oficiales
- PDFs de reportes más recientes
- Documentación técnica de cada métrica

### Responsive Design
- Compatible con móviles y tablets
- Layout adaptativo
- Controles optimizados para touch

## 🔄 Actualización de Datos

### Automática
- Cache inteligente con duración configurable
- Actualización diaria programable
- Verificación de calidad de datos

### Manual
```bash
python update_data.py --force --verbose
```

### Programada (Opcional)
Usar cron (Linux/Mac) o Task Scheduler (Windows) para ejecutar:
```bash
python update_data.py --cleanup 30 --report
```

## 📊 Fuentes de Datos

### FRED (Federal Reserve Economic Data)
- **Series**: UNRATE, JTSJOL, JTSQUR, JTSLDR, CIVPART
- **Frecuencia**: Mensual
- **Latencia**: 1 mes típicamente

### BLS (Bureau of Labor Statistics)
- **Series**: CES0000000001, CES0500000003, CIU2010000000000SA
- **Frecuencia**: Mensual
- **Latencia**: 1-2 semanas típicamente

## 🎨 Personalización

### Colores y Temas
Editar `COLOR_PALETTE` en `config.py`:
```python
COLOR_PALETTE = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'warning': '#d62728',
    # ...
}
```

### Umbrales de Alerta
Editar `ALERT_THRESHOLDS` en `config.py`:
```python
ALERT_THRESHOLDS = {
    'unemployment_rate_high': 5.0,
    'job_openings_low': 8000000,
    # ...
}
```

## 🤝 Contribuir

1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-metrica`)
3. Commit cambios (`git commit -am 'Agregar nueva métrica'`)
4. Push al branch (`git push origin feature/nueva-metrica`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es de código abierto bajo la licencia MIT.

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar la documentación en `vibe_docs/`
2. Ejecutar tests con `python test_apis.py --all`
3. Generar reporte con `python update_data.py --report`

---

**Desarrollado con ❤️ para análisis del mercado laboral USA**