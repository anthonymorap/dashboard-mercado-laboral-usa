# 📊 Dashboard Mercado Laboral USA

Dashboard interactivo profesional para monitorear los 9 indicadores clave del mercado laboral de Estados Unidos, con visualizaciones en tiempo real, calendario de publicaciones oficiales y sistema de alertas automáticas.

**🌐 DEMO EN VIVO**: https://dashboard-mercado-laboral-usa-wfypdtffs6ynuajwkibn7q.streamlit.app/

## 🎯 Características Principales

- **📊 9 Métricas Oficiales**: Datos directos de BLS y FRED
- **📈 Visualizaciones Interactivas**: Gráficos profesionales con Plotly
- **🚨 Sistema de Alertas**: Notificaciones basadas en umbrales críticos  
- **📅 Calendario de Publicaciones**: Fechas exactas de reportes oficiales 2025-2026
- **🔗 Enlaces Directos**: Acceso inmediato a PDFs y reportes oficiales
- **📱 Responsive Design**: Funciona en móviles, tablets y desktop
- **🤖 Modo Demo**: Datos simulados para usar sin configuración

## 📊 Métricas del Dashboard

### Indicadores Principales (KPIs)
1. **Tasa de Desempleo** (FRED: UNRATE) - Indicador clave de salud económica
2. **Vacantes de Trabajo** (FRED: JTSJOL) - Demanda laboral disponible  
3. **Tasa de Renuncias** (FRED: JTSQUR) - Confianza de trabajadores
4. **Ratio Vacantes/Desempleo** - Tensión del mercado laboral

### Indicadores Complementarios
5. **Tasa de Despidos** (FRED: JTSLDR) - Indicador de deterioro económico
6. **Participación Laboral** (FRED: CIVPART) - Porcentaje población activa
7. **Empleo en Nóminas** (BLS: CES0000000001) - Total empleos no agrícolas
8. **Salarios por Hora** (BLS: CES0500000003) - Crecimiento salarial
9. **Índice Costo Empleo** (BLS: CIU2010000000000SA) - Costos laborales totales

## 📅 Calendario de Publicaciones (NUEVA FUNCIONALIDAD)

El dashboard incluye un calendario completo con las fechas exactas de publicación de reportes oficiales:

### Employment Situation Report (BLS)
- **Frecuencia**: Mensual (primer viernes del mes)
- **Horario**: 8:30 AM ET
- **Incluye**: Desempleo, empleo en nóminas, salarios, participación laboral

### JOLTS Report (BLS) 
- **Frecuencia**: Mensual (2 meses después del mes de referencia)
- **Horario**: 10:00 AM ET  
- **Incluye**: Vacantes, renuncias, despidos

### Employment Cost Index (BLS)
- **Frecuencia**: Trimestral
- **Horario**: 8:30 AM ET
- **Incluye**: Índice de costos laborales totales

**🎯 Características del Calendario:**
- ✅ Fechas programadas 2025-2026
- ✅ Alertas para publicaciones próximas (7 días)
- ✅ Enlaces directos a reportes actuales
- ✅ Acceso a PDFs oficiales
- ✅ Información detallada de cada reporte

## 🚀 Acceso Rápido

### Opción 1: Demo Online (Recomendado)
**Accede directamente**: https://dashboard-mercado-laboral-usa-wfypdtffs6ynuajwkibn7q.streamlit.app/

### Opción 2: Instalación Local
```bash
# 1. Clonar repositorio
git clone https://github.com/anthonymorap/dashboard-mercado-laboral-usa.git

# 2. Instalar dependencias  
pip install -r requirements.txt

# 3. Ejecutar dashboard
streamlit run dashboard.py
```

## ⚙️ Configuración APIs (Opcional)

Para datos en tiempo real (el dashboard funciona en modo demo sin configuración):

### FRED API (Recomendado)
1. Obtener API key gratuita: https://fred.stlouisfed.org/docs/api/api_key.html
2. Crear archivo `.env`:
```env
FRED_API_KEY=tu_clave_fred_aqui
BLS_API_KEY=tu_clave_bls_aqui_opcional
```

### BLS API (Opcional)
- Aumenta límites de consultas
- Registro: https://www.bls.gov/developers/

## 🛠️ Herramientas de Desarrollo

### Scripts Incluidos
```bash
# Probar conectividad APIs
python test_apis.py --all

# Actualizar datos manualmente  
python update_data.py --force --verbose

# Sistema de visualización avanzado
python view_dashboard.py http://localhost:8501
```

### Herramientas Avanzadas
- **autonomous_viewer.py**: Visualización automática headless
- **iterative_dev.py**: Sistema de desarrollo iterativo
- **autonomous_dev.bat**: Script de análisis completo

## 📁 Estructura del Proyecto

