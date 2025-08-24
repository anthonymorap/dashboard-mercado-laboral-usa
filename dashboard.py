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
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(
    page_title=STREAMLIT_CONFIG['page_title'],
    page_icon=STREAMLIT_CONFIG['page_icon'],
    layout=STREAMLIT_CONFIG['layout'],
    initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
)

def get_colors():
    """
    Obtiene la paleta de colores del tema oscuro único
    """
    return COLOR_PALETTE

def apply_custom_css():
    """
    Aplica CSS personalizado para tema oscuro único
    """
    colors = get_colors()
    
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
            color: {colors['text']};
        }}
        
        /* Texto del sidebar - elementos específicos */
        .css-1d391kg .css-10trblm {{
            color: {colors['text']} !important;
        }}
        
        .css-1d391kg h3, .css-1d391kg h2, .css-1d391kg h1 {{
            color: {colors['text']} !important;
        }}
        
        .css-1d391kg .css-1629p8f {{
            color: {colors['text']} !important;
        }}
        
        .css-1d391kg .stMarkdown {{
            color: {colors['text']} !important;
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
        
        .stTabs [data-baseweb="tab"] {{
            color: {colors['text']} !important;
        }}
        
        /* Texto de pestañas activas e inactivas */
        .stTabs [role="tab"][aria-selected="true"] {{
            color: {colors['primary']} !important;
        }}
        
        .stTabs [role="tab"][aria-selected="false"] {{
            color: {colors['text']} !important;
        }}
        
        /* Texto general mejorado */
        .markdown-text-container {{
            color: {colors['text']};
        }}
        
        /* Elementos de texto específicos de Streamlit */
        .css-10trblm, .css-1629p8f {{
            color: {colors['text']} !important;
        }}
        
        /* Headers y títulos */
        h1, h2, h3, h4, h5, h6 {{
            color: {colors['text']} !important;
        }}
        
        /* Texto de párrafos y elementos markdown */
        p, span, div {{
            color: {colors['text']};
        }}
        
        /* Datos de tablas */
        .dataframe {{
            background-color: {colors['card_bg']};
            color: {colors['text']};
        }}
        
        /* Correcciones espec\u00edficas para alertas */
        .stAlert {{
            color: {colors['text']} !important;
        }}
        
        /* Forzar colores en todos los elementos de texto */
        .stApp * {{
            color: inherit;
        }}
        
        /* Sidebar - selectores m\u00e1s espec\u00edficos */
        .css-1d391kg * {{
            color: {colors['text']} !important;
        }}
        
        /* Contenedor principal de la app */
        .main .block-container {{
            color: {colors['text']};
        }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def get_plotly_template():
    """
    Obtiene la plantilla de Plotly para tema oscuro
    """
    return 'plotly_dark'

def hex_to_rgba(hex_color, alpha=0.2):
    """
    Convierte color hexadecimal a formato rgba con transparencia
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16) 
    b = int(hex_color[4:6], 16)
    return f'rgba({r},{g},{b},{alpha})'

def get_chart_colors():
    """
    Obtiene los colores para gráficos
    """
    colors = get_colors()
    return {
        'bg_color': 'rgba(45, 45, 48, 0.8)',
        'paper_bgcolor': colors['card_bg'],
        'plot_bgcolor': colors['chart_bg'],
        'text_color': colors['text'],
        'grid_color': 'rgba(255,255,255,0.1)'
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

def create_bullet_chart(title, value, previous_value):
    """
    Crea un gráfico de tipo bullet chart para un KPI.
    """
    theme_colors = get_colors()
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        delta = {'reference': previous_value, 'relative': False, 'valueformat': '.2f'},
        title = {'text': title, 'font': {'size': 16, 'color': theme_colors['text']}},
        gauge = {
            'axis': {'range': [None, max(value, previous_value) * 1.2], 'visible': False},
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

def create_sparkline_chart(data):
    """
    Crea un pequeño gráfico de tendencia (sparkline).
    """
    theme_colors = get_colors()
    
    fig = go.Figure(go.Scatter(
        x=data['date'],
        y=data['value'],
        mode='lines',
        line=dict(color=theme_colors['primary'], width=2),
        fill='tozeroy',
        fillcolor=hex_to_rgba(theme_colors["primary"], 0.2)  # Add transparency
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

def create_sunburst_chart(sector_data):
    """
    Crea un gráfico sunburst para la composición del empleo por sector.
    """
    theme_colors = get_colors()
    
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

def create_trend_chart(data, title, y_title, color=COLOR_PALETTE['primary']):
    """
    Crea un gráfico de tendencia con Plotly
    """
    fig = go.Figure()
    
    # Obtener colores del tema
    theme_colors = get_colors()
    chart_colors = get_chart_colors()
    template = get_plotly_template()
    
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

def create_combined_chart(data_dict, title_suffix=""):
    """
    Crea un gráfico combinado con múltiples métricas
    """
    # Obtener colores del tema
    theme_colors = get_colors()
    chart_colors = get_chart_colors()
    template = get_plotly_template()
    
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
        title=f'Indicadores Clave del Mercado Laboral{title_suffix}',
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

def filter_data_by_date(data, filter_type, filter_params):
    """
    Filtra datos por diferentes criterios temporales con validaciones
    """
    if data is None or len(data) == 0:
        return data
    
    # Asegurar que date es datetime
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date')
    
    try:
        if filter_type == 'preset':
            preset_key = filter_params.get('preset_key')
            if preset_key in FILTER_PRESETS:
                preset = FILTER_PRESETS[preset_key]
                
                if 'months' in preset:
                    # Filtrar por últimos N meses
                    months_back = preset['months']
                    cutoff_date = data['date'].max() - pd.DateOffset(months=months_back)
                    filtered = data[data['date'] >= cutoff_date]
                    return filtered if len(filtered) > 0 else data.tail(1)  # Al menos 1 registro
                
                elif 'year' in preset:
                    # Filtrar por año específico
                    year = preset['year']
                    filtered = data[data['date'].dt.year == year]
                    return filtered if len(filtered) > 0 else data  # Si no hay datos del año, devolver todo
                
                elif 'start_date' in preset:
                    # Filtrar por rango de fechas
                    start_date = pd.to_datetime(preset['start_date'])
                    end_date = pd.to_datetime(preset['end_date']) if preset['end_date'] else data['date'].max()
                    filtered = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
                    return filtered if len(filtered) > 0 else data  # Si no hay datos, devolver todo
        
        elif filter_type == 'years':
            # Filtrar por años específicos
            years = filter_params.get('years', [])
            if years:
                filtered = data[data['date'].dt.year.isin(years)]
                return filtered if len(filtered) > 0 else data  # Si no hay datos, devolver todo
        
        elif filter_type in ['months', 'custom']:
            # Filtrar por rango de fechas
            start_date = pd.to_datetime(filter_params.get('start_date'))
            end_date = pd.to_datetime(filter_params.get('end_date'))
            
            # Validar que el rango sea válido
            if start_date > end_date:
                return data  # Rango inválido, devolver datos completos
                
            filtered = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
            return filtered if len(filtered) > 0 else data  # Si no hay datos, devolver todo
        
    except Exception as e:
        # Si hay cualquier error en el filtrado, devolver datos originales
        st.warning(f"Error aplicando filtro: {e}. Mostrando datos completos.")
        return data
    
    return data

def apply_date_filters_to_category(category_data, filter_type, filter_params):
    """
    Aplica filtros de fecha a todas las métricas de una categoría
    """
    filtered_data = {}
    for metric, data in category_data.items():
        if data is not None:
            filtered_data[metric] = filter_data_by_date(data, filter_type, filter_params)
        else:
            filtered_data[metric] = data
    return filtered_data

def get_available_years(data_dict):
    """
    Obtiene los años disponibles en los datos
    """
    years = set()
    for metric_data in data_dict.values():
        if metric_data is not None and 'date' in metric_data.columns:
            metric_data['date'] = pd.to_datetime(metric_data['date'])
            years.update(metric_data['date'].dt.year.unique())
    return sorted(years)

def get_date_range(data_dict):
    """
    Obtiene el rango de fechas disponible en los datos
    """
    min_date = None
    max_date = None
    
    for metric_data in data_dict.values():
        if metric_data is not None and 'date' in metric_data.columns:
            metric_data['date'] = pd.to_datetime(metric_data['date'])
            if min_date is None or metric_data['date'].min() < min_date:
                min_date = metric_data['date'].min()
            if max_date is None or metric_data['date'].max() > max_date:
                max_date = metric_data['date'].max()
    
    return min_date, max_date

def render_date_filters_dynamic(available_years, min_date, max_date):
    """
    Renderiza los controles de filtro de fecha en el sidebar con datos dinámicos
    """
    st.sidebar.markdown("### 📅 Filtros Temporales")
    
    # Mostrar rango de datos disponibles
    if min_date and max_date:
        st.sidebar.caption(f"📊 Datos disponibles: {min_date.strftime('%Y-%m')} a {max_date.strftime('%Y-%m')}")
    
    # Tipo de filtro
    filter_type = st.sidebar.selectbox(
        "Tipo de filtro:",
        options=list(FILTER_TYPES.keys()),
        format_func=lambda x: FILTER_TYPES[x],
        key="filter_type"
    )
    
    filter_params = {}
    
    if filter_type == 'preset':
        preset_key = st.sidebar.selectbox(
            "Período:",
            options=list(FILTER_PRESETS.keys()),
            format_func=lambda x: FILTER_PRESETS[x]['name'],
            help="Selecciona un período predefinido",
            key="preset_key"
        )
        filter_params['preset_key'] = preset_key
        
        # Mostrar descripción del preset
        if preset_key in FILTER_PRESETS:
            st.sidebar.info(FILTER_PRESETS[preset_key]['description'])
    
    elif filter_type == 'years':
        selected_years = st.sidebar.multiselect(
            "Selecciona años:",
            options=available_years,
            default=[available_years[-1]] if available_years else [2024],
            help="Puedes seleccionar múltiples años",
            key="selected_years"
        )
        filter_params['years'] = selected_years
        
        if selected_years:
            years_str = ', '.join(map(str, selected_years))
            st.sidebar.success(f"Analizando años: {years_str}")
    
    elif filter_type == 'months':
        col1, col2 = st.sidebar.columns(2)
        
        # Establecer valores por defecto basados en datos disponibles
        default_start = min_date if min_date else datetime(2024, 1, 1) 
        default_end = max_date if max_date else datetime.now()
        
        with col1:
            start_date = st.date_input(
                "Desde:",
                value=default_start.date() if hasattr(default_start, 'date') else default_start,
                min_value=min_date.date() if min_date else datetime(2020, 1, 1).date(),
                max_value=max_date.date() if max_date else datetime.now().date(),
                key="month_start_date"
            )
        with col2:
            end_date = st.date_input(
                "Hasta:",
                value=default_end.date() if hasattr(default_end, 'date') else default_end,
                min_value=min_date.date() if min_date else datetime(2020, 1, 1).date(),
                max_value=max_date.date() if max_date else datetime.now().date(),
                key="month_end_date"
            )
        filter_params['start_date'] = start_date
        filter_params['end_date'] = end_date
        
        # Validar fechas
        if start_date > end_date:
            st.sidebar.error("❌ La fecha de inicio debe ser anterior a la fecha de fin")
    
    elif filter_type == 'custom':
        col1, col2 = st.sidebar.columns(2)
        
        # Establecer valores por defecto basados en datos disponibles
        default_start = min_date if min_date else datetime(2023, 1, 1)
        default_end = max_date if max_date else datetime.now()
        
        with col1:
            start_date = st.date_input(
                "Fecha inicio:",
                value=default_start.date() if hasattr(default_start, 'date') else default_start,
                min_value=min_date.date() if min_date else datetime(2020, 1, 1).date(),
                max_value=max_date.date() if max_date else datetime.now().date(),
                key="custom_start_date"
            )
        with col2:
            end_date = st.date_input(
                "Fecha fin:",
                value=default_end.date() if hasattr(default_end, 'date') else default_end,
                min_value=min_date.date() if min_date else datetime(2020, 1, 1).date(),
                max_value=max_date.date() if max_date else datetime.now().date(),
                key="custom_end_date"
            )
        filter_params['start_date'] = start_date
        filter_params['end_date'] = end_date
        
        # Validar fechas
        if start_date > end_date:
            st.sidebar.error("❌ La fecha de inicio debe ser anterior a la fecha de fin")
    
    # Botón para limpiar filtros
    if st.sidebar.button("🔄 Limpiar Filtros"):
        # Limpiar session state de filtros
        for key in list(st.session_state.keys()):
            if key.startswith(('filter_', 'preset_', 'selected_', 'month_', 'custom_')):
                del st.session_state[key]
        st.rerun()
    
    return filter_type, filter_params

def render_category_metrics(category_key, data_dict, filter_type=None, filter_params=None):
    """
    Renderiza las métricas de una categoría específica con filtros aplicados
    """
    category = DASHBOARD_CATEGORIES[category_key]
    colors = get_colors()
    
    st.markdown(f"## {category['title']}")
    st.markdown(f"*{category['description']}*")
    
    # Aplicar filtros si están definidos
    if filter_type and filter_params:
        # Filtrar solo las métricas de esta categoría
        category_data = {k: v for k, v in data_dict.items() if k in category['metrics']}
        filtered_data = apply_date_filters_to_category(category_data, filter_type, filter_params)
        
        # Mostrar información del filtro aplicado
        if filter_type == 'preset' and filter_params.get('preset_key'):
            preset = FILTER_PRESETS[filter_params['preset_key']]
            st.info(f"📅 Filtro activo: {preset['name']}")
        elif filter_type == 'years':
            years_str = ', '.join(map(str, filter_params.get('years', [])))
            st.info(f"📅 Filtro activo: Años {years_str}")
        elif filter_type in ['months', 'custom']:
            start_date = filter_params.get('start_date')
            end_date = filter_params.get('end_date')
            st.info(f"📅 Filtro activo: {start_date} a {end_date}")
    else:
        filtered_data = {k: v for k, v in data_dict.items() if k in category['metrics']}
    
    # Crear columnas para las métricas de la categoría
    metrics_available = [metric for metric in category['metrics'] if metric in filtered_data and filtered_data[metric] is not None and len(filtered_data[metric]) > 0]
    
    if not metrics_available:
        st.warning(f"No hay datos disponibles para la categoría {category['title']} en el período seleccionado")
        return filtered_data  # Retornar para uso en gráficos combinados
    
    cols = st.columns(len(metrics_available))
    
    for idx, metric in enumerate(metrics_available):
        with cols[idx]:
            data = filtered_data[metric]
            if data is not None and len(data) > 0:
                current_value = data.iloc[-1]['value']
                previous_value = data.iloc[-2]['value'] if len(data) > 1 else current_value
                delta = current_value - previous_value
                
                # Formatear valores según el tipo de métrica
                if 'rate' in metric or 'unemployment' in metric or 'participation' in metric:
                    value_str = f"{current_value:.1f}%"
                    delta_str = f"{delta:+.2f}" if delta != 0 else "0.00"
                elif 'earnings' in metric:
                    value_str = f"${current_value:.2f}"
                    delta_str = f"${delta:+.2f}" if delta != 0 else "$0.00"
                elif metric == 'job_openings':
                    value_str = f"{current_value/1000:.0f}K"
                    delta_str = f"{delta/1000:+.0f}K" if delta != 0 else "0K"
                else:
                    value_str = f"{current_value:,.0f}"
                    delta_str = f"{delta:+,.0f}" if delta != 0 else "0"
                
                # Mostrar métrica
                st.metric(
                    label=UI_LABELS[metric],
                    value=value_str,
                    delta=delta_str
                )
                
                # Mostrar sparkline con datos filtrados (máximo 12 puntos)
                sparkline_data = data.tail(12) if len(data) >= 12 else data
                sparkline_fig = create_sparkline_chart(sparkline_data)
                st.plotly_chart(sparkline_fig, use_container_width=True)
                
                # Mostrar conteo de datos disponibles
                st.caption(f"📊 {len(data)} registros disponibles")
            else:
                st.error(f"No hay datos para {UI_LABELS[metric]} en el período seleccionado")
    
    return filtered_data

def get_metric_health_indicator(metric, current_value, delta):
    """
    Determina el indicador de salud para una métrica específica
    """
    health_rules = {
        'unemployment_rate': {
            'good_threshold': 4.0,
            'bad_threshold': 6.0,
            'lower_is_better': True
        },
        'job_openings': {
            'good_threshold': 8000000,
            'bad_threshold': 6000000,
            'lower_is_better': False
        },
        'quits_rate': {
            'good_threshold': 2.3,
            'bad_threshold': 1.8,
            'lower_is_better': False
        },
        'avg_hourly_earnings': {
            'good_threshold': 3.0,  # % growth
            'bad_threshold': 1.5,
            'lower_is_better': False
        },
        'payroll_employment': {
            'good_threshold': 150000,  # monthly change
            'bad_threshold': 50000,
            'lower_is_better': False
        }
    }
    
    if metric not in health_rules:
        return "⚪", "neutral"  # Sin regla definida
    
    rule = health_rules[metric]
    
    if rule['lower_is_better']:
        if current_value <= rule['good_threshold']:
            return "🟢", "good"
        elif current_value >= rule['bad_threshold']:
            return "🔴", "bad"
        else:
            return "🟡", "warning"
    else:
        if current_value >= rule['good_threshold']:
            return "🟢", "good"
        elif current_value <= rule['bad_threshold']:
            return "🔴", "bad"
        else:
            return "🟡", "warning"

def get_trend_indicator(delta):
    """
    Obtiene indicador visual de tendencia basado en el delta
    """
    if delta > 0:
        return "↗️"
    elif delta < 0:
        return "↘️"
    else:
        return "➡️"

def render_kpi_dashboard(data_dict, filter_type=None, filter_params=None):
    """
    Renderiza KPIs principales en la parte superior del dashboard
    """
    st.markdown("## 📊 Indicadores Clave del Mercado Laboral")
    
    # Métricas clave para KPIs principales
    key_metrics = {
        'unemployment_rate': {
            'label': 'Tasa de Desempleo',
            'format': 'percentage',
            'icon': '📉'
        },
        'payroll_employment': {
            'label': 'Variación Nóminas',
            'format': 'thousands',
            'icon': '🏭'
        },
        'job_openings': {
            'label': 'Vacantes de Trabajo', 
            'format': 'millions',
            'icon': '💼'
        },
        'avg_hourly_earnings': {
            'label': 'Salario Promedio/Hora',
            'format': 'currency',
            'icon': '💰'
        }
    }
    
    # Aplicar filtros si están definidos
    if filter_type and filter_params:
        filtered_data = {}
        for metric in key_metrics.keys():
            if metric in data_dict:
                filtered_data[metric] = filter_data_by_date(data_dict[metric], filter_type, filter_params)
            else:
                filtered_data[metric] = None
    else:
        filtered_data = {k: v for k, v in data_dict.items() if k in key_metrics.keys()}
    
    # Crear columnas para KPIs
    available_metrics = [k for k, v in filtered_data.items() if v is not None and len(v) > 0]
    
    if not available_metrics:
        st.warning("No hay datos disponibles para los KPIs principales")
        return
    
    cols = st.columns(len(available_metrics))
    
    for idx, metric in enumerate(available_metrics):
        with cols[idx]:
            data = filtered_data[metric]
            metric_config = key_metrics[metric]
            
            if data is not None and len(data) > 0:
                current_value = data.iloc[-1]['value']
                previous_value = data.iloc[-2]['value'] if len(data) > 1 else current_value
                delta = current_value - previous_value
                
                # Obtener indicadores de salud y tendencia
                health_emoji, health_status = get_metric_health_indicator(metric, current_value, delta)
                trend_indicator = get_trend_indicator(delta)
                
                # Formatear valores según el tipo de métrica
                if metric_config['format'] == 'percentage':
                    value_str = f"{current_value:.1f}%"
                    delta_str = f"{delta:+.2f}pp" if delta != 0 else "0.00pp"
                elif metric_config['format'] == 'currency':
                    value_str = f"${current_value:.2f}"
                    delta_str = f"${delta:+.2f}" if delta != 0 else "$0.00"
                elif metric_config['format'] == 'thousands':
                    if metric == 'payroll_employment' and len(data) > 1:
                        # Para nóminas, mostrar variación mensual
                        monthly_change = current_value - previous_value
                        value_str = f"{monthly_change/1000:+.0f}K"
                        delta_str = f"{monthly_change:+,.0f}" if monthly_change != 0 else "0"
                    else:
                        value_str = f"{current_value/1000:.0f}K"
                        delta_str = f"{delta/1000:+.0f}K" if delta != 0 else "0K"
                elif metric_config['format'] == 'millions':
                    value_str = f"{current_value/1000000:.1f}M"
                    delta_str = f"{delta/1000000:+.1f}M" if delta != 0 else "0.0M"
                else:
                    value_str = f"{current_value:,.0f}"
                    delta_str = f"{delta:+,.0f}" if delta != 0 else "0"
                
                # Crear label con emoji e indicador de salud
                kpi_label = f"{metric_config['icon']} {metric_config['label']} {health_emoji}"
                
                # Mostrar métrica con indicador de tendencia
                st.metric(
                    label=kpi_label,
                    value=value_str,
                    delta=f"{trend_indicator} {delta_str}"
                )
                
                # Agregar contexto de salud
                if health_status == "good":
                    st.success("🎯 Nivel saludable", icon="✅")
                elif health_status == "bad":
                    st.error("⚠️ Nivel preocupante", icon="🚨")
                elif health_status == "warning":
                    st.warning("📊 Nivel moderado", icon="⚠️")
                else:
                    st.info("📈 Monitoreando", icon="ℹ️")
                
                # Mostrar fecha del último dato
                last_date = data.iloc[-1]['date']
                if hasattr(last_date, 'strftime'):
                    st.caption(f"📅 {last_date.strftime('%Y-%m')}")
                else:
                    st.caption(f"📅 {last_date}")
    
    st.markdown("---")

def create_enhanced_line_chart(data, title, y_title, color=None, show_events=True):
    """
    Crea un gráfico de líneas mejorado con anotaciones y líneas de referencia
    """
    if data is None or len(data) == 0:
        return go.Figure()
    
    colors = get_colors()
    chart_colors = get_chart_colors()
    
    if color is None:
        color = colors['primary']
    
    fig = go.Figure()
    
    # Línea principal
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['value'],
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3),
        marker=dict(size=4),
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Fecha: %{x}<br>' +
                     'Valor: %{y}<br>' +
                     '<extra></extra>'
    ))
    
    # Línea de promedio histórico
    mean_value = data['value'].mean()
    fig.add_hline(y=mean_value, line_dash="dash", line_color=colors['neutral'],
                  annotation_text=f"Promedio: {mean_value:.1f}")
    
    # Sombrear recesiones si corresponde
    if show_events:
        # COVID period
        fig.add_vrect(
            x0="2020-03-01", x1="2020-12-31",
            fillcolor="red", opacity=0.1,
            annotation_text="COVID", annotation_position="top left"
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="Fecha",
        yaxis_title=y_title,
        template=get_plotly_template(),
        height=400,
        font=dict(color=chart_colors['text_color']),
        plot_bgcolor=chart_colors['plot_bgcolor'],
        paper_bgcolor=chart_colors['paper_bgcolor'],
        hovermode='x unified'
    )
    
    return fig

def create_bar_chart_with_comparison(data, title, y_title, comparison_type="MoM"):
    """
    Crea gráfico de barras con comparación período sobre período
    """
    if data is None or len(data) < 2:
        return go.Figure()
    
    colors = get_colors()
    chart_colors = get_chart_colors()
    
    # Calcular cambios período sobre período
    data = data.copy()
    if comparison_type == "MoM":
        data['change'] = data['value'].diff()
        data['pct_change'] = data['value'].pct_change() * 100
    elif comparison_type == "YoY":
        data['change'] = data['value'].diff(12)  # 12 months ago
        data['pct_change'] = data['value'].pct_change(12) * 100
    
    # Colores condicionalesbasados en el cambio
    bar_colors = [colors['success'] if x > 0 else colors['warning'] if x < 0 else colors['neutral'] 
                  for x in data['change'].fillna(0)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data['date'],
        y=data['change'],
        name=f'Cambio {comparison_type}',
        marker_color=bar_colors,
        hovertemplate=f'<b>Cambio {comparison_type}</b><br>' +
                     'Fecha: %{x}<br>' +
                     'Cambio: %{y}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{title} - Cambios {comparison_type}",
        xaxis_title="Fecha",
        yaxis_title=f"Cambio {comparison_type} ({y_title})",
        template=get_plotly_template(),
        height=400,
        font=dict(color=chart_colors['text_color']),
        plot_bgcolor=chart_colors['plot_bgcolor'],
        paper_bgcolor=chart_colors['paper_bgcolor'],
        showlegend=False
    )
    
    return fig

def create_dual_axis_chart(data1, data2, title1, title2, overall_title):
    """
    Crea gráfico con doble eje Y para comparar dos métricas relacionadas
    """
    colors = get_colors()
    chart_colors = get_chart_colors()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Primera métrica (eje izquierdo)
    if data1 is not None and len(data1) > 0:
        fig.add_trace(
            go.Scatter(
                x=data1['date'],
                y=data1['value'],
                name=title1,
                line=dict(color=colors['primary'], width=3),
                mode='lines'
            ),
            secondary_y=False,
        )
    
    # Segunda métrica (eje derecho)
    if data2 is not None and len(data2) > 0:
        fig.add_trace(
            go.Scatter(
                x=data2['date'],
                y=data2['value'],
                name=title2,
                line=dict(color=colors['secondary'], width=3),
                mode='lines'
            ),
            secondary_y=True,
        )
    
    fig.update_xaxes(title_text="Fecha")
    fig.update_yaxes(title_text=title1, secondary_y=False)
    fig.update_yaxes(title_text=title2, secondary_y=True)
    
    fig.update_layout(
        title=overall_title,
        template=get_plotly_template(),
        height=500,
        font=dict(color=chart_colors['text_color']),
        plot_bgcolor=chart_colors['plot_bgcolor'],
        paper_bgcolor=chart_colors['paper_bgcolor'],
        hovermode='x unified'
    )
    
    return fig

def create_jolts_flow_chart(data_dict):
    """
    Crea gráfico combinado de flujos JOLTS (Contrataciones, Renuncias, Despidos)
    """
    colors = get_colors()
    chart_colors = get_chart_colors()
    
    fig = go.Figure()
    
    jolts_metrics = {
        'quits_rate': {'name': 'Renuncias', 'color': colors['success']},
        'layoffs_rate': {'name': 'Despidos', 'color': colors['warning']},
        # 'hires_rate': {'name': 'Contrataciones', 'color': colors['info']}  # Si está disponible
    }
    
    for metric, config in jolts_metrics.items():
        if metric in data_dict and data_dict[metric] is not None:
            data = data_dict[metric]
            fig.add_trace(go.Scatter(
                x=data['date'],
                y=data['value'],
                mode='lines+markers',
                name=config['name'],
                line=dict(color=config['color'], width=2),
                marker=dict(size=4),
                hovertemplate=f'<b>{config["name"]}</b><br>' +
                             'Fecha: %{x}<br>' +
                             'Tasa: %{y}%<br>' +
                             '<extra></extra>'
            ))
    
    fig.update_layout(
        title="🔄 Dinámica del Mercado Laboral - Flujos JOLTS",
        xaxis_title="Fecha",
        yaxis_title="Tasa (%)",
        template=get_plotly_template(),
        height=500,
        font=dict(color=chart_colors['text_color']),
        plot_bgcolor=chart_colors['plot_bgcolor'],
        paper_bgcolor=chart_colors['paper_bgcolor'],
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
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
    # Control de configuración en sidebar
    st.sidebar.header("⚙️ Configuración")
    
    # Aplicar CSS tema oscuro único
    apply_custom_css()
    
    # Header principal
    st.markdown('<h1 class="main-header">Dashboard Mercado Laboral USA</h1>', 
                unsafe_allow_html=True)
    
    # Control para forzar actualización
    force_refresh = st.sidebar.button("🔄 Actualizar Datos")
    
    # Cargar datos primero para obtener años disponibles
    with st.spinner("Cargando datos..."):
        try:
            data_dict = load_labor_data(force_refresh=force_refresh)
            
            if data_dict:
                available_years = get_available_years(data_dict)
                min_date, max_date = get_date_range(data_dict)
            else:
                available_years = list(range(2020, 2026))
                min_date, max_date = datetime(2020, 1, 1), datetime.now()
                
        except Exception as e:
            st.error(f"❌ Error cargando datos: {e}")
            available_years = list(range(2020, 2026))
            min_date, max_date = datetime(2020, 1, 1), datetime.now()
            data_dict = None
    
    # Renderizar controles de filtro de fecha con años dinámicos
    filter_type, filter_params = render_date_filters_dynamic(available_years, min_date, max_date)
    
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
        # Si los datos no se cargaron antes, intentar cargarlos ahora
        if not data_dict:
            with st.spinner("Cargando datos del mercado laboral desde SQLite..."):
                try:
                    data_dict = load_labor_data(force_refresh=True)
                    
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
                    
                    # Recalcular años disponibles y rango de fechas
                    available_years = get_available_years(data_dict)
                    min_date, max_date = get_date_range(data_dict)
                    
                except Exception as e:
                    st.error(f"❌ Error cargando datos: {e}")
                    return
        
        st.sidebar.success("📊 Datos actualizados desde APIs")
    
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
    
    # KPIs Principales en la parte superior
    render_kpi_dashboard(data_dict, filter_type, filter_params)
    
    # Dashboard reorganizado por categorías temáticas
    # Crear pestañas principales siguiendo la propuesta del usuario
    thematic_tabs = st.tabs([
        "🏥 Salud General",
        "🏗️ Creación de Empleo", 
        "🔄 Dinámica Laboral",
        "💰 Compensación",
        "📅 Calendario",
        "🔗 Enlaces"
    ])
    
    # Pestaña 1: 🏥 Salud General del Mercado Laboral
    with thematic_tabs[0]:
        st.markdown("### 🏥 Salud General del Mercado Laboral")
        st.markdown("*Métricas fundamentales que indican la salud general del empleo*")
        
        # Aplicar filtros a métricas de salud general
        health_metrics = ['unemployment_rate', 'labor_force_participation']
        filtered_health_data = {}
        
        for metric in health_metrics:
            if metric in data_dict:
                if filter_type and filter_params:
                    filtered_health_data[metric] = filter_data_by_date(data_dict[metric], filter_type, filter_params)
                else:
                    filtered_health_data[metric] = data_dict[metric]
        
        # Gráfico dual: Desempleo vs Participación Laboral
        if 'unemployment_rate' in filtered_health_data and 'labor_force_participation' in filtered_health_data:
            dual_fig = create_dual_axis_chart(
                filtered_health_data['unemployment_rate'],
                filtered_health_data['labor_force_participation'], 
                "Tasa de Desempleo (%)",
                "Participación Laboral (%)",
                "🏥 Desempleo vs Participación en la Fuerza Laboral"
            )
            st.plotly_chart(dual_fig, use_container_width=True)
        
        # Gráficos individuales mejorados
        col1, col2 = st.columns(2)
        
        with col1:
            if 'unemployment_rate' in filtered_health_data:
                unemp_fig = create_enhanced_line_chart(
                    filtered_health_data['unemployment_rate'],
                    "📉 Tasa de Desempleo",
                    "Porcentaje (%)",
                    color='#ff6b6b'
                )
                st.plotly_chart(unemp_fig, use_container_width=True)
        
        with col2:
            if 'labor_force_participation' in filtered_health_data:
                part_fig = create_enhanced_line_chart(
                    filtered_health_data['labor_force_participation'],
                    "👥 Participación en Fuerza Laboral", 
                    "Porcentaje (%)",
                    color='#4dabf7'
                )
                st.plotly_chart(part_fig, use_container_width=True)
    
    # Pestaña 2: 🏗️ Creación de Empleo
    with thematic_tabs[1]:
        filtered_data_2 = render_category_metrics('dinamica_mercado', data_dict, filter_type, filter_params)
        
        # Gráfico específico para dinámica con datos filtrados
        if len(filtered_data_2) >= 2:
            st.markdown("### 📈 Tendencias de Dinámica Laboral")
            combined_fig = create_combined_chart(filtered_data_2, " (Filtrado)")
            st.plotly_chart(combined_fig, use_container_width=True)
    
    # Pestaña 3: Salarios e Inflación
    with thematic_tabs[2]:
        filtered_data_3 = render_category_metrics('salarios_inflacion', data_dict, filter_type, filter_params)
        
        # Gráficos específicos para salarios con datos filtrados
        if len(filtered_data_3) >= 1:
            st.markdown("### 📈 Tendencias Salariales")
            for metric, data in filtered_data_3.items():
                if data is not None and len(data) > 0:
                    colors = get_colors()
                    fig = create_trend_chart(data, UI_LABELS[metric], 
                                           UI_LABELS[metric], colors['success'])
                    st.plotly_chart(fig, use_container_width=True)
    

    # Pestaña 4: 💰 Compensación (placeholder por ahora)
    with thematic_tabs[3]:
        st.markdown("### 💰 Compensación y Costo Laboral")
        st.info("🚧 Esta sección se está desarrollando - próximamente análisis completo de salarios")
    
    # Pestaña 5: 📅 Calendario de Publicaciones
    with thematic_tabs[4]:
        create_publication_calendar()
    
    # Pestaña 6: 🔗 Enlaces Útiles
    with thematic_tabs[5]:
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