"""
Dashboard Principal - Mercado Laboral USA
Aplicación Streamlit para monitorear indicadores clave del mercado laboral
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
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

# CSS personalizado para mejorar el aspecto
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .alert-high {
        background-color: #f8d7da;
        border-left-color: #dc3545;
    }
    .alert-warning {
        background-color: #fff3cd;
        border-left-color: #ffc107;
    }
    .alert-good {
        background-color: #d1edff;
        border-left-color: #0dcaf0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_labor_data():
    """
    Carga los datos del mercado laboral con caché
    """
    collector = LaborMarketDataCollector()
    return collector.get_all_labor_data()

@st.cache_data
def generate_sample_data():
    """
    Genera datos de muestra para demostración cuando las APIs no están disponibles
    """
    # Crear fechas mensuales para los últimos 5 años
    dates = pd.date_range(start='2020-01-01', end='2025-08-01', freq='MS')
    
    sample_data = {}
    
    # Tasa de desempleo (3-6%)
    unemployment_trend = 4.5 + 1.5 * np.sin(np.linspace(0, 4*np.pi, len(dates))) + np.random.normal(0, 0.2, len(dates))
    unemployment_trend = np.clip(unemployment_trend, 3.0, 6.5)
    sample_data['unemployment_rate'] = pd.DataFrame({
        'date': dates,
        'value': unemployment_trend
    })
    
    # Vacantes de trabajo (8-12 millones)
    job_openings_trend = 10000 + 2000 * np.cos(np.linspace(0, 3*np.pi, len(dates))) + np.random.normal(0, 500, len(dates))
    job_openings_trend = np.clip(job_openings_trend, 7000, 13000)
    sample_data['job_openings'] = pd.DataFrame({
        'date': dates,
        'value': job_openings_trend
    })
    
    # Tasa de renuncias (2-4%)
    quits_trend = 3.0 + 0.8 * np.cos(np.linspace(0, 2*np.pi, len(dates))) + np.random.normal(0, 0.1, len(dates))
    quits_trend = np.clip(quits_trend, 1.8, 4.2)
    sample_data['quits_rate'] = pd.DataFrame({
        'date': dates,
        'value': quits_trend
    })
    
    # Tasa de despidos (1-2%)
    layoffs_trend = 1.4 + 0.3 * np.sin(np.linspace(0, 3*np.pi, len(dates))) + np.random.normal(0, 0.1, len(dates))
    layoffs_trend = np.clip(layoffs_trend, 1.0, 2.0)
    sample_data['layoffs_rate'] = pd.DataFrame({
        'date': dates,
        'value': layoffs_trend
    })
    
    # Participación laboral (62-64%)
    participation_trend = 63.0 + 0.5 * np.cos(np.linspace(0, np.pi, len(dates))) + np.random.normal(0, 0.1, len(dates))
    sample_data['labor_force_participation'] = pd.DataFrame({
        'date': dates,
        'value': participation_trend
    })
    
    # Empleo en nóminas (140-155 millones)
    payroll_trend = 150000 + 5000 * np.linspace(-1, 1, len(dates)) + np.random.normal(0, 1000, len(dates))
    sample_data['payroll_employment'] = pd.DataFrame({
        'date': dates,
        'value': payroll_trend
    })
    
    # Salario promedio por hora ($25-35)
    wage_trend = 30 + 2 * np.linspace(-0.5, 1.5, len(dates)) + np.random.normal(0, 0.5, len(dates))
    sample_data['avg_hourly_earnings'] = pd.DataFrame({
        'date': dates,
        'value': wage_trend
    })
    
    # Ratio vacantes/desempleo
    if 'job_openings' in sample_data and 'unemployment_rate' in sample_data:
        ratio_values = (sample_data['job_openings']['value'] / 1000) / sample_data['unemployment_rate']['value']
        sample_data['vacancy_unemployment_ratio'] = pd.DataFrame({
            'date': dates,
            'value': ratio_values
        })
    
    return sample_data

def create_kpi_card(title, value, delta=None, delta_color="normal"):
    """
    Crea una tarjeta KPI personalizada
    """
    if delta is not None:
        delta_str = f"**{delta:+.1f}%** desde el mes anterior"
        delta_color_map = {"normal": "🔵", "good": "🟢", "bad": "🔴"}
        color_icon = delta_color_map.get(delta_color, "🔵")
    else:
        delta_str = ""
        color_icon = ""
    
    st.markdown(f"""
    <div class="metric-container">
        <h3>{title}</h3>
        <h1>{value}</h1>
        <p>{color_icon} {delta_str}</p>
    </div>
    """, unsafe_allow_html=True)

def create_trend_chart(data, title, y_title, color=COLOR_PALETTE['primary']):
    """
    Crea un gráfico de tendencia con Plotly
    """
    fig = go.Figure()
    
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
            'font': {'size': 18, 'color': COLOR_PALETTE['text']}
        },
        xaxis_title="Fecha",
        yaxis_title=y_title,
        template='plotly_white',
        height=400,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
    
    return fig

def create_combined_chart(data_dict):
    """
    Crea un gráfico combinado con múltiples métricas
    """
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
                      line=dict(color=COLOR_PALETTE['warning'])),
            row=1, col=1
        )
    
    # Vacantes de trabajo
    if 'job_openings' in data_dict:
        fig.add_trace(
            go.Scatter(x=data_dict['job_openings']['date'], 
                      y=data_dict['job_openings']['value'],
                      name='Vacantes (Miles)',
                      line=dict(color=COLOR_PALETTE['primary'])),
            row=1, col=2
        )
    
    # Tasa de renuncias
    if 'quits_rate' in data_dict:
        fig.add_trace(
            go.Scatter(x=data_dict['quits_rate']['date'], 
                      y=data_dict['quits_rate']['value'],
                      name='Renuncias (%)',
                      line=dict(color=COLOR_PALETTE['success'])),
            row=2, col=1
        )
    
    # Ratio vacantes/desempleo
    if 'vacancy_unemployment_ratio' in data_dict:
        fig.add_trace(
            go.Scatter(x=data_dict['vacancy_unemployment_ratio']['date'], 
                      y=data_dict['vacancy_unemployment_ratio']['value'],
                      name='Ratio V/D',
                      line=dict(color=COLOR_PALETTE['info'])),
            row=2, col=2
        )
    
    fig.update_layout(
        title='Indicadores Clave del Mercado Laboral',
        template='plotly_white',
        height=600,
        showlegend=False,
        font=dict(family="Arial, sans-serif", size=12)
    )
    
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
    # Header principal
    st.markdown('<h1 class="main-header">Dashboard Mercado Laboral USA</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar para controles
    st.sidebar.header("Configuración")
    
    # Control para forzar actualización
    force_refresh = st.sidebar.button("🔄 Actualizar Datos")
    
    # Información sobre las fuentes de datos
    st.sidebar.markdown("### Fuentes de Datos")
    st.sidebar.markdown("- **FRED**: Federal Reserve Economic Data")
    st.sidebar.markdown("- **BLS**: Bureau of Labor Statistics")
    
    # Selector de modo de datos
    use_sample_data = st.sidebar.checkbox("Usar datos de muestra", value=True, 
                                         help="Activa para usar datos simulados en lugar de APIs reales")
    
    # Cargar datos
    with st.spinner("Cargando datos del mercado laboral..."):
        try:
            if use_sample_data:
                data_dict = generate_sample_data()
                st.sidebar.success("Usando datos de muestra para demostración")
            else:
                data_dict = load_labor_data()
                if not data_dict:
                    st.error("No se pudieron cargar datos de las APIs. Verifica la configuración.")
                    return
                st.sidebar.success("Datos cargados desde APIs")
        except Exception as e:
            st.error(f"Error cargando datos: {e}")
            st.info("Usando datos de muestra como respaldo...")
            data_dict = generate_sample_data()
    
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
    
    # KPI 1: Tasa de Desempleo
    if 'unemployment_rate' in data_dict and not data_dict['unemployment_rate'].empty:
        latest_unemployment = data_dict['unemployment_rate'].iloc[-1]
        prev_unemployment = data_dict['unemployment_rate'].iloc[-2] if len(data_dict['unemployment_rate']) > 1 else None
        delta_unemployment = ((latest_unemployment['value'] - prev_unemployment['value']) / prev_unemployment['value'] * 100) if prev_unemployment is not None else None
        
        with kpi_cols[0]:
            create_kpi_card(
                "Tasa de Desempleo",
                f"{latest_unemployment['value']:.1f}%",
                delta_unemployment,
                "bad" if delta_unemployment and delta_unemployment > 0 else "good"
            )
    
    # KPI 2: Vacantes de Trabajo
    if 'job_openings' in data_dict and not data_dict['job_openings'].empty:
        latest_openings = data_dict['job_openings'].iloc[-1]
        with kpi_cols[1]:
            create_kpi_card(
                "Vacantes de Trabajo",
                f"{latest_openings['value']:,.0f}K"
            )
    
    # KPI 3: Tasa de Renuncias
    if 'quits_rate' in data_dict and not data_dict['quits_rate'].empty:
        latest_quits = data_dict['quits_rate'].iloc[-1]
        with kpi_cols[2]:
            create_kpi_card(
                "Tasa de Renuncias",
                f"{latest_quits['value']:.1f}%"
            )
    
    # KPI 4: Ratio Vacantes/Desempleo
    if 'vacancy_unemployment_ratio' in data_dict and not data_dict['vacancy_unemployment_ratio'].empty:
        latest_ratio = data_dict['vacancy_unemployment_ratio'].iloc[-1]
        with kpi_cols[3]:
            create_kpi_card(
                "Ratio Vacantes/Desempleo",
                f"{latest_ratio['value']:.2f}"
            )
    
    st.markdown("---")
    
    # Crear pestañas principales del dashboard
    main_tabs = st.tabs(["📊 Análisis de Datos", "📅 Calendario de Publicaciones", "🔗 Enlaces Útiles"])
    
    with main_tabs[0]:  # Pestaña de Análisis
        st.markdown("### 📈 Tendencias Históricas")
        
        # Gráfico combinado
        if len(data_dict) >= 2:
            combined_fig = create_combined_chart(data_dict)
            st.plotly_chart(combined_fig, use_container_width=True)
        
        # Gráficos individuales en tabs
        tab_names = []
        tab_data = []
        
        metric_configs = [
            ('unemployment_rate', 'Tasa de Desempleo (%)', COLOR_PALETTE['warning']),
            ('job_openings', 'Vacantes de Trabajo (Miles)', COLOR_PALETTE['primary']),
            ('quits_rate', 'Tasa de Renuncias (%)', COLOR_PALETTE['success']),
            ('layoffs_rate', 'Tasa de Despidos (%)', COLOR_PALETTE['warning']),
            ('labor_force_participation', 'Participación Laboral (%)', COLOR_PALETTE['info']),
            ('payroll_employment', 'Empleo en Nóminas (Miles)', COLOR_PALETTE['primary']),
            ('avg_hourly_earnings', 'Salario Promedio/Hora ($)', COLOR_PALETTE['success'])
        ]
        
        for metric, title, color in metric_configs:
            if metric in data_dict and not data_dict[metric].empty:
                tab_names.append(UI_LABELS.get(metric, title))
                tab_data.append((data_dict[metric], title, color))
        
        if tab_names:
            metric_tabs = st.tabs(tab_names)
            
            for i, (tab, (data, title, color)) in enumerate(zip(metric_tabs, tab_data)):
                with tab:
                    fig = create_trend_chart(data, title, title.split('(')[1].rstrip(')') if '(' in title else title, color)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Mostrar estadísticas básicas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Último Valor", f"{data.iloc[-1]['value']:.2f}")
                    with col2:
                        st.metric("Promedio", f"{data['value'].mean():.2f}")
                    with col3:
                        st.metric("Desv. Estándar", f"{data['value'].std():.2f}")
    
    with main_tabs[1]:  # Pestaña de Calendario
        create_publication_calendar()
    
    with main_tabs[2]:  # Pestaña de Enlaces
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
        st.markdown(f"- **Fuente**: {'Datos de muestra' if use_sample_data else 'APIs en vivo'}")

if __name__ == "__main__":
    main()