"""
Dashboard Principal - Mercado Laboral USA
Aplicación Streamlit para monitorear indicadores clave del mercado laboral
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Añadir el directorio actual al path para importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *
from data_collector import LaborMarketDataCollector

# Configuración de la página
st.set_page_config(
    page_title=STREAMLIT_CONFIG['page_title'],
    page_icon=STREAMLIT_CONFIG['page_icon'],
    layout=STREAMLIT_CONFIG['layout'],
    initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
)

def get_theme_colors(theme_mode='light'):
    """
    Obtiene la paleta de colores según el tema seleccionado
    """
    return COLOR_PALETTES.get(theme_mode, COLOR_PALETTES['light'])

def apply_custom_css(theme_mode='light'):
    """
    Aplica CSS personalizado según el tema seleccionado
    """
    colors = get_theme_colors(theme_mode)
    
    css = f"""
    <style>
        /* Estilos base del tema */
        .stApp {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}
        
        /* Header principal */
        .main-header {{
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            color: {colors['primary']};
            margin-bottom: 2rem;
        }}
        
        /* Contenedores de métricas */
        .metric-container {{
            background-color: {colors['card_bg']};
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid {colors['primary']};
            margin: 0.5rem 0;
            border: 1px solid {colors['border']};
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* Alertas */
        .alert-high {{
            background-color: {colors['warning']}20;
            border-left-color: {colors['warning']};
        }}
        .alert-warning {{
            background-color: {colors['secondary']}20;
            border-left-color: {colors['secondary']};
        }}
        .alert-good {{
            background-color: {colors['info']}20;
            border-left-color: {colors['info']};
        }}
        
        /* Sidebar personalizado */
        .css-1d391kg {{
            background-color: {colors['sidebar_bg']};
        }}
        
        /* Texto de métricas */
        .metric-container h1, .metric-container h3 {{
            color: {colors['text']};
        }}
        
        /* Toggle de tema */
        .theme-toggle {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background-color: {colors['card_bg']};
            border-radius: 8px;
            border: 1px solid {colors['border']};
            margin: 10px 0;
        }}
        
        /* Contenido de pestañas */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {colors['card_bg']};
        }}
        
        /* Texto general mejorado */
        .markdown-text-container {{
            color: {colors['text']};
        }}
        
        /* Datos de tablas */
        .dataframe {{
            background-color: {colors['card_bg']};
            color: {colors['text']};
        }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def get_plotly_template(theme_mode='light'):
    """
    Obtiene la plantilla de Plotly según el tema
    """
    if theme_mode == 'dark':
        return 'plotly_dark'
    else:
        return 'plotly_white'

def get_theme_chart_colors(theme_mode='light'):
    """
    Obtiene los colores para gráficos según el tema
    """
    colors = get_theme_colors(theme_mode)
    if theme_mode == 'dark':
        return {
            'bg_color': 'rgba(45, 45, 48, 0.8)',
            'paper_bgcolor': colors['card_bg'],
            'plot_bgcolor': colors['chart_bg'],
            'text_color': colors['text'],
            'grid_color': 'rgba(255,255,255,0.1)'
        }
    else:
        return {
            'bg_color': 'rgba(255, 255, 255, 0.8)',
            'paper_bgcolor': colors['card_bg'],
            'plot_bgcolor': colors['chart_bg'],
            'text_color': colors['text'],
            'grid_color': 'rgba(128,128,128,0.2)'
        }

@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_labor_data(force_refresh=False):
    """
    Carga los datos del mercado laboral desde SQLite (fuente única)
    
    Args:
        force_refresh (bool): Forzar actualización desde APIs
    
    Returns:
        dict: Diccionario con todos los DataFrames del mercado laboral
    """
    collector = LaborMarketDataCollector()
    return collector.get_all_labor_data(force_refresh=force_refresh)

def get_database_status():
    """
    Obtiene el estado actual de la base de datos SQLite
    
    Returns:
        dict: Información del estado de la base de datos
    """
    collector = LaborMarketDataCollector()
    return collector.get_database_status()

def create_bullet_chart(title, value, previous_value, theme_mode='light'):
    """
    Crea un gráfico de tipo bullet chart para un KPI.
    """
    theme_colors = get_theme_colors(theme_mode)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        delta = {'reference': previous_value, 'relative': False, 'valueformat': '.2f'},
        title = {'text': title, 'font': {'size': 16, 'color': theme_colors['text']}},
        gauge = {
            'axis': {'range': [None, max(value, previous_value) * 1.2)], 'visible': False},
            'bar': {'color': theme_colors['primary'], 'thickness': 0.7},
            'steps': [
                {'range': [0, previous_value * 0.8], 'color': theme_colors['warning']},
                {'range': [previous_value * 0.8, previous_value * 1.2], 'color': theme_colors['secondary']},
                {'range': [previous_value * 1.2, max(value, previous_value) * 1.5], 'color': theme_colors['success']}
            ],
            'threshold': {
                'line': {'color': theme_colors['text'], 'width': 3},
                'thickness': 0.9,
                'value': previous_value
            }
        },
        number={'font': {'color': theme_colors['text'], 'size': 36}},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(
        height=150,
        paper_bgcolor=theme_colors['card_bg'],
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_sparkline_chart(data, theme_mode='light'):
    """
    Crea un pequeño gráfico de tendencia (sparkline).
    """
    theme_colors = get_theme_colors(theme_mode)
    
    fig = go.Figure(go.Scatter(
        x=data['date'],
        y=data['value'],
        mode='lines',
        line=dict(color=theme_colors['primary'], width=2),
        fill='tozeroy',
        fillcolor=f'{theme_colors["primary"]}33' # Add transparency
    ))
    
    fig.update_layout(
        height=150,
        showlegend=False,
        paper_bgcolor=theme_colors['card_bg'],
        plot_bgcolor=theme_colors['card_bg'],
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig

def create_sunburst_chart(sector_data, theme_mode='light'):
    """
    Crea un gráfico sunburst para la composición del empleo por sector.
    """
    theme_colors = get_theme_colors(theme_mode)
    
    labels = ["Total Empleo Privado"]
    parents = [""]
    values = []

    # Sumar el total de todos los sectores para el padre
    total_employment = sum(df.iloc[-1]['value'] for df in sector_data.values())
    values.append(total_employment)

    for sector, df in sector_data.items():
        labels.append(sector)
        parents.append("Total Empleo Privado")
        values.append(df.iloc[-1]['value'])

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate='<b>%{label} </b> <br> Empleo: %{value:,.0f}K<br> Proporción: %{percentParent:.2%}',
        marker=dict(colors=px.colors.qualitative.Plotly)
    ))

    fig.update_layout(
        title='Composición del Empleo por Sector',
        height=600,
        paper_bgcolor=theme_colors['card_bg'],
        font=dict(color=theme_colors['text'])
    )

    return fig

