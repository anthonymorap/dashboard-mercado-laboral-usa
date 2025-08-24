"""
Script para probar la conectividad con las APIs BLS y FRED
"""

import argparse
import sys
from data_collector import LaborMarketDataCollector
import logging

def test_fred_connectivity():
    """
    Prueba la conectividad con la API de FRED
    """
    print("Probando conectividad con FRED API...")
    
    collector = LaborMarketDataCollector()
    
    if not collector.fred_api_key or collector.fred_api_key == 'tu_api_key_aqui_requerida':
        print("API key de FRED no configurada en .env")
        print("   Obtén tu API key gratuita en: https://fred.stlouisfed.org/docs/api/api_key.html")
        return False
    
    # Test con serie simple de desempleo
    test_data = collector.get_fred_data('UNRATE', limit=3)
    
    if test_data.empty:
        print("ERROR: No se pudieron obtener datos de FRED")
        return False
    else:
        print(f"OK: FRED conectado correctamente")
        print(f"   Últimos datos obtenidos:")
        for _, row in test_data.tail(3).iterrows():
            print(f"   {row['date'].strftime('%Y-%m')}: {row['value']}%")
        return True

def test_bls_connectivity():
    """
    Prueba la conectividad con la API de BLS
    """
    print("Probando conectividad con BLS API...")
    
    collector = LaborMarketDataCollector()
    
    # BLS API funciona sin key pero con límites
    if not collector.bls_api_key:
        print("WARNING:  API key de BLS no configurada (funciona pero con límites)")
        print("   Obtén tu API key gratuita en: https://www.bls.gov/developers/")
    else:
        print("OK: API key de BLS configurada")
    
    # Test con serie de empleo en nóminas
    test_data = collector.get_bls_data(['CES0000000001'], start_year=2024, end_year=2025)
    
    if not test_data or 'CES0000000001' not in test_data:
        print("ERROR: No se pudieron obtener datos de BLS")
        return False
    else:
        df = test_data['CES0000000001']
        print(f"OK: BLS conectado correctamente")
        print(f"   Últimos datos obtenidos:")
        for _, row in df.tail(3).iterrows():
            print(f"   {row['date'].strftime('%Y-%m')}: {row['value']:,.0f} empleos")
        return True

def test_all_metrics():
    """
    Prueba la obtención de todas las métricas del dashboard
    """
    print("Probando obtención de todas las métricas...")
    
    collector = LaborMarketDataCollector()
    all_data = collector.get_all_labor_data()
    
    if not all_data:
        print("ERROR: No se pudieron obtener datos")
        return False
    
    print(f"OK: Se obtuvieron {len(all_data)} métricas:")
    
    for metric, df in all_data.items():
        if df.empty:
            print(f"   ERROR: {metric}: Sin datos")
        else:
            latest = df.iloc[-1]
            print(f"   OK: {metric}: {len(df)} registros (último: {latest['date'].strftime('%Y-%m')}, valor: {latest['value']:.2f})")
    
    return len(all_data) > 0

def test_database():
    """
    Prueba la funcionalidad completa de la base de datos SQLite
    """
    print("Probando base de datos SQLite (nueva arquitectura)...")
    
    collector = LaborMarketDataCollector()
    
    # Probar que la base de datos se creó correctamente
    import sqlite3
    import os
    
    if not os.path.exists(collector.db_path):
        print("ERROR: Base de datos no creada")
        return False
    
    try:
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        
        # Verificar tablas del esquema mejorado
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        expected_tables = {
            'labor_data', 'series_metadata', 'update_log', 'system_config'
        }
        actual_tables = {table[0] for table in tables}
        
        if not expected_tables.issubset(actual_tables):
            print(f"ERROR: Faltan tablas en el esquema mejorado")
            print(f"   Esperadas: {expected_tables}")
            print(f"   Encontradas: {actual_tables}")
            return False
        
        # Verificar datos
        cursor.execute("SELECT COUNT(*) FROM labor_data;")
        data_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM series_metadata;")
        metadata_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM update_log;")
        log_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT value FROM system_config WHERE key = 'db_version';")
        db_version_result = cursor.fetchone()
        db_version = db_version_result[0] if db_version_result else "Unknown"
        
        # Verificar índices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [idx[0] for idx in cursor.fetchall()]
        
        # Mostrar estado detallado
        print(f"OK: Base de datos SQLite funcionando correctamente")
        print(f"   Version del esquema: {db_version}")
        print(f"   Registros de datos: {data_count:,}")
        print(f"   Series configuradas: {metadata_count}")
        print(f"   Entradas en log: {log_count}")
        print(f"   Indices creados: {len(indexes)}")
        
        # Verificar datos recientes
        if data_count > 0:
            cursor.execute('''
                SELECT series_id, COUNT(*) as records, MAX(date) as latest_date
                FROM labor_data 
                GROUP BY series_id 
                ORDER BY series_id
            ''')
            series_data = cursor.fetchall()
            
            print("   Series disponibles:")
            for series_id, records, latest_date in series_data:
                print(f"     {series_id}: {records} registros (ultimo: {latest_date})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Error probando base de datos: {e}")
        return False

def test_database_status():
    """
    Prueba el nuevo método de estado de la base de datos
    """
    print("Probando estado detallado de la base de datos...")
    
    collector = LaborMarketDataCollector()
    db_status = collector.get_database_status()
    
    if 'error' in db_status:
        print(f"ERROR: {db_status['error']}")
        return False
    
    print("OK: Estado de la base de datos obtenido correctamente")
    print(f"   Series totales: {db_status['total_series']}")
    print(f"   Registros totales: {db_status['total_records']:,}")
    print(f"   Ultima actualizacion: {db_status['last_update']}")
    print(f"   Archivo: {db_status['db_path']}")
    
    if db_status['series_details']:
        print("   Detalles por serie:")
        for series_id, title, source, records, latest_date, last_updated in db_status['series_details']:
            print(f"     {series_id} ({source}): {records} registros (ultimo: {latest_date})")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Probar conectividad con APIs del mercado laboral')
    parser.add_argument('--fred', action='store_true', help='Probar solo FRED API')
    parser.add_argument('--bls', action='store_true', help='Probar solo BLS API')
    parser.add_argument('--db', action='store_true', help='Probar solo base de datos')
    parser.add_argument('--status', action='store_true', help='Probar estado de base de datos')
    parser.add_argument('--all', action='store_true', help='Probar todo')
    parser.add_argument('--verbose', action='store_true', help='Mostrar logs detallados')
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    print("Test de conectividad - Dashboard Mercado Laboral USA")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    if args.fred or args.all:
        total_tests += 1
        if test_fred_connectivity():
            success_count += 1
        print()
    
    if args.bls or args.all:
        total_tests += 1
        if test_bls_connectivity():
            success_count += 1
        print()
    
    if args.db or args.all:
        total_tests += 1
        if test_database():
            success_count += 1
        print()
    
    if args.status or args.all:
        total_tests += 1
        if test_database_status():
            success_count += 1
        print()
    
    if args.all or not any([args.fred, args.bls, args.db, args.status]):
        total_tests += 1
        if test_all_metrics():
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"Resumen: {success_count}/{total_tests} tests pasaron")
    
    if success_count == total_tests:
        print("Todos los tests pasaron - El sistema esta listo!")
        return 0
    else:
        print("Algunos tests fallaron - Revisar configuracion")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)