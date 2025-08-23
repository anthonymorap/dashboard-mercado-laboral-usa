"""
Sistema de Desarrollo Iterativo Autónomo
Claude puede hacer cambios, probarlos automáticamente y continuar sin intervención
"""

import os
import time
import json
import subprocess
import shutil
from datetime import datetime
from autonomous_viewer import AutonomousViewer

class IterativeDeveloper:
    """
    Sistema que permite a Claude hacer cambios al código y verificarlos automáticamente
    """
    
    def __init__(self):
        self.viewer = AutonomousViewer()
        self.iteration_count = 0
        self.development_log = []
        self.backup_files = {}
        
    def backup_current_state(self):
        """
        Hace backup del estado actual antes de hacer cambios
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backups/iteration_{self.iteration_count}_{timestamp}"
            
            os.makedirs(backup_dir, exist_ok=True)
            
            # Archivos principales a respaldar
            files_to_backup = [
                'dashboard.py',
                'config.py', 
                'data_collector.py',
                'requirements.txt'
            ]
            
            backed_up = []
            for file in files_to_backup:
                if os.path.exists(file):
                    shutil.copy2(file, os.path.join(backup_dir, file))
                    backed_up.append(file)
            
            self.backup_files[self.iteration_count] = {
                'directory': backup_dir,
                'files': backed_up,
                'timestamp': timestamp
            }
            
            print(f"💾 Backup creado: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return None
    
    def make_development_change(self, change_description, file_changes):
        """
        Hace cambios específicos al código
        
        Args:
            change_description: Descripción del cambio
            file_changes: Dict con {archivo: nuevo_contenido}
        """
        try:
            print(f"🔧 Aplicando cambio: {change_description}")
            
            changes_applied = []
            
            for filename, new_content in file_changes.items():
                if os.path.exists(filename):
                    # Leer contenido actual para logging
                    with open(filename, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                    
                    # Escribir nuevo contenido
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    changes_applied.append({
                        'file': filename,
                        'old_size': len(old_content),
                        'new_size': len(new_content),
                        'changed': old_content != new_content
                    })
                    
                    print(f"   ✏️ Modificado: {filename}")
            
            # Log del cambio
            change_log = {
                'iteration': self.iteration_count,
                'timestamp': datetime.now().isoformat(),
                'description': change_description,
                'files_changed': changes_applied
            }
            
            self.development_log.append(change_log)
            print(f"✅ Cambios aplicados: {len(changes_applied)} archivos")
            
            return True
            
        except Exception as e:
            print(f"❌ Error aplicando cambios: {e}")
            return False
    
    def test_changes_automatically(self):
        """
        Prueba automáticamente los cambios realizados
        """
        try:
            print("🧪 Probando cambios automáticamente...")
            
            # Ejecutar análisis autónomo completo
            result = self.viewer.run_autonomous_session()
            
            if result:
                print("✅ Test automático completado exitosamente")
                return {
                    'success': True,
                    'screenshots': self.viewer.screenshot_counter,
                    'analysis': self.viewer.analysis_log
                }
            else:
                print("❌ Test automático falló")
                return {
                    'success': False,
                    'error': 'Autonomous analysis failed'
                }
                
        except Exception as e:
            print(f"❌ Error en test automático: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def rollback_changes(self, iteration):
        """
        Revierte cambios a una iteración anterior
        """
        try:
            if iteration not in self.backup_files:
                print(f"❌ No existe backup para iteración {iteration}")
                return False
            
            backup_info = self.backup_files[iteration]
            backup_dir = backup_info['directory']
            
            print(f"🔄 Revirtiendo a iteración {iteration}...")
            
            restored = []
            for file in backup_info['files']:
                backup_file = os.path.join(backup_dir, file)
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, file)
                    restored.append(file)
            
            print(f"✅ Revertidos {len(restored)} archivos")
            return True
            
        except Exception as e:
            print(f"❌ Error revirtiendo cambios: {e}")
            return False
    
    def run_development_cycle(self, changes_to_make):
        """
        Ejecuta un ciclo completo de desarrollo
        
        Args:
            changes_to_make: Lista de cambios a realizar
            Formato: [{'description': str, 'files': {filename: content}}]
        """
        print("🚀 INICIANDO CICLO DE DESARROLLO ITERATIVO")
        print("=" * 50)
        
        # Test inicial
        print("0️⃣ Ejecutando test baseline...")
        baseline_result = self.test_changes_automatically()
        
        for change in changes_to_make:
            self.iteration_count += 1
            
            print(f"\n🔄 ITERACIÓN {self.iteration_count}")
            print("-" * 30)
            
            # 1. Backup
            backup_dir = self.backup_current_state()
            if not backup_dir:
                print("❌ No se pudo crear backup, abortando iteración")
                continue
            
            # 2. Aplicar cambios
            success = self.make_development_change(
                change['description'], 
                change['files']
            )
            
            if not success:
                print("❌ Error aplicando cambios, continuando...")
                continue
            
            # 3. Probar cambios
            test_result = self.test_changes_automatically()
            
            # 4. Evaluar resultado
            if test_result['success']:
                print(f"✅ Iteración {self.iteration_count} EXITOSA")
            else:
                print(f"❌ Iteración {self.iteration_count} FALLÓ")
                
                # Opcional: Revertir automáticamente si falla
                # self.rollback_changes(self.iteration_count - 1)
            
            # 5. Log resultado
            iteration_result = {
                'iteration': self.iteration_count,
                'change': change['description'],
                'test_result': test_result,
                'backup': backup_dir
            }
            
            self.save_iteration_log(iteration_result)
            
            print(f"📊 Iteración {self.iteration_count} completada")
        
        print("\n🎉 CICLO DE DESARROLLO COMPLETADO")
        self.save_final_report()
    
    def save_iteration_log(self, iteration_result):
        """
        Guarda log de la iteración
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"development_logs/iteration_{iteration_result['iteration']}_{timestamp}.json"
            
            os.makedirs("development_logs", exist_ok=True)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(iteration_result, f, indent=2, ensure_ascii=False)
                
            print(f"📝 Log guardado: {log_file}")
            
        except Exception as e:
            print(f"❌ Error guardando log: {e}")
    
    def save_final_report(self):
        """
        Guarda reporte final del desarrollo
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"development_logs/final_report_{timestamp}.json"
            
            report = {
                'session_info': {
                    'timestamp': timestamp,
                    'total_iterations': self.iteration_count,
                    'total_changes': len(self.development_log)
                },
                'development_log': self.development_log,
                'backups': self.backup_files
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"📋 REPORTE FINAL: {report_file}")
            print(f"📊 Iteraciones completadas: {self.iteration_count}")
            
        except Exception as e:
            print(f"❌ Error guardando reporte final: {e}")

def main():
    """
    Ejemplo de uso del sistema iterativo
    """
    developer = IterativeDeveloper()
    
    # Ejemplo de cambios a realizar
    sample_changes = [
        {
            'description': 'Mejorar colores del dashboard',
            'files': {
                'config.py': '# Cambios de configuración aquí'
            }
        }
    ]
    
    # Para uso real, Claude llamaría esto con cambios específicos
    # developer.run_development_cycle(sample_changes)
    
    print("🤖 Sistema de Desarrollo Iterativo listo")
    print("Claude puede usar este sistema para desarrollo autónomo")

if __name__ == "__main__":
    main()