def create_trend_chart(data, title, y_title, color=COLOR_PALETTE['primary'], theme_mode='light'):
    """
    Crea un gráfico de tendencia con Plotly
    """
    fig = go.Figure()
    
    # Obtener colores del tema
    theme_colors = get_theme_colors(theme_mode)
    chart_colors = get_theme_chart_colors(theme_mode)
    template = get_plotly_template(theme_mode)
    
    # Si no se especifica color, usar el primary del tema
    if color == COLOR_PALETTE['primary']:
        color = theme_colors['primary']
    
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['value'],
        mode='lines+markers',
        line=dict(color=color, width=3),
        marker=dict(size=6, color=color),
        hovertemplate='<b>%{x|%Y-%m}</b><br>' +
                      f'{y_title}: %{{y:.2f}}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': chart_colors['text_color']}
        },
        xaxis_title="Fecha",
        yaxis_title=y_title,
        template=template,
        height=400,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=12, color=chart_colors['text_color']),
        plot_bgcolor=chart_colors['plot_bgcolor'],
        paper_bgcolor=chart_colors['paper_bgcolor']
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=chart_colors['grid_color'])
    fig.update_yaxes(showgrid=True, gridcolor=chart_colors['grid_color'])
    
    return fig

def create_combined_chart(data_dict, theme_mode='light'):
    """
    Crea un gráfico combinado con múltiples métricas
    """
    # Obtener colores del tema
    theme_colors = get_theme_colors(theme_mode)
    chart_colors = get_theme_chart_colors(theme_mode)
    template = get_plotly_template(theme_mode)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Tasa de Desempleo', 'Vacantes de Trabajo', 'Tasa de Renuncias', 'Ratio Vacantes/Desempleo'),
        vertical_spacing=0.12
    )
    
    # Tasa de desempleo
    if 'unemployment_rate' in data_dict:
        fig.add_trace(
            go.Scatter(x=data_dict['unemployment_rate']['date'], 
                      y=data_dict['unemployment_rate']['value'],
                      name='Desempleo (%)',
                      line=dict(color=theme_colors['warning'])),
            row=1, col=1
        )
    
    # Vacantes de trabajo
    if 'job_openings' in data_dict:
        fig.add_trace(
            go.Scatter(x=data_dict['job_openings']['date'], 
                      y=data_dict['job_openings']['value'],
                      name='Vacantes (Miles)',
                      line=dict(color=theme_colors['primary'])),
            row=1, col=2
        )
    
    # Tasa de renuncias
    if 'quits_rate' in data_dict:
        fig.add_trace(
            go.Scatter(x=data_dict['quits_rate']['date'], 
                      y=data_dict['quits_rate']['value'],
                      name='Renuncias (%)',
                      line=dict(color=theme_colors['success'])),
            row=2, col=1
        )
    
    # Ratio vacantes/desempleo
    if 'vacancy_unemployment_ratio' in data_dict:
        fig.add_trace(
            go.Scatter(x=data_dict['vacancy_unemployment_ratio']['date'], 
                      y=data_dict['vacancy_unemployment_ratio']['value'],
                      name='Ratio V/D',
                      line=dict(color=theme_colors['info'])),
            row=2, col=2
        )
    
    fig.update_layout(
        title='Indicadores Clave del Mercado Laboral',
        template=template,
        height=600,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=12, color=chart_colors['text_color']),
        plot_bgcolor=chart_colors['plot_bgcolor'],
        paper_bgcolor=chart_colors['paper_bgcolor']
    )
    
    # Actualizar el color del texto de los subtítulos
    fig.update_annotations(font=dict(color=chart_colors['text_color']))
    
    return fig

