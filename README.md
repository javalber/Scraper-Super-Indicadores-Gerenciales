# Scraper Super Indicadores Gerenciales

Monitorea la página de la **Superintendencia Financiera de Colombia** y avisa por
correo cuando se publica un nuevo informe mensual de *Indicadores Gerenciales (NIIF)*.

Todo es **automático**: ya no hay que ajustar la fecha a mano cada vez que llega un
reporte nuevo.

## Cómo funciona

1. Un GitHub Action ([.github/workflows/monitor_super.yml](.github/workflows/monitor_super.yml))
   se ejecuta dos veces al día (08:00 y 14:00 hora Colombia).
2. El script [scrap_sup_ind.py](scrap_sup_ind.py):
   - Descarga la página de la Superfinanciera.
   - Extrae **automáticamente el período más reciente** publicado (el mes/año más
     alto, sin depender del orden de los enlaces en la página).
   - Lo compara con el último mes guardado en [ultimo_mes.txt](ultimo_mes.txt).
3. Si hay un mes nuevo:
   - Envía un correo de aviso.
   - Actualiza `ultimo_mes.txt` y **el propio workflow hace commit del cambio** de
     vuelta al repositorio.

De esta forma el archivo `ultimo_mes.txt` siempre refleja el último informe detectado
sin intervención manual, y el correo de aviso se envía **una sola vez** por cada
informe nuevo.

## Configuración (una sola vez)

- **Secret `GMAIL_APP_PASSWORD`**: en *Settings → Secrets and variables → Actions*,
  crear un secret con la contraseña de aplicación de Gmail de la cuenta remitente.
- **Permisos de Actions**: el workflow ya declara `permissions: contents: write`, que
  es lo que le permite hacer commit automático de `ultimo_mes.txt`. Si el push aún
  fallara, verificar en *Settings → Actions → General → Workflow permissions* que esté
  habilitado **"Read and write permissions"**.
- Los destinatarios y la cuenta remitente se configuran en las constantes al inicio de
  [scrap_sup_ind.py](scrap_sup_ind.py) (`GMAIL_USER`, `DESTINO`).

## Ejecución manual

Se puede lanzar a demanda desde la pestaña **Actions → Monitor Superfinanciera →
Run workflow**, o localmente:

```bash
pip install requests beautifulsoup4
export GMAIL_APP_PASSWORD="tu_app_password"   # en Windows PowerShell: $env:GMAIL_APP_PASSWORD="..."
python scrap_sup_ind.py
```

Al correr localmente, si detecta un mes nuevo actualiza `ultimo_mes.txt` en tu copia
local (tú decides si lo commiteas).

## Archivos

| Archivo | Descripción |
|---|---|
| `scrap_sup_ind.py` | Script de scraping y notificación por correo. |
| `ultimo_mes.txt` | Último período detectado. Lo mantiene actualizado el workflow. |
| `.github/workflows/monitor_super.yml` | Programación y automatización en GitHub Actions. |
