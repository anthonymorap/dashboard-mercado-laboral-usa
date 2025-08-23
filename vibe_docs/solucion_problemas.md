# Guía de Solución de Problemas

## Formato de Registro de Errores
Para cada error, documenta:

### [Error de Codificación Unicode]
**Fecha:** 2025-08-23
**Mensaje de Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 0: character maps to <undefined>
```

**Contexto:** Al ejecutar scripts Python con emojis en Windows con encoding cp1252
**Causa Raíz:** Windows usa codificación cp1252 por defecto que no soporta caracteres Unicode como emojis
**Solución:**
1. Reemplazar todos los emojis por texto equivalente
2. Usar `print("texto")` en lugar de `print("🎉 texto")`
3. Alternativa: Configurar UTF-8 pero puede causar otros problemas

**Prevención:** Evitar emojis en scripts de producción en Windows
**Archivos Relacionados:** test_apis.py

---

## API Keys Requeridas

### [Configuración de FRED API Key]
**Fecha:** 2025-08-23
**Contexto:** Para obtener datos del Federal Reserve Economic Data
**Pasos de configuración:**
1. Ir a https://fred.stlouisfed.org/docs/api/api_key.html
2. Crear cuenta gratuita en FRED
3. Solicitar API key
4. Actualizar .env con `FRED_API_KEY=tu_clave_aqui`

**Estado:** Pendiente - necesita configuración manual del usuario

---

### [Configuración opcional de BLS API Key]  
**Fecha:** 2025-08-23
**Contexto:** Para aumentar límites de la API de Bureau of Labor Statistics
**Pasos:**
1. Ir a https://www.bls.gov/developers/
2. Registrarse para API key (opcional pero recomendado)
3. Actualizar .env con `BLS_API_KEY=tu_clave_aqui`

**Estado:** Opcional - funciona sin key pero con límites

---