def check_alerts(data_dict):
    """
    Verifica alertas basadas en los umbrales configurados
    """
    alerts = []
    
    # Verificar cada métrica contra sus umbrales
    for metric, threshold_key in [
        ('unemployment_rate', 'unemployment_rate_high'),
        ('job_openings', 'job_openings_low'),
        ('quits_rate', 'quits_rate_low'),
        ('layoffs_rate', 'layoffs_rate_high')
    ]:
        if metric in data_dict and not data_dict[metric].empty:
            latest_value = data_dict[metric].iloc[-1]['value']
            threshold = ALERT_THRESHOLDS[threshold_key]
            
            if metric == 'unemployment_rate' and latest_value > threshold:
                alerts.append(f"⚠️ Tasa de desempleo alta: {latest_value:.1f}% (umbral: {threshold}%)")
            elif metric == 'job_openings' and latest_value < threshold:
                alerts.append(f"⚠️ Vacantes bajas: {latest_value:,.0f} (umbral: {threshold:,.0f})")
            elif metric == 'quits_rate' and latest_value < threshold:
                alerts.append(f"⚠️ Confianza laboral baja: {latest_value:.1f}% renuncias (umbral: {threshold}%)")
            elif metric == 'layoffs_rate' and latest_value > threshold:
                alerts.append(f"⚠️ Despidos altos: {latest_value:.1f}% (umbral: {threshold}%)")
    
    return alerts

