"""
Test simple del dashboard sin Streamlit para verificar que funciona
"""
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import LaborMarketDataCollector

def test_dashboard_data_loading():
    """
    Prueba la carga de datos como lo hace el dashboard
    """
    print("Probando carga de datos del dashboard...")
    
    try:
        # Simular la función load_labor_data del dashboard
        collector = LaborMarketDataCollector()
        data_dict = collector.get_all_labor_data(force_refresh=False)
        
        if not data_dict:
            print("ERROR: No se pudieron cargar datos")
            return False
        
        print(f"OK: Datos cargados correctamente")
        print(f"   Métricas disponibles: {len(data_dict)}")
        
        # Verificar KPIs principales como en el dashboard
        kpis = ['unemployment_rate', 'job_openings', 'quits_rate', 'vacancy_unemployment_ratio']
        
        print("\n   KPIs principales:")
        for kpi in kpis:
            if kpi in data_dict and not data_dict[kpi].empty:
                latest = data_dict[kpi].iloc[-1]
                print(f"     {kpi}: {latest['value']:.2f} (fecha: {latest['date'].strftime('%Y-%m')})")
            else:
                print(f"     {kpi}: Sin datos")
        
        # Probar función get_database_status
        db_status = collector.get_database_status()
        if 'error' not in db_status:
            print(f"\n   Estado de la base de datos:")
            print(f"     Series: {db_status['total_series']}")
            print(f"     Registros: {db_status['total_records']:,}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Test de funcionamiento del Dashboard (sin Streamlit)")
    print("=" * 60)
    
    success = test_dashboard_data_loading()
    
    if success:
        print("\nTest exitoso - El dashboard deberia funcionar correctamente")
        print("  Para ejecutar el dashboard real:")
        print("    1. Activar entorno virtual: venv_mercado_laboral\\Scripts\\activate")
        print("    2. Ejecutar: streamlit run dashboard.py")
    else:
        print("\nTest fallo - Revisar configuracion")