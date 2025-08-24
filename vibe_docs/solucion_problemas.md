# Guía de Solución de Problemas

## Formato de Registro de Errores
Para cada error, documenta:

### [Error de Codificación Unicode]
**Fecha:** 2025-08-23
**Mensaje de Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 0: character maps to <undefined>
```

**Contexto:** Al ejecutar scripts Python con emojis en Windows con encoding cp1252
**Causa Raíz:** Windows usa codificación cp1252 por defecto que no soporta caracteres Unicode como emojis
**Solución:**
1. Reemplazar todos los emojis por texto equivalente
2. Usar `print("texto")` en lugar de `print("🎉 texto")`
3. Alternativa: Configurar UTF-8 pero puede causar otros problemas

**Prevención:** Evitar emojis en scripts de producción en Windows
**Archivos Relacionados:** test_apis.py

---

## API Keys Requeridas

### [Configuración de FRED API Key]
**Fecha:** 2025-08-23
**Contexto:** Para obtener datos del Federal Reserve Economic Data
**Pasos de configuración:**
1. Ir a https://fred.stlouisfed.org/docs/api/api_key.html
2. Crear cuenta gratuita en FRED
3. Solicitar API key
4. Actualizar .env con `FRED_API_KEY=tu_clave_aqui`

**Estado:** Pendiente - necesita configuración manual del usuario

---

### [Configuración opcional de BLS API Key]  
**Fecha:** 2025-08-23
**Contexto:** Para aumentar límites de la API de Bureau of Labor Statistics
**Pasos:**
1. Ir a https://www.bls.gov/developers/
2. Registrarse para API key (opcional pero recomendado)
3. Actualizar .env con `BLS_API_KEY=tu_clave_aqui`

**Estado:** Opcional - funciona sin key pero con límites

---

### [Puerto 8501 ya en uso]
**Fecha:** 2025-08-23
**Mensaje de Error:**
```
Port 8501 is already in use
```

**Contexto:** Al intentar iniciar el dashboard de Streamlit, el puerto por defecto (8501) ya está siendo utilizado por otra aplicación o una instancia previa de Streamlit.
**Causa Raíz:** Otro proceso está escuchando en el puerto 8501.
**Solución:**
1.  **Identificar y terminar el proceso que usa el puerto:**
    *   **En Windows:**
        *   Abre el Símbolo del sistema (CMD) o PowerShell como **Administrador**.
        *   Ejecuta `netstat -ano | findstr :8501` para encontrar el PID (ID de Proceso) que está usando el puerto 8501.
        *   Una vez que tengas el PID, ejecuta `taskkill /PID <PID> /F` (reemplaza `<PID>` con el número de PID que encontraste).
    *   **En Linux/macOS:**
        *   Abre la terminal.
        *   Ejecuta `lsof -i :8501` para encontrar el PID.
        *   Ejecuta `kill -9 <PID>` (reemplaza `<PID>` con el número de PID que encontraste).
2.  **Iniciar Streamlit en un puerto diferente (alternativa):**
    *   Si no quieres terminar el proceso o no lo encuentras, puedes indicarle a Streamlit que use otro puerto:
        ```bash
        streamlit run dashboard.py --server.port 8502
        ```
        (Puedes usar cualquier otro número de puerto disponible, como 8503, 8504, etc.)

**Prevención:** Asegúrate de cerrar correctamente las instancias de Streamlit cuando termines de usarlas (presionando `Ctrl+C` en la terminal donde se está ejecutando).
**Archivos Relacionados:** dashboard.py

---

### [Error de Formato de Color en Plotly]
**Fecha:** 2025-08-24
**Mensaje de Error:**
```
ValueError: Invalid value of type 'builtins.str' received for the 'fillcolor' property of scatter
Received value: '#1f77b433'

The 'fillcolor' property is a color and may be specified as:
  - A hex string (e.g. '#ff0000')
  - An rgb/rgba string (e.g. 'rgb(255,0,0)')
  - An hsl/hsla string (e.g. 'hsl(0,100%,50%)')
  - An hsv/hsva string (e.g. 'hsv(0,100%,100%)')
  - A named CSS color
