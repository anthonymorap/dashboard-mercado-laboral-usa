
import time
import sys
import os
import threading
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class DashboardViewer:
    """
    Herramienta avanzada para visualización iterativa del dashboard Streamlit
    Permite desarrollo en tiempo real con auto-refresh y captura de screenshots
    """
    
    def __init__(self, app_url="http://localhost:8501", refresh_interval=30):
        self.app_url = app_url
        self.refresh_interval = refresh_interval
        self.driver = None
        self.is_running = False
        self.screenshot_count = 0
        
    def setup_driver(self):
        """
        Configura Chrome WebDriver con opciones optimizadas para desarrollo
        """
        print("🚀 Inicializando Chrome WebDriver para desarrollo iterativo...")
        
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Configurar para desarrollo
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome WebDriver configurado correctamente")
        
    def wait_for_streamlit_load(self, timeout=30):
        """
        Espera a que Streamlit cargue completamente
        """
        try:
            print("⏳ Esperando a que Streamlit cargue...")
            
            # Esperar a que aparezca el contenido principal
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stApp']"))
            )
            
            # Esperar un poco más para que los datos se carguen
            time.sleep(3)
            
            print("✅ Dashboard cargado correctamente")
            return True
            
        except TimeoutException:
            print("⚠️ Timeout esperando que Streamlit cargue")
            return False
    
    def take_screenshot(self, description="dashboard"):
        """
        Toma screenshot del estado actual del dashboard
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/{description}_{timestamp}.png"
            
            # Crear directorio si no existe
            os.makedirs("screenshots", exist_ok=True)
            
            self.driver.save_screenshot(filename)
            self.screenshot_count += 1
            
            print(f"📸 Screenshot guardado: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error tomando screenshot: {e}")
            return None
    
    def refresh_and_monitor(self):
        """
        Refresca el dashboard y monitorea cambios
        """
        print(f"🔄 Refrescando dashboard... (cada {self.refresh_interval}s)")
        
        while self.is_running:
            try:
                # Refrescar página
                self.driver.refresh()
                
                # Esperar a que cargue
                if self.wait_for_streamlit_load(timeout=15):
                    
                    # Tomar screenshot del estado actual
                    self.take_screenshot(f"refresh_{self.screenshot_count}")
                    
                    # Verificar si hay errores en la consola
                    self.check_console_errors()
                    
                    print(f"✅ Dashboard actualizado - {datetime.now().strftime('%H:%M:%S')}")
                    
                else:
                    print("⚠️ El dashboard no cargó correctamente después del refresh")
                
                # Esperar antes del próximo refresh
                time.sleep(self.refresh_interval)
                
            except WebDriverException as e:
                print(f"❌ Error durante el refresh: {e}")
                break
            except KeyboardInterrupt:
                print("\n🛑 Refresh automático interrumpido por el usuario")
                break
    
    def check_console_errors(self):
        """
        Verifica errores en la consola del navegador
        """
        try:
            logs = self.driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']
            
            if errors:
                print(f"⚠️ Se encontraron {len(errors)} errores en la consola:")
                for error in errors[-3:]:  # Mostrar solo los últimos 3
                    print(f"   - {error['message']}")
        except:
            pass  # Algunos drivers no soportan logs
    
    def interactive_session(self):
        """
        Sesión interactiva para desarrollo iterativo
        """
        print("\n🎯 MODO DESARROLLO ITERATIVO ACTIVADO")
        print("=" * 50)
        print("Comandos disponibles:")
        print("  r - Refrescar dashboard manualmente")
        print("  s - Tomar screenshot")
        print("  t - Cambiar a pestaña específica")
        print("  q - Salir")
        print("=" * 50)
        
        while self.is_running:
            try:
                command = input("\n📝 Comando (r/s/t/q): ").lower().strip()
                
                if command == 'q':
                    print("🛑 Cerrando sesión...")
                    break
                    
                elif command == 'r':
                    print("🔄 Refrescando dashboard...")
                    self.driver.refresh()
                    if self.wait_for_streamlit_load():
                        print("✅ Dashboard refrescado")
                    
                elif command == 's':
                    description = input("📸 Descripción del screenshot: ").strip() or "manual"
                    self.take_screenshot(description)
                    
                elif command == 't':
                    self.switch_tabs_interactive()
                    
                else:
                    print("❓ Comando no reconocido")
                    
            except KeyboardInterrupt:
                print("\n🛑 Sesión interrumpida")
                break
    
    def switch_tabs_interactive(self):
        """
        Permite cambiar entre pestañas del dashboard interactivamente
        """
        try:
            # Encontrar las pestañas disponibles
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "[data-baseweb='tab']")
            
            if tabs:
                print(f"📋 Pestañas encontradas ({len(tabs)}):")
                for i, tab in enumerate(tabs):
                    print(f"  {i+1}. {tab.text}")
                
                try:
                    choice = int(input("Selecciona pestaña (número): ")) - 1
                    if 0 <= choice < len(tabs):
                        tabs[choice].click()
                        time.sleep(2)  # Esperar a que cargue el contenido
                        print(f"✅ Cambiado a pestaña: {tabs[choice].text}")
                    else:
                        print("❌ Número de pestaña inválido")
                except ValueError:
                    print("❌ Por favor ingresa un número válido")
            else:
                print("❓ No se encontraron pestañas en el dashboard")
                
        except Exception as e:
            print(f"❌ Error cambiando pestañas: {e}")
    
    def start_viewing(self, mode="interactive"):
        """
        Inicia la visualización del dashboard
        
        Args:
            mode: "interactive" para modo interactivo, "auto" para auto-refresh
        """
        try:
            self.setup_driver()
            
            print(f"🌐 Navegando a: {self.app_url}")
            self.driver.get(self.app_url)
            
            if not self.wait_for_streamlit_load():
                print("❌ No se pudo cargar el dashboard")
                return
                
            # Tomar screenshot inicial
            self.take_screenshot("initial_load")
            
            self.is_running = True
            
            if mode == "auto":
                # Iniciar auto-refresh en hilo separado
                refresh_thread = threading.Thread(target=self.refresh_and_monitor, daemon=True)
                refresh_thread.start()
                
                print(f"🤖 Auto-refresh cada {self.refresh_interval} segundos activado")
                print("Presiona Ctrl+C para detener...")
                
                try:
                    while self.is_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Auto-refresh detenido")
                    
            elif mode == "interactive":
                self.interactive_session()
            
        except Exception as e:
            print(f"❌ Error durante la visualización: {e}")
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Limpia recursos y cierra el navegador
        """
        self.is_running = False
        
        if self.driver:
            print("🧹 Cerrando navegador...")
            self.driver.quit()
            
        print(f"📊 Sesión completada - {self.screenshot_count} screenshots tomados")


def main():
    """
    Función principal con argumentos mejorados
    """
    print("🚀 DASHBOARD VIEWER - DESARROLLO ITERATIVO")
    print("=" * 50)
    
    # Configuración por defecto
    app_url = "http://localhost:8501"
    mode = "interactive"
    refresh_interval = 30
    
    # Procesar argumentos
    if len(sys.argv) > 1:
        app_url = sys.argv[1]
    
    if len(sys.argv) > 2:
        if sys.argv[2] == "auto":
            mode = "auto"
        elif sys.argv[2] == "interactive":
            mode = "interactive"
    
    if len(sys.argv) > 3:
        try:
            refresh_interval = int(sys.argv[3])
        except ValueError:
            print("⚠️ Intervalo de refresh inválido, usando 30 segundos")
    
    print(f"📊 URL: {app_url}")
    print(f"🎛️ Modo: {mode}")
    if mode == "auto":
        print(f"⏱️ Refresh cada: {refresh_interval} segundos")
    
    # Iniciar viewer
    viewer = DashboardViewer(app_url, refresh_interval)
    viewer.start_viewing(mode)


if __name__ == "__main__":
    main()
