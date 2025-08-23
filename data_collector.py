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
        Configura la base de datos SQLite local para caché
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla para datos de series temporales
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS labor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    value REAL NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(series_id, date)
                )
            ''')
            
            # Tabla para metadatos de series
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS series_metadata (
                    series_id TEXT PRIMARY KEY,
                    title TEXT,
                    units TEXT,
                    frequency TEXT,
                    source TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info("Base de datos configurada correctamente")
            
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
        Guarda datos en la base de datos local
        
        Args:
            series_id (str): ID de la serie
            df (pd.DataFrame): DataFrame con los datos
            source (str): Fuente de los datos (FRED o BLS)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Limpiar datos existentes para esta serie
            conn.execute('DELETE FROM labor_data WHERE series_id = ?', (series_id,))
            
            # Insertar nuevos datos
            for _, row in df.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO labor_data (series_id, date, value)
                    VALUES (?, ?, ?)
                ''', (series_id, row['date'].strftime('%Y-%m-%d'), row['value']))
            
            # Actualizar metadatos
            title = UI_LABELS.get(series_id, series_id)
            conn.execute('''
                INSERT OR REPLACE INTO series_metadata (series_id, title, source)
                VALUES (?, ?, ?)
            ''', (series_id, title, source))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Datos guardados en caché para {series_id}")
            
        except Exception as e:
            logging.error(f"Error guardando en caché {series_id}: {e}")
    
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
    
    def get_all_labor_data(self, force_refresh=False):
        """
        Obtiene todos los datos del mercado laboral
        
        Args:
            force_refresh (bool): Forzar actualización desde APIs
        
        Returns:
            dict: Diccionario con todos los DataFrames
        """
        all_data = {}
        
        # Series de FRED
        fred_series = ['unemployment_rate', 'job_openings', 'quits_rate', 
                      'layoffs_rate', 'labor_force_participation']
        
        for metric in fred_series:
            series_id = SERIES_MAPPING[metric]
            
            # Verificar caché
            if not force_refresh and self.is_cache_fresh(series_id, CACHE_DURATION_HOURS):
                df = self.load_from_cache(series_id)
                if not df.empty:
                    all_data[metric] = df[['date', 'value']]
                    continue
            
            # Obtener desde API
            df = self.get_fred_data(series_id)
            if not df.empty:
                self.save_to_cache(series_id, df, 'FRED')
                all_data[metric] = df[['date', 'value']]
            
            # Rate limiting
            time.sleep(0.5)
        
        # Series de BLS
        bls_series = ['payroll_employment', 'avg_hourly_earnings', 'employment_cost_index']
        bls_series_ids = [SERIES_MAPPING[metric] for metric in bls_series]
        
        # Verificar caché de BLS
        need_bls_refresh = force_refresh
        if not force_refresh:
            for metric in bls_series:
                series_id = SERIES_MAPPING[metric]
                if not self.is_cache_fresh(series_id, CACHE_DURATION_HOURS):
                    need_bls_refresh = True
                    break
        
        if need_bls_refresh:
            bls_data = self.get_bls_data(bls_series_ids)
            
            for metric in bls_series:
                series_id = SERIES_MAPPING[metric]
                if series_id in bls_data:
                    self.save_to_cache(series_id, bls_data[series_id], 'BLS')
                    all_data[metric] = bls_data[series_id]
        else:
            # Cargar desde caché
            for metric in bls_series:
                series_id = SERIES_MAPPING[metric]
                df = self.load_from_cache(series_id)
                if not df.empty:
                    all_data[metric] = df[['date', 'value']]
        
        # Calcular métrica derivada: Ratio Vacantes/Desempleo
        if 'job_openings' in all_data and 'unemployment_rate' in all_data:
            vacancy_ratio = self.calculate_vacancy_unemployment_ratio(
                all_data['job_openings'], 
                all_data['unemployment_rate']
            )
            if not vacancy_ratio.empty:
                all_data['vacancy_unemployment_ratio'] = vacancy_ratio
        
        logging.info(f"Recopilados datos para {len(all_data)} métricas")
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

# Función principal para testing
if __name__ == "__main__":
    collector = LaborMarketDataCollector()
    
    # Test de conectividad básica
    print("Probando conexión con FRED...")
    fred_test = collector.get_fred_data('UNRATE', limit=3)
    print(f"FRED test: {'✓' if not fred_test.empty else '✗'}")
    
    print("Probando conexión con BLS...")
    bls_test = collector.get_bls_data(['CES0000000001'])
    print(f"BLS test: {'✓' if bls_test else '✗'}")
    
    print("Obteniendo todos los datos...")
    all_data = collector.get_all_labor_data()
    
    for metric, df in all_data.items():
        print(f"{metric}: {len(df)} registros")