```

**Contexto:** Al intentar renderizar gráficos sparkline en el dashboard, función create_sparkline_chart línea 222
**Causa Raíz:** Plotly no acepta colores hex con transparencia concatenada ('33'). El código intenta usar `f'{theme_colors["primary"]}33'` que resulta en '#1f77b433', un formato inválido para Plotly
**Solución:**
1. **Convertir hex a rgba para transparencia:**
   ```python
   # En lugar de: fillcolor=f'{theme_colors["primary"]}33'
   # Usar función de conversión hex a rgba:
   def hex_to_rgba(hex_color, alpha=0.2):
       hex_color = hex_color.lstrip('#')
       r = int(hex_color[0:2], 16)
       g = int(hex_color[2:4], 16)
       b = int(hex_color[4:6], 16)
       return f'rgba({r},{g},{b},{alpha})'
   
   fillcolor=hex_to_rgba(theme_colors["primary"], 0.2)
   ```

2. **Implementar conversión directa:**
   ```python
   # Opción más simple - usar rgba directamente
   primary_rgb = theme_colors["primary_rgb"]  # Definir en config
   fillcolor=f'rgba({primary_rgb[0]},{primary_rgb[1]},{primary_rgb[2]},0.2)'
   ```

**Prevención:** 
- Siempre usar formato rgba() para transparencia en Plotly
- Definir paletas de colores en formatos múltiples (hex, rgb, rgba)
- Probar gráficos después de cambios en el sistema de temas

**Archivos Relacionados:** dashboard.py (línea 222, función create_sparkline_chart), config.py (paletas de colores)

**Estado:** ✅ RESUELTO - Fix implementado el 2025-08-24

---

### [Problema de Legibilidad en Tema Oscuro]
**Fecha:** 2025-08-24
**Mensaje de Error:** "No logro leer bien la información del dashboard" al cambiar entre temas
**Contexto:** Los usuarios reportan problemas de legibilidad al usar el tema oscuro del dashboard
**Causa Raíz:** Los selectores CSS no aplicaban correctamente los colores del tema oscuro definidos en config.py. Los elementos del sidebar y navegación mantenían colores hardcodeados del tema claro, resultando en:
- Ratio de contraste crítico: 1.13:1 (cuando el mínimo es 4.5:1)  
- Texto oscuro `rgb(33, 37, 41)` sobre fondo oscuro `rgb(26, 26, 26)`

**Solución:**
1. **Mejorar selectores CSS en apply_custom_css():**
   ```python
   # Agregar selectores específicos para sidebar
   .css-1d391kg * {
       color: {colors['text']} !important;
   }
   
   # Mejorar selectores de pestañas
   .stTabs [role="tab"][aria-selected="false"] {
       color: {colors['text']} !important;
   }
   
   # Forzar herencia de colores
   .stApp * {
       color: inherit;
   }
   ```

2. **Selectores específicos añadidos para:**
   - Elementos del sidebar (.css-1d391kg)
   - Pestañas activas e inactivas
   - Alertas del sistema
   - Headers y títulos
   - Texto de párrafos y markdown

**Prevención:** 
- Testear ambos temas en cada cambio CSS
- Usar !important solo cuando sea necesario
- Validar ratios de contraste ≥4.5:1 (WCAG 2.1)
- Documentar colores problemáticos en dashboard_issues.md

**Archivos Relacionados:** 
- dashboard.py (función apply_custom_css, líneas 84-185)
- config.py (paletas COLOR_PALETTES - correctamente definidas)
- dashboard_issues.md (análisis detallado de contraste)

**Estado:** ✅ RESUELTO - Mejoras CSS implementadas el 2025-08-24

---

### [Reorganización del Dashboard por Categorías]
**Fecha:** 2025-08-24
**Contexto:** Usuario solicitó eliminar tema claro, establecer tema oscuro como único y reorganizar dashboard por categorías lógicas
**Cambios Implementados:**
1. **Eliminación de sistema dual de temas:**
   - Eliminado `COLOR_PALETTES` y funciones de switching
   - Simplificado a `COLOR_PALETTE` único (tema oscuro)
   - Removido selector de tema del sidebar
   - Limpiadas todas las referencias a `theme_mode`

2. **Nueva organización por categorías:**
   - **Condiciones Generales del Empleo**: Tasa desempleo, empleo en nóminas, participación laboral, vacantes
   - **Dinámica del Mercado Laboral**: Renuncias, despidos, ratio vacantes/desempleo  
   - **Salarios e Inflación**: Salarios promedio, índice costo empleo

3. **Funciones implementadas:**
   - `render_category_metrics()` - Renderiza métricas por categoría con KPIs y sparklines
   - Configuración `DASHBOARD_CATEGORIES` en config.py
   - Pestañas organizadas por categoría lógica

4. **Archivos modificados:**
   - `config.py`: Simplificado colores, agregado DASHBOARD_CATEGORIES
   - `dashboard.py`: Eliminadas funciones de tema dual, nueva estructura
   - Eliminado: `dashboard_issues.md` (documentación redundante)

**Beneficios:**
- Dashboard más limpio y enfocado
- Información organizada lógicamente sin redundancia
- Tema oscuro único optimizado para legibilidad
- Estructura mantenible y extensible

**Archivos Relacionados:** 
- config.py (DASHBOARD_CATEGORIES, COLOR_PALETTE simplificado)
- dashboard.py (nueva estructura main(), render_category_metrics())

**Estado:** ✅ COMPLETADO - Reorganización exitosa el 2025-08-24

---

### [Implementación de Filtros Temporales]
**Fecha:** 2025-08-24
**Contexto:** Usuario solicitó filtros para poder elegir años específicos o meses específicos para análisis más granular
**Funcionalidades Implementadas:**

1. **Sistema completo de filtros temporales:**
   - **Períodos Predefinidos**: Último año, últimos 6 meses, años específicos (2024, 2023), períodos COVID
   - **Por Años Específicos**: Multi-select para seleccionar varios años simultáneamente
   - **Rango de Meses**: Date picker para seleccionar período específico mes a mes
   - **Rango Personalizado**: Selector de fechas completamente personalizable

2. **Funciones de filtrado implementadas:**
   ```python
   # Funciones principales agregadas
   filter_data_by_date(data, filter_type, filter_params)  # Filtrado con validaciones
   apply_date_filters_to_category(category_data, filter_type, filter_params)  # Aplicar a categoría
   get_available_years(data_dict)  # Obtener años disponibles dinámicamente
   get_date_range(data_dict)  # Obtener rango de fechas disponible
   render_date_filters_dynamic(available_years, min_date, max_date)  # UI dinámica
   ```

3. **Integración en todas las categorías:**
   - Filtros aplicados a Condiciones Generales del Empleo
   - Filtros aplicados a Dinámica del Mercado Laboral  
   - Filtros aplicados a Salarios e Inflación
   - Indicadores visuales del filtro activo
   - Conteo de registros disponibles por métrica

4. **Características avanzadas:**
   - **Validaciones robustas**: Manejo de rangos inválidos y datos faltantes
   - **Años dinámicos**: Se obtienen de los datos reales, no hardcodeados
   - **Fallbacks inteligentes**: Si no hay datos en el período, muestra datos completos
   - **Indicadores visuales**: Muestra período activo en cada categoría
   - **Limpieza de filtros**: Botón para resetear a vista completa

5. **Presets configurables:**
   - 📅 Último Año (12 meses)
   - 📆 Últimos 6 Meses  
   - 🗓️ Año 2024/2023 completo
   - 🕰️ Pre-COVID (Jan-Feb 2020)
   - 🦠 Período COVID (Mar 2020-Dec 2021)
   - 📈 Post-COVID (Jan 2022-Presente)

**Beneficios:**
- Análisis temporal granular por año, mes o período personalizado
- Comparación entre diferentes períodos históricos
- Análisis estacional y de tendencias específicas
- Validación automática de datos y rangos
- UI intuitiva con feedback visual

**Archivos Modificados:**
- `config.py`: Agregado FILTER_PRESETS, FILTER_TYPES
- `dashboard.py`: Nuevas funciones de filtrado, integración en todas las categorías
- Todas las visualizaciones actualizadas para usar datos filtrados

**Estado:** ✅ COMPLETADO - Sistema completo de filtros implementado el 2025-08-24

---

### [Rediseño Visual del Dashboard por Métricas]
**Fecha:** 2025-08-24
**Contexto:** Usuario propuso reorganización visual con KPIs principales, navegación por pestañas temáticas, y visualizaciones específicas por métrica
**Implementaciones Realizadas:**

1. **KPI Dashboard Superior:**
   ```python
   # Nueva función render_kpi_dashboard()
   - 4 métricas principales: Desempleo, Variación Nóminas, Vacantes, Salarios
   - Indicadores de salud visual: 🟢🟡🔴 basados en umbrales
   - Indicadores de tendencia: ↗️↘️➡️ 
   - Formato inteligente por tipo de métrica
   - Contexto de salud: "Nivel saludable", "Nivel preocupante", etc.
   ```

2. **Navegación por Pestañas Temáticas:**
   - 🏥 **Salud General**: Desempleo + Participación Laboral
   - 🏗️ **Creación de Empleo**: Nóminas + Vacantes + Ratios
   - 🔄 **Dinámica Laboral**: Renuncias + Despidos + Flujos JOLTS
   - 💰 **Compensación**: Salarios + Índice Costo Empleo
   - 📅 **Calendario**: Fechas de publicación
   - 🔗 **Enlaces**: Recursos útiles

3. **Visualizaciones Mejoradas:**
   ```python
   # Nuevas funciones de gráficos
   create_enhanced_line_chart()       # Líneas con anotaciones y eventos
   create_bar_chart_with_comparison() # Barras MoM/YoY con colores condicionales  
   create_dual_axis_chart()          # Doble eje para métricas relacionadas
   create_jolts_flow_chart()         # Flujos combinados de entrada/salida
   ```

4. **Características Avanzadas:**
   - **Líneas de referencia**: Promedios históricos en cada gráfico
   - **Períodos sombreados**: COVID, recesiones visualmente marcadas
   - **Tooltips informativos**: Contexto detallado en hover
   - **Colores condicionales**: Verde/rojo basado en dirección del cambio
   - **Interactividad Plotly**: Zoom, pan, hover mejorados

5. **Indicadores de Salud Visual:**
   ```python
   # Sistema de umbrales por métrica
   health_rules = {
       'unemployment_rate': {'good_threshold': 4.0, 'bad_threshold': 6.0},
       'job_openings': {'good_threshold': 8M, 'bad_threshold': 6M},
       'payroll_employment': {'good_threshold': 150K, 'bad_threshold': 50K}
   }
   # Resultado: 🟢 Saludable, 🟡 Moderado, 🔴 Preocupante
   ```

6. **Integración con Filtros Existentes:**
   - KPIs se ajustan según filtros temporales aplicados
   - Gráficos mejorados respetan rangos de fechas
   - Indicadores de "filtro activo" en cada sección
   - Validaciones de datos insuficientes

**Estructura Implementada (Primera Pestaña Completa):**
```python
# 🏥 Salud General - Completamente implementada
- Gráfico dual: Desempleo vs Participación (ejes separados)
- Gráfico individual Desempleo con eventos COVID
- Gráfico individual Participación con promedios históricos
- Filtros temporales aplicados a ambas métricas
```

**Beneficios del Rediseño:**
- **Dashboard más profesional** con KPIs prominentes
- **Navegación intuitiva** por categorías temáticas 
- **Visualizaciones apropiadas** para cada tipo de métrica
- **Interactividad Plotly** mejorada con contexto
- **Indicadores de salud** para interpretación rápida
- **Compatibilidad completa** con sistema de filtros existente

**Archivos Modificados:**
- `dashboard.py`: Nuevas funciones de visualización, KPI dashboard, navegación temática
- Integración completa con filtros temporales implementados anteriormente

**Estado:** 🚧 EN PROGRESO - Primera pestaña completamente implementada, estructura base para las demás pestañas establecida el 2025-08-24

---