"""
Módulo de extracción de datos del mercado laboral USA
Conecta con APIs de BLS (Bureau of Labor Statistics) y FRED (Federal Reserve Economic Data)
"""

import requests
import pandas as pd
import json
import sqlite3
from datetime import datetime, timedelta
import time
import logging
from config import *

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LaborMarketDataCollector:
    """
    Clase principal para recolección de datos del mercado laboral
    """
    
    def __init__(self):
        self.fred_api_key = FRED_API_KEY
        self.bls_api_key = BLS_API_KEY
        self.db_path = DATABASE_PATH
        self.setup_database()
        
    def setup_database(self):
        """
        Configura la base de datos SQLite como almacenamiento principal permanente
        """
        try:
            # Crear directorio de datos si no existe
            import os
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla principal para datos de series temporales (mejorada)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS labor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    value REAL NOT NULL,
                    value_status TEXT DEFAULT 'valid',
                    revision_date TEXT,
                    data_quality_score INTEGER DEFAULT 100,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(series_id, date)
                )
            ''')
            
            # Índices para mejor rendimiento
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_labor_data_series_date 
                ON labor_data(series_id, date DESC)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_labor_data_updated 
                ON labor_data(last_updated DESC)
            ''')
            
            # Tabla para metadatos de series (expandida)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS series_metadata (
                    series_id TEXT PRIMARY KEY,
                    metric_name TEXT,
                    title TEXT,
                    units TEXT,
                    frequency TEXT,
                    source TEXT,
                    source_url TEXT,
                    description TEXT,
                    seasonal_adjustment TEXT,
                    geography TEXT DEFAULT 'USA',
                    category TEXT,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de log de actualizaciones para auditoría
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS update_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_id TEXT,
                    update_type TEXT,
                    records_affected INTEGER,
                    source TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    execution_time_ms INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de configuración del sistema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    description TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Poblar configuración inicial
            cursor.execute('''
                INSERT OR IGNORE INTO system_config (key, value, description)
                VALUES 
                ('db_version', '2.0', 'Versión del esquema de la base de datos'),
                ('last_full_refresh', '', 'Última actualización completa de datos'),
                ('data_source_priority', 'API_ONLY', 'Solo APIs reales, sin datos simulados'),
                ('auto_populate', 'true', 'Poblar automáticamente datos faltantes')
            ''')
            
            conn.commit()
            conn.close()
            logging.info("Base de datos SQLite configurada como almacenamiento principal")
            
        except Exception as e:
            logging.error(f"Error configurando base de datos: {e}")
            
    def get_fred_data(self, series_id, limit=60):
        """
        Obtiene datos de la API de FRED
        
        Args:
            series_id (str): ID de la serie de FRED
            limit (int): Número de observaciones a obtener
        
        Returns:
            pd.DataFrame: DataFrame con los datos
        """
        if not self.fred_api_key or self.fred_api_key == 'tu_api_key_aqui_requerida':
            logging.error("API key de FRED no configurada")
            return pd.DataFrame()
            
        try:
            params = {
                'series_id': series_id,
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': limit
            }
            
            response = requests.get(FRED_BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' in data:
                df = pd.DataFrame(data['observations'])
                df['date'] = pd.to_datetime(df['date'])
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df = df[df['value'].notna()]  # Remover valores faltantes
                df = df.sort_values('date').reset_index(drop=True)
                
                logging.info(f"Obtenidos {len(df)} registros para {series_id} desde FRED")
                return df
                
        except requests.RequestException as e:
            logging.error(f"Error obteniendo datos de FRED para {series_id}: {e}")
        except Exception as e:
            logging.error(f"Error procesando datos de FRED para {series_id}: {e}")
            
        return pd.DataFrame()
    
    def get_bls_data(self, series_ids, start_year=2020, end_year=2025):
        """
        Obtiene datos de la API de BLS
        
        Args:
            series_ids (list): Lista de IDs de series de BLS
            start_year (int): Año de inicio
            end_year (int): Año final
        
        Returns:
            dict: Diccionario con DataFrames por serie
        """
        if not isinstance(series_ids, list):
            series_ids = [series_ids]
            
        data_dict = {}
        
        try:
            payload = {
                'seriesid': series_ids,
                'startyear': str(start_year),
                'endyear': str(end_year)
            }
            
            if self.bls_api_key:
                payload['registrationkey'] = self.bls_api_key
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(BLS_BASE_URL, 
                                   data=json.dumps(payload), 
                                   headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'REQUEST_SUCCEEDED':
                for series in data['Results']['series']:
                    series_id = series['seriesID']
                    observations = []
                    
                    for item in series['data']:
                        # Crear fecha a partir de year y period
                        if 'M' in item['period']:
                            month = int(item['period'][1:])
                            year = int(item['year'])
                            date = datetime(year, month, 1)
                        else:
                            continue
                            
                        observations.append({
                            'date': date,
                            'value': float(item['value']) if item['value'] != '.' else None
                        })
                    
                    df = pd.DataFrame(observations)
                    df = df[df['value'].notna()]  # Remover valores faltantes
                    df = df.sort_values('date').reset_index(drop=True)
                    
                    data_dict[series_id] = df
                    logging.info(f"Obtenidos {len(df)} registros para {series_id} desde BLS")
            else:
                logging.error(f"Error en respuesta de BLS: {data.get('message', 'Error desconocido')}")
                
        except requests.RequestException as e:
            logging.error(f"Error obteniendo datos de BLS: {e}")
        except Exception as e:
            logging.error(f"Error procesando datos de BLS: {e}")
            
        return data_dict
    
    def save_to_cache(self, series_id, df, source='FRED'):
        """
        Guarda datos en la base de datos SQLite permanente
        
        Args:
            series_id (str): ID de la serie
            df (pd.DataFrame): DataFrame con los datos
            source (str): Fuente de los datos (FRED, BLS, SAMPLE)
        """
        start_time = time.time()
        records_affected = 0
        success = False
        error_message = None
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Limpiar datos existentes para esta serie
            conn.execute('DELETE FROM labor_data WHERE series_id = ?', (series_id,))
            
            # Insertar nuevos datos
            for _, row in df.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO labor_data 
                    (series_id, date, value, value_status, data_quality_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    series_id, 
                    row['date'].strftime('%Y-%m-%d'), 
                    row['value'],
                    'valid',
                    100 if source in ['FRED', 'BLS'] else 80  # Datos de ejemplo tienen menor score
                ))
                records_affected += 1
            
            # Encontrar el nombre de métrica para esta serie
            metric_name = None
            for metric, sid in SERIES_MAPPING.items():
                if sid == series_id:
                    metric_name = metric
                    break
            
            # Actualizar metadatos mejorados
            title = UI_LABELS.get(series_id, series_id)
            description = METRIC_DESCRIPTIONS.get(metric_name, 'Serie de datos del mercado laboral')
            
            conn.execute('''
                INSERT OR REPLACE INTO series_metadata 
                (series_id, metric_name, title, source, description, active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (series_id, metric_name, title, source, description, True))
            
            # Registrar en log de actualizaciones
            execution_time_ms = int((time.time() - start_time) * 1000)
            conn.execute('''
                INSERT INTO update_log 
                (series_id, update_type, records_affected, source, success, execution_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (series_id, 'data_save', records_affected, source, True, execution_time_ms))
            
            conn.commit()
            conn.close()
            
            success = True
            logging.info(f"Datos guardados permanentemente: {series_id} ({records_affected} registros) desde {source}")
            
        except Exception as e:
            error_message = str(e)
            logging.error(f"Error guardando datos {series_id}: {e}")
            
            # Registrar error en log
            try:
                conn = sqlite3.connect(self.db_path)
                execution_time_ms = int((time.time() - start_time) * 1000)
                conn.execute('''
                    INSERT INTO update_log 
                    (series_id, update_type, records_affected, source, success, error_message, execution_time_ms)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (series_id, 'data_save', records_affected, source, False, error_message, execution_time_ms))
                conn.commit()
                conn.close()
            except:
                pass
    
    def load_from_cache(self, series_id):
        """
        Carga datos desde la base de datos local
        
        Args:
            series_id (str): ID de la serie
        
        Returns:
            pd.DataFrame: DataFrame con los datos o DataFrame vacío
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = '''
                SELECT date, value, last_updated 
                FROM labor_data 
                WHERE series_id = ? 
                ORDER BY date
            '''
            
            df = pd.read_sql_query(query, conn, params=(series_id,))
            conn.close()
            
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                logging.info(f"Cargados {len(df)} registros desde caché para {series_id}")
                
            return df
            
        except Exception as e:
            logging.error(f"Error cargando desde caché {series_id}: {e}")
            return pd.DataFrame()
    
    def is_cache_fresh(self, series_id, hours=24):
        """
        Verifica si el caché está actualizado
        
        Args:
            series_id (str): ID de la serie
            hours (int): Horas de validez del caché
        
        Returns:
            bool: True si el caché está fresco
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT MAX(last_updated) 
                FROM labor_data 
                WHERE series_id = ?
            ''', (series_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result[0]:
                last_updated = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
                threshold = datetime.now() - timedelta(hours=hours)
                return last_updated > threshold
                
        except Exception as e:
            logging.error(f"Error verificando caché para {series_id}: {e}")
            
        return False
    
    def ensure_data_availability(self):
        """
        Asegura que hay datos disponibles en la base de datos.
        Si no hay datos o están muy desactualizados, los obtiene de las APIs.
        
        Returns:
            bool: True si hay datos disponibles
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si existe al menos una métrica con datos recientes
            cursor.execute('''
                SELECT COUNT(DISTINCT series_id) 
                FROM labor_data 
                WHERE last_updated > datetime('now', '-7 days')
            ''')
            
            recent_series_count = cursor.fetchone()[0]
            conn.close()
            
            # Si tenemos al menos 5 series con datos recientes, consideramos que hay suficientes datos
            if recent_series_count >= 5:
                logging.info(f"Datos disponibles: {recent_series_count} series actualizadas")
                return True
            else:
                logging.warning(f"Datos insuficientes o desactualizados: {recent_series_count} series")
                # Intentar actualizar automáticamente
                self.refresh_all_data()
                return True
                
        except Exception as e:
            logging.error(f"Error verificando disponibilidad de datos: {e}")
            # Intentar poblar la base de datos por primera vez
            self.refresh_all_data()
            return True
    
    def refresh_all_data(self):
        """
        Actualiza todos los datos desde las APIs y los almacena en SQLite
        """
        logging.info("Actualizando todos los datos desde APIs...")
        
        # Verificar que las APIs estén configuradas
        if not self.fred_api_key or self.fred_api_key == 'tu_api_key_aqui_requerida':
            error_msg = "API key de FRED es requerida para obtener datos reales. Configura FRED_API_KEY en el archivo .env"
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        # Obtener datos reales de APIs
        self._fetch_all_api_data()
    
    
    def _fetch_all_api_data(self):
        """
        Obtiene datos reales de las APIs y los almacena
        """
        all_data = {}
        
        # Series de FRED
        fred_series = ['unemployment_rate', 'job_openings', 'quits_rate', 
                      'layoffs_rate', 'labor_force_participation']
        
        for metric in fred_series:
            series_id = SERIES_MAPPING[metric]
            
            # Obtener desde API
            df = self.get_fred_data(series_id)
            if not df.empty:
                self.save_to_cache(series_id, df, 'FRED')
            
            # Rate limiting
            time.sleep(0.5)
        
        # Series de BLS
        bls_series = ['payroll_employment', 'avg_hourly_earnings', 'employment_cost_index']
        bls_series_ids = [SERIES_MAPPING[metric] for metric in bls_series]
        
        bls_data = self.get_bls_data(bls_series_ids)
        
        for metric in bls_series:
            series_id = SERIES_MAPPING[metric]
            if series_id in bls_data:
                self.save_to_cache(series_id, bls_data[series_id], 'BLS')

        # Series de empleo por sector de BLS
        sector_series_ids = list(SECTOR_EMPLOYMENT_SERIES.values())
        sector_data = self.get_bls_data(sector_series_ids)

        for sector_name, series_id in SECTOR_EMPLOYMENT_SERIES.items():
            if series_id in sector_data:
                # Usamos el series_id como 'metric' para el cache
                self.save_to_cache(series_id, sector_data[series_id], 'BLS')
    
    def get_all_labor_data(self, force_refresh=False):
        """
        Obtiene todos los datos del mercado laboral desde SQLite.
        Si no hay datos disponibles o force_refresh=True, actualiza desde APIs.
        
        Args:
            force_refresh (bool): Forzar actualización desde APIs
        
        Returns:
            dict: Diccionario con todos los DataFrames
        """
        # Asegurar que hay datos disponibles en la base de datos
        if force_refresh or not self.ensure_data_availability():
            self.refresh_all_data()
        
        # Cargar todos los datos desde SQLite
        all_data = {}
        
        # Mapear series ID a nombres de métricas
        for metric, series_id in SERIES_MAPPING.items():
            df = self.load_from_cache(series_id)
            if not df.empty:
                all_data[metric] = df[['date', 'value']]

        # Cargar datos de empleo por sector
        sector_employment_data = {}
        for sector_name, series_id in SECTOR_EMPLOYMENT_SERIES.items():
            df = self.load_from_cache(series_id)
            if not df.empty:
                sector_employment_data[sector_name] = df[['date', 'value']]
        
        if sector_employment_data:
            all_data['sector_employment'] = sector_employment_data
        
        # Calcular métrica derivada: Ratio Vacantes/Desempleo
        if 'job_openings' in all_data and 'unemployment_rate' in all_data:
            vacancy_ratio = self.calculate_vacancy_unemployment_ratio(
                all_data['job_openings'], 
                all_data['unemployment_rate']
            )
            if not vacancy_ratio.empty:
                all_data['vacancy_unemployment_ratio'] = vacancy_ratio
        
        logging.info(f"Datos cargados desde SQLite: {len(all_data)} métricas")
        return all_data
    
    def calculate_vacancy_unemployment_ratio(self, job_openings_df, unemployment_df):
        """
        Calcula el ratio de vacantes a desempleo
        
        Args:
            job_openings_df (pd.DataFrame): Datos de vacantes
            unemployment_df (pd.DataFrame): Datos de desempleo
        
        Returns:
            pd.DataFrame: DataFrame con el ratio calculado
        """
        try:
            # Merge de los datos por fecha
            merged = pd.merge(job_openings_df, unemployment_df, on='date', suffixes=('_openings', '_unemployment'))
            
            # Calcular ratio (vacantes en miles / tasa de desempleo)
            merged['value'] = (merged['value_openings'] / 1000) / merged['value_unemployment']
            
            return merged[['date', 'value']].copy()
            
        except Exception as e:
            logging.error(f"Error calculando ratio vacantes/desempleo: {e}")
            return pd.DataFrame()

    def get_database_status(self):
        """
        Obtiene el estado actual de la base de datos
        
        Returns:
            dict: Información del estado de la base de datos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Contar series disponibles
            cursor.execute('SELECT COUNT(DISTINCT series_id) FROM labor_data')
            total_series = cursor.fetchone()[0]
            
            # Contar registros totales
            cursor.execute('SELECT COUNT(*) FROM labor_data')
            total_records = cursor.fetchone()[0]
            
            # Obtener última actualización
            cursor.execute('SELECT MAX(last_updated) FROM labor_data')
            last_update = cursor.fetchone()[0]
            
            # Obtener información por serie
            cursor.execute('''
                SELECT 
                    sm.series_id,
                    sm.title,
                    sm.source,
                    COUNT(ld.value) as record_count,
                    MAX(ld.date) as latest_date,
                    MAX(ld.last_updated) as last_updated
                FROM series_metadata sm
                LEFT JOIN labor_data ld ON sm.series_id = ld.series_id
                GROUP BY sm.series_id
                ORDER BY sm.series_id
            ''')
            
            series_info = cursor.fetchall()
            conn.close()
            
            return {
                'total_series': total_series,
                'total_records': total_records,
                'last_update': last_update,
                'series_details': series_info,
                'db_path': self.db_path
            }
            
        except Exception as e:
            logging.error(f"Error obteniendo estado de la base de datos: {e}")
            return {'error': str(e)}

# Función principal para testing
if __name__ == "__main__":
    collector = LaborMarketDataCollector()
    
    print("Dashboard Mercado Laboral USA - Data Collector Test")
    print("=" * 60)
    
    # Mostrar estado de la base de datos
    print("Estado actual de la base de datos:")
    db_status = collector.get_database_status()
    
    if 'error' not in db_status:
        print(f"Series disponibles: {db_status['total_series']}")
        print(f"Registros totales: {db_status['total_records']}")
        print(f"Ultima actualizacion: {db_status['last_update']}")
        print("\nDetalles por serie:")
        
        for series_info in db_status['series_details']:
            series_id, title, source, records, latest_date, last_updated = series_info
            print(f"  {series_id}: {records} registros (ultimo: {latest_date}) [{source}]")
    else:
        print(f"Error: {db_status['error']}")
    
    print("\n" + "=" * 60)
    print("Obteniendo todos los datos del mercado laboral...")
    
    all_data = collector.get_all_labor_data()
    
    print(f"\nDatos cargados exitosamente:")
    for metric, df in all_data.items():
        if not df.empty:
            latest_value = df.iloc[-1]['value']
            latest_date = df.iloc[-1]['date'].strftime('%Y-%m-%d')
            print(f"  {metric}: {len(df)} registros (ultimo: {latest_value:.2f} el {latest_date})")
        else:
            print(f"  {metric}: Sin datos")
    
    print("\nTest completado exitosamente")