```
dashboard-mercado-laboral-usa/
├── 📊 dashboard.py              # Aplicación principal Streamlit
├── ⚙️ config.py                # Configuración centralizada  
├── 📈 data_collector.py        # Extracción datos APIs
├── 🧪 test_apis.py             # Testing conectividad
├── 🔄 update_data.py           # Actualización de datos
├── 👁️ view_dashboard.py        # Herramienta visualización
├── 🤖 autonomous_viewer.py     # Sistema autónomo
├── 🔧 iterative_dev.py         # Desarrollo iterativo
├── 📋 requirements.txt         # Dependencias Python
├── 📚 README.md               # Esta documentación
├── 📖 DOCUMENTACION_COMPLETA.md # Documentación técnica detallada
└── 📂 vibe_docs/              # Documentación desarrollo
    ├── configuracion_entorno.md
    ├── solucion_problemas.md
    └── registro_desarrollo.md
```

## 📱 Navegación del Dashboard

### Pestaña 1: 📊 Análisis de Datos
- **KPIs Principales**: 4 métricas destacadas con indicadores
- **Gráfico Combinado**: Vista general de todas las tendencias  
- **Análisis Individual**: Pestaña por cada métrica con estadísticas

### Pestaña 2: 📅 Calendario de Publicaciones
- **Employment Situation**: Fechas y enlaces directos
- **JOLTS Report**: Cronograma completo con alertas
- **Employment Cost Index**: Calendario trimestral

### Pestaña 3: 🔗 Enlaces Útiles  
- **Fuentes Oficiales**: BLS, FRED, calendarios económicos
- **Reportes Actuales**: Links directos a publicaciones
- **Documentos PDF**: Acceso a reportes oficiales

## 🔧 Stack Tecnológico

- **Frontend**: Streamlit 1.48+
- **Visualizaciones**: Plotly 6.3+ 
- **Procesamiento**: pandas 2.3+
- **APIs**: requests 2.32+
- **Cache**: SQLite3 local
- **Deploy**: Streamlit Cloud
- **Testing**: Selenium + WebDriver Manager

## 🎯 Casos de Uso

### Para Analistas Económicos
- Monitoreo continuo de indicadores clave
- Alertas automáticas de cambios significativos  
- Acceso directo a fuentes oficiales

### Para Planificación Estratégica
- Calendario exacto de publicaciones importantes
- Anticipación de datos críticos
- Análisis de tendencias históricas

### Para Investigación  
- Datos oficiales verificados
- Visualizaciones para presentaciones
- Enlaces directos a metodología

## 🚨 Sistema de Alertas

### Umbrales Configurados
- **Desempleo Alto**: >5.0%
- **Vacantes Bajas**: <8M  
- **Renuncias Bajas**: <2.0% (baja confianza)
- **Despidos Altos**: >1.5%
- **Participación Baja**: <62.0%

### Tipos de Alerta
- 🔴 **Crítica**: Valores fuera de rangos normales
- 🟡 **Advertencia**: Tendencias preocupantes
- 🔵 **Información**: Cambios menores notables

## 📊 Fuentes de Datos

### Bureau of Labor Statistics (BLS)
- Employment Situation (mensual)
- JOLTS Report (mensual)  
- Employment Cost Index (trimestral)
- Latencia típica: 1-2 semanas

### Federal Reserve Economic Data (FRED)
- Todas las series de St. Louis Fed
- Actualización automática
- Latencia típica: Mismo día BLS

## 🔄 Desarrollo y Contribución

### Para Desarrolladores
```bash
# Desarrollo con visualización automática
python autonomous_viewer.py

# Testing completo
python test_apis.py --all --verbose

# Actualización con logs  
python update_data.py --report
```

### Arquitectura Modular
- **Separación de responsabilidades**: UI, datos, configuración
- **Cache inteligente**: Minimiza llamadas API
- **Error handling**: Graceful degradation
- **Documentación**: Código autodocumentado

## 📈 Métricas de Rendimiento

- **Tiempo de carga**: <3 segundos con cache
- **Actualización**: ~30 segundos refresh completo
- **Memoria**: ~150MB para datos 5 años
- **Compatibilidad**: Todos los navegadores modernos

## 🆘 Soporte y Troubleshooting

### Problemas Comunes
1. **Dashboard no carga**: Verificar que Streamlit esté corriendo
2. **Sin datos**: Activar "Usar datos de muestra" en sidebar  
3. **API errors**: Revisar configuración de .env
4. **Performance**: Limpiar caché navegador

### Documentación Adicional
- **Configuración detallada**: `vibe_docs/configuracion_entorno.md`
- **Solución problemas**: `vibe_docs/solucion_problemas.md`  
- **Registro desarrollo**: `vibe_docs/registro_desarrollo.md`

## 📄 Licencia

MIT License - Libre para uso personal y comercial

## 🙏 Créditos

- **Datos**: Bureau of Labor Statistics (BLS) + Federal Reserve Economic Data (FRED)
- **Desarrollo**: Claude Code Assistant
- **Deploy**: Streamlit Cloud
- **Fecha**: Agosto 2025

---

**🌐 Accede al dashboard**: https://dashboard-mercado-laboral-usa-wfypdtffs6ynuajwkibn7q.streamlit.app/

**📊 Dashboard profesional del mercado laboral USA con calendario oficial de publicaciones** ✨