def create_publication_calendar():
    """
    Crea la pestaña de calendario de publicaciones
    """
    st.markdown("### 📅 Calendario de Publicaciones Oficiales")
    st.markdown("Fechas programadas de publicación de reportes del mercado laboral USA")
    
    # Crear tabs para cada reporte
    report_names = [info['name'] for info in PUBLICATION_CALENDAR.values()]
    calendar_tabs = st.tabs(report_names)
    
    for tab, (report_key, report_info) in zip(calendar_tabs, PUBLICATION_CALENDAR.items()):
        with tab:
            # Header del reporte
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"#### {report_info['name']}")
                st.markdown(f"**Fuente:** {report_info['source']}")
                st.markdown(f"**Descripción:** {report_info['description']}")
            
            with col2:
                st.markdown("**Detalles de Publicación:**")
                st.markdown(f"• **Frecuencia:** {report_info['frequency']}")
                st.markdown(f"• **Horario:** {report_info['time']}")
                st.markdown(f"• **Timing:** {report_info['timing']}")
            
            # Enlaces oficiales
            st.markdown("**Enlaces Oficiales:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"🔗 [Reporte Actual]({report_info['url']})")
            with col2:
                st.markdown(f"📋 [Calendario Oficial]({report_info['schedule_url']})")
            with col3:
                if report_key == 'employment_situation':
                    st.markdown(f"📄 [PDF Actual]({REPORT_LINKS['employment_situation_pdf']})")
                elif report_key == 'jolts':
                    st.markdown(f"📄 [PDF Actual]({REPORT_LINKS['jolts_pdf']})")
            
            # Métricas que incluye este reporte
            st.markdown("**Métricas incluidas en este reporte:**")
            
            metrics_cols = st.columns(len(report_info['metrics']))
            for i, metric in enumerate(report_info['metrics']):
                with metrics_cols[i]:
                    metric_name = UI_LABELS.get(metric, metric)
                    st.markdown(f"• {metric_name}")
            
            # Calendario de fechas programadas
            st.markdown("**📅 Fechas Programadas 2025-2026:**")
            
            # Crear DataFrame para mostrar el calendario
            calendar_data = []
            for release in report_info['release_dates_2025']:
                release_date = datetime.strptime(release['date'], '%Y-%m-%d')
                
                # Determinar si ya pasó la fecha
                is_past = release_date < datetime.now()
                status_icon = "✅" if is_past else "⏳"
                
                # Calcular días hasta la publicación
                days_until = (release_date - datetime.now()).days
                if days_until < 0:
                    time_info = f"Hace {abs(days_until)} días"
                elif days_until == 0:
                    time_info = "HOY"
                elif days_until == 1:
                    time_info = "Mañana"
                else:
                    time_info = f"En {days_until} días"
                
                calendar_data.append({
                    'Fecha de Publicación': release_date.strftime('%Y-%m-%d (%A)'),
                    'Datos para': release['data_for'],
                    'Estado': status_icon,
                    'Tiempo': time_info,
                    'Hora': report_info['time']
                })
            
            # Mostrar tabla del calendario
            if calendar_data:
                calendar_df = pd.DataFrame(calendar_data)
                st.dataframe(calendar_df, use_container_width=True, hide_index=True)
                
                # Destacar próxima fecha
                next_release = None
                for release in report_info['release_dates_2025']:
                    release_date = datetime.strptime(release['date'], '%Y-%m-%d')
                    if release_date >= datetime.now():
                        next_release = release
                        break
                
                if next_release:
                    next_date = datetime.strptime(next_release['date'], '%Y-%m-%d')
                    days_until = (next_date - datetime.now()).days
                    
                    if days_until <= 7:  # Próximas publicaciones en la semana
                        if days_until == 0:
                            st.success(f"🚨 **PUBLICACIÓN HOY**: {next_release['data_for']} a las {report_info['time']}")
                        elif days_until == 1:
                            st.info(f"📢 **PRÓXIMA PUBLICACIÓN MAÑANA**: {next_release['data_for']} a las {report_info['time']}")
                        else:
                            st.info(f"📅 **PRÓXIMA PUBLICACIÓN**: {next_release['data_for']} en {days_until} días ({next_date.strftime('%Y-%m-%d')})")
            
            st.markdown("---")

def create_report_links_section():
    """
    Crea sección con enlaces útiles a reportes y calendarios
    """
    st.markdown("### 🔗 Enlaces Útiles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Fuentes Principales")
        st.markdown(f"🏛️ [Bureau of Labor Statistics]({REPORT_LINKS['bls_main']})")
        st.markdown(f"🏦 [FRED - St. Louis Fed]({REPORT_LINKS['fred_main']})")
        st.markdown(f"📅 [Calendario BLS]({REPORT_LINKS['bls_schedule']})")
    
    with col2:
        st.markdown("#### Reportes Actuales")
        st.markdown(f"💼 [Employment Situation]({REPORT_LINKS['employment_situation_current']})")
        st.markdown(f"🔄 [JOLTS Report]({REPORT_LINKS['jolts_current']})")
        st.markdown(f"📊 [Calendario Económico FRED]({REPORT_LINKS['economic_calendar_fred']})")
    
    with col3:
        st.markdown("#### Documentos PDF")
        st.markdown(f"📄 [Employment Situation PDF]({REPORT_LINKS['employment_situation_pdf']})")
        st.markdown(f"📄 [JOLTS PDF]({REPORT_LINKS['jolts_pdf']})")
        st.markdown("📊 [Todos los PDFs BLS](https://www.bls.gov/schedule/)")

def main():
    """
    Función principal del dashboard
    """
    # Control de tema en sidebar
    st.sidebar.header("⚙️ Configuración")
    
    # Selector de tema
    st.sidebar.markdown("### 🎨 Tema")
    theme_mode = st.sidebar.selectbox(
        "Seleccionar tema:",
        options=["light", "dark"],
        format_func=lambda x: "🌞 Claro" if x == "light" else "🌙 Oscuro",
        index=0,
        key="theme_selector"
    )
    
    # Aplicar CSS según el tema seleccionado
    apply_custom_css(theme_mode)
    
    # Header principal
    st.markdown('<h1 class="main-header">Dashboard Mercado Laboral USA</h1>', 
                unsafe_allow_html=True)
    
    # Control para forzar actualización
    force_refresh = st.sidebar.button("🔄 Actualizar Datos")
    
    # Información sobre las fuentes de datos
    st.sidebar.markdown("### Fuentes de Datos")
    st.sidebar.markdown("- **FRED**: Federal Reserve Economic Data")
    st.sidebar.markdown("- **BLS**: Bureau of Labor Statistics")
    
    # Información de la base de datos
    db_status = get_database_status()
    if 'error' not in db_status:
        st.sidebar.markdown("### Estado de la Base de Datos")
        st.sidebar.markdown(f"**Series disponibles**: {db_status['total_series']}")
        st.sidebar.markdown(f"**Registros totales**: {db_status['total_records']:,}")
        if db_status['last_update']:
            st.sidebar.markdown(f"**Última actualización**: {db_status['last_update'][:16]}")
    
    # Opción para actualización completa
    if st.sidebar.button("🔄 Actualizar desde APIs", help="Obtiene los datos más recientes desde BLS y FRED"):
        force_refresh = True
        st.sidebar.success("Actualización programada")
    else:
        force_refresh = False
    
    # Cargar datos desde SQLite
    with st.spinner("Cargando datos del mercado laboral desde SQLite..."):
        try:
            data_dict = load_labor_data(force_refresh=force_refresh)
            
            if not data_dict:
                st.error("🚨 No hay datos disponibles en la base de datos")
                st.info("🔧 Intentando poblar la base de datos...")
                
                # Intentar poblar la base de datos
                collector = LaborMarketDataCollector()
                collector.refresh_all_data()
                data_dict = load_labor_data()
                
                if not data_dict:
                    st.error("No se pudo poblar la base de datos. Verifica la configuración de APIs.")
                    return
            
            # Determinar fuente de datos
            sample_data_info = ""
            if db_status.get('series_details'):
                sources = [detail[2] for detail in db_status['series_details'] if detail[2]]
                if sources and sources[0] == 'SAMPLE':
                    sample_data_info = " (datos de ejemplo)"
                elif any('FRED' in source or 'BLS' in source for source in sources):
                    sample_data_info = " (datos reales de APIs)"
            
            st.sidebar.success(f"📊 Datos cargados desde SQLite{sample_data_info}")
            
        except Exception as e:
            st.error(f"❌ Error cargando datos: {e}")
            st.info("🔄 Reintentando con actualización completa...")
            
            try:
                data_dict = load_labor_data(force_refresh=True)
                if data_dict:
                    st.sidebar.success("📊 Datos cargados con actualización completa")
                else:
                    st.error("Error crítico: No se pudieron cargar datos")
                    return
            except Exception as e2:
                st.error(f"Error crítico: {e2}")
                return
    
    if not data_dict:
        st.error("No hay datos disponibles para mostrar")
        return
    
    # Verificar alertas
    alerts = check_alerts(data_dict)
    
    # Mostrar alertas si existen
    if alerts:
        st.markdown("### 🚨 Alertas del Sistema")
        for alert in alerts:
            st.warning(alert)
        st.markdown("---")
    
    # KPIs principales
    st.markdown("### 📊 Indicadores Principales")

    kpi_cols = st.columns(4)
    kpi_metrics = [
        ('unemployment_rate', 'Tasa de Desempleo', '{:.1f}%'),
        ('job_openings', 'Vacantes de Trabajo', '{:,.0f}K'),
        ('quits_rate', 'Tasa de Renuncias', '{:.1f}%'),
        ('vacancy_unemployment_ratio', 'Ratio Vacantes/Desempleo', '{:.2f}')
    ]

    for i, (metric, title, value_format) in enumerate(kpi_metrics):
        if metric in data_dict and not data_dict[metric].empty:
            with kpi_cols[i]:
                st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
                
                latest_data = data_dict[metric].iloc[-1]
                previous_data = data_dict[metric].iloc[-2] if len(data_dict[metric]) > 1 else latest_data

                bullet_fig = create_bullet_chart(
                    title="",
                    value=latest_data['value'],
                    previous_value=previous_data['value'],
                    theme_mode=theme_mode
                )
                st.plotly_chart(bullet_fig, use_container_width=True)

                sparkline_fig = create_sparkline_chart(data_dict[metric].tail(12), theme_mode=theme_mode)
                st.plotly_chart(sparkline_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Crear pestañas principales del dashboard
    main_tabs = st.tabs(["📊 Análisis de Datos", "📈 Composición del Empleo", "📅 Calendario de Publicaciones", "🔗 Enlaces Útiles"])
    
    with main_tabs[0]:  # Pestaña de Análisis
        st.markdown("### 📈 Tendencias Históricas")
        
        # Gráfico combinado
        if len(data_dict) >= 2:
            combined_fig = create_combined_chart(data_dict, theme_mode)
            st.plotly_chart(combined_fig, use_container_width=True)
        
        # Gráficos individuales en tabs
        tab_names = []
        tab_data = []
        
        # Obtener colores del tema actual
        theme_colors = get_theme_colors(theme_mode)
        
        metric_configs = [
            ('unemployment_rate', 'Tasa de Desempleo (%)', theme_colors['warning']),
            ('job_openings', 'Vacantes de Trabajo (Miles)', theme_colors['primary']),
            ('quits_rate', 'Tasa de Renuncias (%)', theme_colors['success']),
            ('layoffs_rate', 'Tasa de Despidos (%)', theme_colors['warning']),
            ('labor_force_participation', 'Participación Laboral (%)', theme_colors['info']),
            ('payroll_employment', 'Empleo en Nóminas (Miles)', theme_colors['primary']),
            ('avg_hourly_earnings', 'Salario Promedio/Hora ($)', theme_colors['success'])
        ]
        
        for metric, title, color in metric_configs:
            if metric in data_dict and not data_dict[metric].empty:
                tab_names.append(UI_LABELS.get(metric, title))
                tab_data.append((data_dict[metric], title, color))
        
        if tab_names:
            metric_tabs = st.tabs(tab_names)
            
            for i, (tab, (data, title, color)) in enumerate(zip(metric_tabs, tab_data)):
                with tab:
                    fig = create_trend_chart(data, title, title.split('(')[1].rstrip(')') if '(' in title else title, color, theme_mode)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Mostrar estadísticas básicas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Último Valor", f"{data.iloc[-1]['value']:.2f}")
                    with col2:
                        st.metric("Promedio", f"{data['value'].mean():.2f}")
                    with col3:
                        st.metric("Desv. Estándar", f"{data['value'].std():.2f}")

    with main_tabs[1]: # Pestaña de Composición del Empleo
        st.markdown("### 📈 Composición del Empleo por Sector")
        if 'sector_employment' in data_dict:
            sunburst_fig = create_sunburst_chart(data_dict['sector_employment'], theme_mode)
            st.plotly_chart(sunburst_fig, use_container_width=True)
        else:
            st.warning("No hay datos de empleo por sector disponibles.")

    with main_tabs[2]:  # Pestaña de Calendario
        create_publication_calendar()
    
    with main_tabs[3]:  # Pestaña de Enlaces
        create_report_links_section()
    
    # Footer con información adicional
    st.markdown("---")
    st.markdown("### ℹ️ Información Adicional")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Descripción de Métricas:**")
        for metric, desc in METRIC_DESCRIPTIONS.items():
            if metric in data_dict:
                st.markdown(f"- **{UI_LABELS.get(metric, metric)}**: {desc}")
    
    with col2:
        st.markdown("**Estado del Sistema:**")
        st.markdown(f"- **Última actualización**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown(f"- **Métricas disponibles**: {len(data_dict)}")
        st.markdown(f"- **Período de datos**: {YEARS_OF_DATA} años")
        st.markdown(f"- **Base de datos**: SQLite ({db_status.get('total_records', 0):,} registros)")
        
        # Mostrar información de fuentes de datos
        if db_status.get('series_details'):
            sources = set(detail[2] for detail in db_status['series_details'] if detail[2])
            if sources:
                st.markdown(f"- **Fuentes**: {', '.join(sources)}")

if __name__ == "__main__":
    main()