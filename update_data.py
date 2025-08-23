"""
Script para actualización manual y automática de datos del mercado laboral
"""

import argparse
import logging
import sys
from datetime import datetime
from data_collector import LaborMarketDataCollector

def setup_logging(verbose=False):
    """
    Configura el sistema de logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configurar formato de logging
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Handler para archivo de log
    file_handler = logging.FileHandler('data/update_log.txt', mode='a')
    file_handler.setFormatter(formatter)
    
    # Configurar logger principal
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def update_all_data(force_refresh=False, verbose=False):
    """
    Actualiza todos los datos del mercado laboral
    
    Args:
        force_refresh (bool): Forzar actualización desde APIs
        verbose (bool): Logging detallado
    
    Returns:
        bool: True si la actualización fue exitosa
    """
    logger = setup_logging(verbose)
    
    try:
        logger.info("=" * 60)
        logger.info("INICIO DE ACTUALIZACION DE DATOS")
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info(f"Forzar refresh: {force_refresh}")
        logger.info("=" * 60)
        
        # Crear instancia del collector
        collector = LaborMarketDataCollector()
        
        # Verificar configuración de API keys
        logger.info("Verificando configuración de APIs...")
        
        if not collector.fred_api_key or collector.fred_api_key == 'tu_api_key_aqui_requerida':
            logger.warning("API key de FRED no configurada - datos limitados disponibles")
        else:
            logger.info("API key de FRED configurada correctamente")
        
        if not collector.bls_api_key:
            logger.warning("API key de BLS no configurada - usando acceso público con límites")
        else:
            logger.info("API key de BLS configurada correctamente")
        
        # Obtener todos los datos
        logger.info("Iniciando recolección de datos...")
        data_dict = collector.get_all_labor_data(force_refresh=force_refresh)
        
        if not data_dict:
            logger.error("No se pudieron obtener datos")
            return False
        
        # Reportar estadísticas de datos obtenidos
        logger.info("RESUMEN DE DATOS OBTENIDOS:")
        logger.info("-" * 40)
        
        total_records = 0
        for metric, df in data_dict.items():
            records_count = len(df) if not df.empty else 0
            total_records += records_count
            
            if not df.empty:
                latest_date = df.iloc[-1]['date'].strftime('%Y-%m-%d')
                latest_value = df.iloc[-1]['value']
                logger.info(f"{metric:.<30} {records_count:>4} registros (último: {latest_date}, valor: {latest_value:.2f})")
            else:
                logger.warning(f"{metric:.<30} SIN DATOS")
        
        logger.info("-" * 40)
        logger.info(f"TOTAL: {total_records} registros obtenidos")
        
        # Verificar calidad de datos
        logger.info("Verificando calidad de datos...")
        
        quality_issues = 0
        for metric, df in data_dict.items():
            if df.empty:
                logger.warning(f"Métrica {metric} sin datos")
                quality_issues += 1
            elif len(df) < 12:  # Menos de un año de datos
                logger.warning(f"Métrica {metric} tiene pocos datos ({len(df)} registros)")
                quality_issues += 1
            elif df['value'].isna().sum() > 0:
                logger.warning(f"Métrica {metric} tiene valores faltantes")
                quality_issues += 1
        
        if quality_issues == 0:
            logger.info("Calidad de datos: EXCELENTE - No se encontraron problemas")
        else:
            logger.warning(f"Calidad de datos: {quality_issues} problema(s) encontrado(s)")
        
        # Estadísticas de caché
        logger.info("Verificando estado del caché...")
        
        cache_stats = []
        from config import SERIES_MAPPING
        for metric in data_dict.keys():
            series_id = SERIES_MAPPING.get(metric, metric)
            is_fresh = collector.is_cache_fresh(series_id)
            cache_stats.append((metric, 'FRESCO' if is_fresh else 'OBSOLETO'))
        
        for metric, status in cache_stats:
            logger.info(f"Cache {metric:.<30} {status}")
        
        logger.info("=" * 60)
        logger.info("ACTUALIZACION COMPLETADA EXITOSAMENTE")
        logger.info(f"Timestamp final: {datetime.now()}")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Error durante la actualización: {e}")
        logger.error("ACTUALIZACION FALLIDA")
        return False

def validate_api_keys():
    """
    Valida que las API keys estén configuradas correctamente
    """
    logger = logging.getLogger()
    
    collector = LaborMarketDataCollector()
    
    # Test FRED
    if collector.fred_api_key and collector.fred_api_key != 'tu_api_key_aqui_requerida':
        logger.info("Probando conectividad FRED...")
        fred_test = collector.get_fred_data('UNRATE', limit=1)
        if not fred_test.empty:
            logger.info("FRED: Conexión exitosa")
        else:
            logger.error("FRED: Fallo en la conexión")
            return False
    else:
        logger.warning("FRED: API key no configurada")
    
    # Test BLS
    logger.info("Probando conectividad BLS...")
    bls_test = collector.get_bls_data(['CES0000000001'], start_year=2024, end_year=2025)
    if bls_test and 'CES0000000001' in bls_test:
        logger.info("BLS: Conexión exitosa")
    else:
        logger.error("BLS: Fallo en la conexión")
        return False
    
    return True

def cleanup_old_data(days_to_keep=30):
    """
    Limpia datos antiguos de la base de datos
    
    Args:
        days_to_keep (int): Días de datos históricos a conservar
    """
    logger = logging.getLogger()
    
    try:
        import sqlite3
        from datetime import timedelta
        
        collector = LaborMarketDataCollector()
        
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(collector.db_path)
        cursor = conn.cursor()
        
        # Contar registros a eliminar
        cursor.execute('SELECT COUNT(*) FROM labor_data WHERE date < ?', (cutoff_date,))
        count_to_delete = cursor.fetchone()[0]
        
        if count_to_delete > 0:
            # Eliminar registros antiguos
            cursor.execute('DELETE FROM labor_data WHERE date < ?', (cutoff_date,))
            conn.commit()
            logger.info(f"Limpieza: Eliminados {count_to_delete} registros anteriores a {cutoff_date}")
        else:
            logger.info("Limpieza: No hay registros antiguos para eliminar")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error durante la limpieza: {e}")

def generate_report():
    """
    Genera un reporte del estado actual de los datos
    """
    logger = logging.getLogger()
    
    try:
        collector = LaborMarketDataCollector()
        data_dict = collector.get_all_labor_data()
        
        report = []
        report.append("REPORTE DE ESTADO DEL MERCADO LABORAL USA")
        report.append("=" * 50)
        report.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if not data_dict:
            report.append("ERROR: No hay datos disponibles")
            logger.info("\n".join(report))
            return
        
        # Resumen ejecutivo
        latest_data = {}
        for metric, df in data_dict.items():
            if not df.empty:
                latest_data[metric] = {
                    'value': df.iloc[-1]['value'],
                    'date': df.iloc[-1]['date'].strftime('%Y-%m'),
                    'records': len(df)
                }
        
        report.append("INDICADORES CLAVE:")
        report.append("-" * 30)
        
        if 'unemployment_rate' in latest_data:
            report.append(f"Tasa de Desempleo: {latest_data['unemployment_rate']['value']:.1f}% ({latest_data['unemployment_rate']['date']})")
        
        if 'job_openings' in latest_data:
            report.append(f"Vacantes: {latest_data['job_openings']['value']:,.0f}K ({latest_data['job_openings']['date']})")
        
        if 'quits_rate' in latest_data:
            report.append(f"Renuncias: {latest_data['quits_rate']['value']:.1f}% ({latest_data['quits_rate']['date']})")
        
        if 'vacancy_unemployment_ratio' in latest_data:
            report.append(f"Ratio V/U: {latest_data['vacancy_unemployment_ratio']['value']:.2f} ({latest_data['vacancy_unemployment_ratio']['date']})")
        
        report.append("")
        report.append("COBERTURA DE DATOS:")
        report.append("-" * 30)
        
        for metric, info in latest_data.items():
            report.append(f"{metric}: {info['records']} registros hasta {info['date']}")
        
        # Guardar reporte
        report_text = "\n".join(report)
        
        with open('data/latest_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info("Reporte generado exitosamente:")
        logger.info(report_text)
        
    except Exception as e:
        logger.error(f"Error generando reporte: {e}")

def main():
    """
    Función principal del script de actualización
    """
    parser = argparse.ArgumentParser(description='Actualizar datos del mercado laboral USA')
    parser.add_argument('--force', action='store_true', help='Forzar actualización desde APIs')
    parser.add_argument('--verbose', action='store_true', help='Logging detallado')
    parser.add_argument('--validate', action='store_true', help='Validar conectividad de APIs')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Limpiar datos antiguos (días a conservar)')
    parser.add_argument('--report', action='store_true', help='Generar reporte de estado')
    
    args = parser.parse_args()
    
    # Configurar logging básico para empezar
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    success = True
    
    # Validar APIs si se solicita
    if args.validate:
        print("Validando conectividad de APIs...")
        if not validate_api_keys():
            print("ERROR: Fallo en la validación de APIs")
            success = False
    
    # Actualizar datos
    if success:
        print("Actualizando datos...")
        if not update_all_data(force_refresh=args.force, verbose=args.verbose):
            print("ERROR: Fallo en la actualización de datos")
            success = False
    
    # Limpiar datos antiguos si se solicita
    if success and args.cleanup:
        print(f"Limpiando datos antiguos (conservando {args.cleanup} días)...")
        cleanup_old_data(args.cleanup)
    
    # Generar reporte si se solicita
    if success and args.report:
        print("Generando reporte de estado...")
        generate_report()
    
    if success:
        print("Actualización completada exitosamente!")
        return 0
    else:
        print("Actualización falló - revisar logs para detalles")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)