"""
Sistema Autónomo de Visualización para Desarrollo Iterativo
Permite que Claude desarrolle de forma completamente independiente
"""

import time
import os
import subprocess
import threading
import json
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class AutonomousViewer:
    """
    Visualizador completamente autónomo para desarrollo iterativo
    Claude puede hacer cambios y ver resultados sin intervención humana
    """
    
    def __init__(self, app_url="http://localhost:8501"):
        self.app_url = app_url
        self.driver = None
        self.is_running = False
        self.screenshot_counter = 0
        self.analysis_log = []
        self.streamlit_process = None
        
    def start_streamlit_server(self):
        """
        Inicia el servidor Streamlit automáticamente
        """
        try:
            print("INICIANDO Iniciando servidor Streamlit automáticamente...")
            
            # Comando para iniciar Streamlit
            cmd = [
                "venv_mercado_laboral/Scripts/python.exe", 
                "-m", "streamlit", "run", "dashboard.py", 
                "--server.port=8501",
                "--server.headless=true",
                "--browser.gatherUsageStats=false"
            ]
            
            # Iniciar proceso en background
            self.streamlit_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            print("⏳ Esperando a que Streamlit se inicie...")
            time.sleep(8)  # Dar tiempo para que inicie
            
            print("✅ Servidor Streamlit iniciado")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando Streamlit: {e}")
            return False
    
    def setup_headless_driver(self):
        """
        Configura Chrome en modo headless para operación autónoma
        """
        print("🤖 Configurando Chrome en modo autónomo...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Sin ventana visible
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--silent")
        
        service = Service(ChromeDriverManager().install())
        service.log_path = os.devnull  # Suprimir logs de ChromeDriver
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome configurado en modo autónomo")
        
    def wait_for_dashboard_load(self, timeout=30):
        """
        Espera a que el dashboard cargue completamente
        """
        try:
            print("⏳ Esperando carga del dashboard...")
            
            # Esperar elemento principal de Streamlit
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stApp']"))
            )
            
            # Esperar a que se carguen los datos
            time.sleep(5)
            
            print("✅ Dashboard cargado completamente")
            return True
            
        except TimeoutException:
            print("⚠️ Timeout esperando carga del dashboard")
            return False
    
    def capture_full_dashboard(self, description="autonomous"):
        """
        Captura screenshot completo del dashboard
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshots/autonomous_{description}_{timestamp}.png"
            
            os.makedirs("screenshots", exist_ok=True)
            
            # Capturar screenshot
            self.driver.save_screenshot(filename)
            self.screenshot_counter += 1
            
            # También obtener el HTML para análisis
            html_content = self.driver.page_source
            html_filename = f"screenshots/page_source_{timestamp}.html"
            
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📸 Screenshot capturado: {filename}")
            
            return {
                'screenshot': filename,
                'html': html_filename,
                'timestamp': timestamp,
                'description': description
            }
            
        except Exception as e:
            print(f"❌ Error capturando screenshot: {e}")
            return None
    
    def analyze_dashboard_content(self):
        """
        Analiza el contenido actual del dashboard
        """
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'url': self.driver.current_url,
                'title': self.driver.title,
                'tabs': [],
                'errors': [],
                'metrics': []
            }
            
            # Detectar pestañas disponibles
            try:
                tabs = self.driver.find_elements(By.CSS_SELECTOR, "[data-baseweb='tab']")
                analysis['tabs'] = [tab.text for tab in tabs if tab.text.strip()]
            except:
                pass
            
            # Detectar métricas visibles
            try:
                metrics = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='metric-container']")
                for metric in metrics[:5]:  # Primeras 5 métricas
                    try:
                        analysis['metrics'].append({
                            'text': metric.text,
                            'visible': metric.is_displayed()
                        })
                    except:
                        pass
            except:
                pass
            
            # Verificar errores en consola
            try:
                logs = self.driver.get_log('browser')
                errors = [log for log in logs if log['level'] == 'SEVERE']
                analysis['errors'] = [error['message'] for error in errors[-3:]]
            except:
                pass
            
            self.analysis_log.append(analysis)
            print(f"📊 Análisis completado - Pestañas: {len(analysis['tabs'])}, Métricas: {len(analysis['metrics'])}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error en análisis: {e}")
            return None
    
    def navigate_through_tabs(self):
        """
        Navega automáticamente por todas las pestañas
        """
        try:
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "[data-baseweb='tab']")
            
            if not tabs:
                print("ℹ️ No se encontraron pestañas para navegar")
                return
            
            print(f"🔄 Navegando por {len(tabs)} pestañas...")
            
            for i, tab in enumerate(tabs):
                try:
                    tab_name = tab.text or f"Tab_{i+1}"
                    print(f"   📂 Navegando a: {tab_name}")
                    
                    # Hacer clic en la pestaña
                    tab.click()
                    time.sleep(3)  # Esperar carga
                    
                    # Capturar screenshot de esta pestaña
                    self.capture_full_dashboard(f"tab_{tab_name}")
                    
                    # Analizar contenido
                    self.analyze_dashboard_content()
                    
                except Exception as e:
                    print(f"   ⚠️ Error navegando pestaña {i+1}: {e}")
            
            print("✅ Navegación por pestañas completada")
            
        except Exception as e:
            print(f"❌ Error navegando pestañas: {e}")
    
    def save_analysis_report(self):
        """
        Guarda reporte completo del análisis
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"analysis/dashboard_analysis_{timestamp}.json"
            
            os.makedirs("analysis", exist_ok=True)
            
            report = {
                'session_info': {
                    'timestamp': timestamp,
                    'screenshots_taken': self.screenshot_counter,
                    'tabs_analyzed': len(set(tab for analysis in self.analysis_log for tab in analysis.get('tabs', []))),
                    'url': self.app_url
                },
                'analysis_log': self.analysis_log
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Reporte guardado: {report_file}")
            return report_file
            
        except Exception as e:
            print(f"❌ Error guardando reporte: {e}")
            return None
    
    def autonomous_analysis_cycle(self):
        """
        Ciclo completo de análisis autónomo
        """
        print("🤖 INICIANDO ANÁLISIS AUTÓNOMO")
        print("=" * 50)
        
        try:
            # 1. Capturar estado inicial
            print("1️⃣ Capturando estado inicial...")
            self.capture_full_dashboard("initial_state")
            self.analyze_dashboard_content()
            
            # 2. Navegar por todas las pestañas
            print("2️⃣ Navegando por todas las pestañas...")
            self.navigate_through_tabs()
            
            # 3. Volver a la primera pestaña
            print("3️⃣ Volviendo al estado inicial...")
            self.driver.get(self.app_url)
            self.wait_for_dashboard_load(timeout=15)
            self.capture_full_dashboard("final_state")
            
            # 4. Generar reporte
            print("4️⃣ Generando reporte de análisis...")
            report_file = self.save_analysis_report()
            
            print("✅ ANÁLISIS AUTÓNOMO COMPLETADO")
            print(f"📊 Screenshots: {self.screenshot_counter}")
            print(f"📋 Reporte: {report_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en análisis autónomo: {e}")
            return False
    
    def run_autonomous_session(self):
        """
        Ejecuta sesión completamente autónoma
        """
        try:
            print("INICIANDO INICIANDO SESIÓN AUTÓNOMA")
            print("=" * 40)
            
            # 1. Iniciar Streamlit
            if not self.start_streamlit_server():
                return False
            
            # 2. Configurar driver
            self.setup_headless_driver()
            
            # 3. Navegar al dashboard
            print(f"🌐 Navegando a: {self.app_url}")
            self.driver.get(self.app_url)
            
            # 4. Esperar carga
            if not self.wait_for_dashboard_load():
                print("❌ No se pudo cargar el dashboard")
                return False
            
            # 5. Ejecutar análisis completo
            self.is_running = True
            success = self.autonomous_analysis_cycle()
            
            return success
            
        except Exception as e:
            print(f"❌ Error en sesión autónoma: {e}")
            return False
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Limpia todos los recursos
        """
        print("🧹 Limpiando recursos...")
        
        self.is_running = False
        
        # Cerrar navegador
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        # Terminar proceso Streamlit
        if self.streamlit_process:
            try:
                self.streamlit_process.terminate()
                self.streamlit_process.wait(timeout=5)
            except:
                try:
                    self.streamlit_process.kill()
                except:
                    pass
        
        print("✅ Recursos liberados")

def main():
    """
    Función principal para ejecución autónoma
    """
    print("SISTEMA AUTONOMO DE VISUALIZACION")
    print("=" * 40)
    print("Claude puede desarrollar completamente independiente")
    print("Sin intervencion humana requerida")
    print("=" * 40)
    
    viewer = AutonomousViewer()
    success = viewer.run_autonomous_session()
    
    if success:
        print("\n🎉 SESIÓN AUTÓNOMA EXITOSA")
        print("📁 Revisa las carpetas 'screenshots/' y 'analysis/' para resultados")
    else:
        print("\n❌ SESIÓN AUTÓNOMA FALLÓ")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())