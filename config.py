"""
Configuración general del proyecto Dashboard Mercado Laboral USA
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# APIs Configuration
BLS_API_KEY = os.getenv('BLS_API_KEY', '')
FRED_API_KEY = os.getenv('FRED_API_KEY', '')

# URLs Base de las APIs
BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Series IDs para las métricas clave
SERIES_MAPPING = {
    # FRED Series
    'unemployment_rate': 'UNRATE',              # Tasa de Desempleo
    'job_openings': 'JTSJOL',                   # Vacantes de Trabajo
    'quits_rate': 'JTSQUR',                     # Tasa de Renuncias
    'layoffs_rate': 'JTSLDR',                   # Tasa de Despidos
    'labor_force_participation': 'CIVPART',     # Tasa de Participación Laboral
    
    # BLS Series - estas necesitan formato especial
    'payroll_employment': 'CES0000000001',      # Total Nonfarm Payrolls
    'avg_hourly_earnings': 'CES0500000003',     # Average Hourly Earnings
    'employment_cost_index': 'CIU2010000000000SA', # Employment Cost Index
}

# Series IDs para empleo por sector (BLS)
SECTOR_EMPLOYMENT_SERIES = {
    'Goods-Producing': 'CES1000000001',
    'Construction': 'CES2000000001',
    'Manufacturing': 'CES3000000001',
    'Trade, Transportation, and Utilities': 'CES4000000001',
    'Information': 'CES5000000001',
    'Financial Activities': 'CES5500000001',
    'Professional and Business Services': 'CES6000000001',
    'Education and Health Services': 'CES6500000001',
    'Leisure and Hospitality': 'CES7000000001',
    'Other Services': 'CES8000000001',
    'Government': 'CES9000000001',
}

# Configuración de datos y base de datos
DATA_UPDATE_HOUR = int(os.getenv('DATA_UPDATE_HOUR', 9))
CACHE_DURATION_HOURS = int(os.getenv('CACHE_DURATION_HOURS', 24))
DATABASE_AUTO_POPULATE = bool(os.getenv('DATABASE_AUTO_POPULATE', True))
DATABASE_FALLBACK_TO_SAMPLE = bool(os.getenv('DATABASE_FALLBACK_TO_SAMPLE', True))

# Configuración de la base de datos SQLite
DATABASE_PATH = "data/labor_market.db"

# Configuración del sistema de datos único (SQLite como fuente principal)
DATA_SYSTEM_CONFIG = {
    'use_sqlite_as_primary': True,
    'auto_populate_on_empty': True,
    'fallback_to_sample_data': True,
    'refresh_threshold_days': 7,
    'min_series_required': 5
}

# Configuración de Streamlit
STREAMLIT_CONFIG = {
    'page_title': "Dashboard Mercado Laboral USA",
    'page_icon': "📊",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

# Paleta de colores tema oscuro único
COLOR_PALETTE = {
    'primary': '#4dabf7',      # Azul más claro
    'secondary': '#ffa94d',    # Naranja más suave
    'success': '#51cf66',      # Verde más brillante
    'warning': '#ff6b6b',      # Rojo más suave
    'info': '#b197fc',         # Púrpura más claro
    'neutral': '#adb5bd',      # Gris más claro
    'background': '#1a1a1a',   # Fondo principal oscuro
    'text': '#e9ecef',         # Texto claro
    'card_bg': '#2d2d30',      # Fondo tarjetas oscuro
    'border': '#495057',       # Bordes oscuros
    'sidebar_bg': '#212529',   # Fondo sidebar oscuro
    'chart_bg': 'rgba(0,0,0,0)' # Fondo gráficos
}

# Límites para alertas (thresholds)
ALERT_THRESHOLDS = {
    'unemployment_rate_high': 5.0,        # % - Alerta si sube mucho
    'job_openings_low': 8000000,          # Número - Alerta si baja mucho
    'quits_rate_low': 2.0,                # % - Confianza del trabajador baja
    'layoffs_rate_high': 1.5,             # % - Alerta despidos altos
    'wage_growth_low': 2.5,               # % - Crecimiento salarial bajo
    'participation_rate_low': 62.0        # % - Participación laboral baja
}

# Configuración de fechas (últimos N años para análisis)
YEARS_OF_DATA = 5

# Configuración de la API de FRED
FRED_API_CONFIG = {
    'file_type': 'json',
    'sort_order': 'desc',
    'limit': 12 * YEARS_OF_DATA,  # Últimos 5 años de datos mensuales
}

# Configuración de la API de BLS
BLS_API_CONFIG = {
    'seriesid': [],  # Se llena dinámicamente
    'startyear': str(2020),
    'endyear': str(2025),
    'registrationkey': BLS_API_KEY if BLS_API_KEY else None
}

# Textos y labels para la interfaz
UI_LABELS = {
    'unemployment_rate': 'Tasa de Desempleo (%)',
    'job_openings': 'Vacantes de Trabajo (Miles)',
    'quits_rate': 'Tasa de Renuncias (%)',
    'layoffs_rate': 'Tasa de Despidos (%)',
    'labor_force_participation': 'Participación Laboral (%)',
    'payroll_employment': 'Empleo en Nóminas (Miles)',
    'avg_hourly_earnings': 'Salario Promedio por Hora ($)',
    'employment_cost_index': 'Índice de Costo de Empleo',
    'vacancy_unemployment_ratio': 'Ratio Vacantes/Desempleo'
}

# Organización por categorías del dashboard
DASHBOARD_CATEGORIES = {
    'condiciones_generales': {
        'title': '📊 Condiciones Generales del Empleo',
        'description': 'Métricas fundamentales del estado del empleo',
        'metrics': [
            'unemployment_rate',
            'payroll_employment', 
            'labor_force_participation',
            'job_openings'  # Como proxy de crecimiento fuerza laboral
        ],
        'color': '#4dabf7'  # Azul principal
    },
    'dinamica_mercado': {
        'title': '🔄 Dinámica del Mercado Laboral',
        'description': 'Flujos y movimientos en el mercado de trabajo',
        'metrics': [
            'quits_rate',
            'layoffs_rate',
            'vacancy_unemployment_ratio'
        ],
        'color': '#ffa94d'  # Naranja
    },
    'salarios_inflacion': {
        'title': '💰 Salarios e Inflación',
        'description': 'Aspectos económicos y compensación laboral',
        'metrics': [
            'avg_hourly_earnings',
            'employment_cost_index'
        ],
        'color': '#51cf66'  # Verde
    }
}

# Configuración de filtros temporales
FILTER_PRESETS = {
    'ultimo_ano': {
        'name': '📅 Último Año',
        'description': 'Últimos 12 meses de datos',
        'months': 12
    },
    'ultimos_6_meses': {
        'name': '📆 Últimos 6 Meses', 
        'description': 'Últimos 6 meses de datos',
        'months': 6
    },
    'ano_2024': {
        'name': '🗓️ Año 2024',
        'description': 'Todo el año 2024',
        'year': 2024
    },
    'ano_2023': {
        'name': '🗓️ Año 2023',
        'description': 'Todo el año 2023', 
        'year': 2023
    },
    'pre_covid': {
        'name': '🕰️ Pre-COVID',
        'description': 'Enero 2020 - Febrero 2020',
        'start_date': '2020-01-01',
        'end_date': '2020-02-29'
    },
    'covid_periodo': {
        'name': '🦠 Período COVID',
        'description': 'Marzo 2020 - Diciembre 2021',
        'start_date': '2020-03-01',
        'end_date': '2021-12-31'
    },
    'post_covid': {
        'name': '📈 Post-COVID',
        'description': 'Enero 2022 - Presente',
        'start_date': '2022-01-01',
        'end_date': None  # None = hasta la fecha más reciente
    }
}

# Opciones de filtros temporales
FILTER_TYPES = {
    'preset': 'Períodos Predefinidos',
    'years': 'Por Años Específicos',  
    'months': 'Rango de Meses',
    'custom': 'Rango Personalizado'
}

# Descripciones para cada métrica
METRIC_DESCRIPTIONS = {
    'unemployment_rate': 'Porcentaje de la fuerza laboral que está desempleada y buscando trabajo activamente',
    'job_openings': 'Número total de puestos de trabajo disponibles en el mercado laboral',
    'quits_rate': 'Porcentaje de trabajadores que renunciaron voluntariamente a sus empleos',
    'layoffs_rate': 'Porcentaje de trabajadores despedidos por razones económicas',
    'labor_force_participation': 'Porcentaje de la población en edad de trabajar que está empleada o buscando empleo',
    'payroll_employment': 'Número total de empleos en nóminas no agrícolas',
    'avg_hourly_earnings': 'Salario promedio por hora de los trabajadores del sector privado',
    'employment_cost_index': 'Medida del costo laboral total (salarios + beneficios)',
    'vacancy_unemployment_ratio': 'Relación entre puestos vacantes y personas desempleadas'
}

# Calendario de publicaciones de reportes oficiales
PUBLICATION_CALENDAR = {
    'employment_situation': {
        'name': 'Employment Situation Report',
        'source': 'Bureau of Labor Statistics (BLS)',
        'frequency': 'Mensual',
        'timing': 'Primer viernes del mes (para mes anterior)',
        'time': '8:30 AM ET',
        'metrics': ['unemployment_rate', 'payroll_employment', 'avg_hourly_earnings', 'labor_force_participation'],
        'url': 'https://www.bls.gov/news.release/empsit.htm',
        'schedule_url': 'https://www.bls.gov/schedule/news_release/empsit.htm',
        'description': 'Reporte principal del mercado laboral con datos de desempleo, empleo en nóminas y salarios',
        'release_dates_2025': [
            {'date': '2025-09-06', 'data_for': 'Agosto 2025', 'status': 'scheduled'},
            {'date': '2025-10-04', 'data_for': 'Septiembre 2025', 'status': 'scheduled'},
            {'date': '2025-11-01', 'data_for': 'Octubre 2025', 'status': 'scheduled'},
            {'date': '2025-12-06', 'data_for': 'Noviembre 2025', 'status': 'scheduled'},
            {'date': '2026-01-10', 'data_for': 'Diciembre 2025', 'status': 'scheduled'}
        ]
    },
    'jolts': {
        'name': 'Job Openings and Labor Turnover Survey (JOLTS)',
        'source': 'Bureau of Labor Statistics (BLS)',
        'frequency': 'Mensual',
        'timing': '2 meses después del mes de referencia',
        'time': '10:00 AM ET',
        'metrics': ['job_openings', 'quits_rate', 'layoffs_rate'],
        'url': 'https://www.bls.gov/news.release/jolts.htm',
        'schedule_url': 'https://www.bls.gov/schedule/news_release/jolts.htm',
        'description': 'Datos de vacantes, renuncias y despidos del mercado laboral',
        'release_dates_2025': [
            {'date': '2025-09-03', 'data_for': 'Julio 2025', 'status': 'scheduled'},
            {'date': '2025-10-01', 'data_for': 'Agosto 2025', 'status': 'scheduled'},
            {'date': '2025-11-05', 'data_for': 'Septiembre 2025', 'status': 'scheduled'},
            {'date': '2025-12-03', 'data_for': 'Octubre 2025', 'status': 'scheduled'},
            {'date': '2026-01-07', 'data_for': 'Noviembre 2025', 'status': 'scheduled'}
        ]
    },
    'employment_cost_index': {
        'name': 'Employment Cost Index',
        'source': 'Bureau of Labor Statistics (BLS)',
        'frequency': 'Trimestral',
        'timing': 'Último mes del trimestre + 1 mes',
        'time': '8:30 AM ET',
        'metrics': ['employment_cost_index'],
        'url': 'https://www.bls.gov/news.release/eci.htm',
        'schedule_url': 'https://www.bls.gov/eci/',
        'description': 'Índice de costo total del empleo (salarios + beneficios)',
        'release_dates_2025': [
            {'date': '2025-10-31', 'data_for': 'Q3 2025', 'status': 'scheduled'},
            {'date': '2026-01-31', 'data_for': 'Q4 2025', 'status': 'scheduled'}
        ]
    }
}

# Información de reportes y enlaces útiles
REPORT_LINKS = {
    'bls_main': 'https://www.bls.gov/',
    'fred_main': 'https://fred.stlouisfed.org/',
    'employment_situation_current': 'https://www.bls.gov/news.release/empsit.htm',
    'employment_situation_pdf': 'https://www.bls.gov/news.release/pdf/empsit.pdf',
    'jolts_current': 'https://www.bls.gov/news.release/jolts.htm',
    'jolts_pdf': 'https://www.bls.gov/news.release/pdf/jolts.pdf',
    'economic_calendar_fred': 'https://fred.stlouisfed.org/releases/calendar',
    'bls_schedule': 'https://www.bls.gov/schedule/'
}