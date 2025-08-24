"""
Test del sistema de tema oscuro/claro
"""
import sys
import os

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import COLOR_PALETTES

def test_theme_colors():
    """
    Prueba que las paletas de colores están correctamente configuradas
    """
    print("Testing tema oscuro/claro...")
    
    # Verificar que ambas paletas existen
    assert 'light' in COLOR_PALETTES, "Falta paleta 'light'"
    assert 'dark' in COLOR_PALETTES, "Falta paleta 'dark'"
    
    # Verificar que tienen todas las claves necesarias
    required_keys = [
        'primary', 'secondary', 'success', 'warning', 'info', 'neutral',
        'background', 'text', 'card_bg', 'border', 'sidebar_bg', 'chart_bg'
    ]
    
    for theme_name, palette in COLOR_PALETTES.items():
        print(f"\nVerificando tema '{theme_name}':")
        for key in required_keys:
            assert key in palette, f"Falta clave '{key}' en tema '{theme_name}'"
            print(f"  {key}: {palette[key]}")
    
    print("\nTodas las paletas de colores están correctamente configuradas!")
    return True

def test_dashboard_imports():
    """
    Verifica que las funciones de tema se pueden importar correctamente
    """
    print("\nTesting importación de funciones de tema...")
    
    try:
        from dashboard import get_theme_colors, apply_custom_css, get_plotly_template, get_theme_chart_colors
        
        # Probar que las funciones funcionan
        light_colors = get_theme_colors('light')
        dark_colors = get_theme_colors('dark')
        
        print(f"Colores tema claro - primary: {light_colors['primary']}")
        print(f"Colores tema oscuro - primary: {dark_colors['primary']}")
        
        # Probar plantillas de Plotly
        light_template = get_plotly_template('light')
        dark_template = get_plotly_template('dark')
        
        print(f"Template claro: {light_template}")
        print(f"Template oscuro: {dark_template}")
        
        print("Importación y funciones de tema funcionando correctamente!")
        return True
        
    except Exception as e:
        print(f"Error en importación: {e}")
        return False

if __name__ == "__main__":
    print("Test del Sistema de Tema Oscuro/Claro")
    print("=" * 50)
    
    success = True
    
    try:
        success &= test_theme_colors()
        success &= test_dashboard_imports()
        
        if success:
            print("\nTodos los tests pasaron exitosamente!")
            print("El sistema de tema oscuro está listo para usar.")
            print("\nPara probarlo:")
            print("1. Ejecutar: streamlit run dashboard.py")
            print("2. En el sidebar, seleccionar entre '🌞 Claro' y '🌙 Oscuro'")
        else:
            print("\nAlgunos tests fallaron - revisar configuración")
            
    except Exception as e:
        print(f"Error en tests: {e}")
        success = False
    
    exit(0 if success else 1)