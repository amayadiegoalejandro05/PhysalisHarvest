# Propuesta de verificación local

Estado: implementación inicial para revisión de los equipos. Las comprobaciones son estáticas y de contexto Git; no demuestran funcionamiento de ROS, seguridad física ni ausencia completa de secretos. No se requiere ROS ni se instala software.

Desde la raíz del repositorio, en PowerShell:

```powershell
python scripts/check_repository.py --json reporte-repositorio.json
python scripts/check_git_context.py --target main --json reporte-git.json
python -m unittest discover -s tests -p "test_*.py" -v
```

En Ubuntu o WSL2:

```bash
python3 scripts/check_repository.py --json /tmp/reporte-repositorio.json
python3 scripts/check_git_context.py --target main --json /tmp/reporte-git.json
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

En PowerShell se recomienda guardar los informes fuera del repositorio o eliminarlos manualmente después de revisarlos. `--json` es opcional. Las pruebas usan repositorios temporales. Los comandos no hacen fetch ni modifican referencias. Para una comparación actualizada, verificar primero `origin` y ejecutar `git fetch origin` con autorización. Use `--target vision`, `brazo`, `locomocion` o `main` según el destino, y opcionalmente `--subsystem vision|brazo|locomocion`.

Cada comprobación produce ID, PASS, FAIL o SKIP, explicación y acción. Un FAIL devuelve 1; una ejecución sin FAIL devuelve 0, incluso con SKIP. Errores de invocación o escritura del informe también producen salida distinta de cero. Un árbol con archivos no rastreados, incluido AGENTS.md local, se informa como FAIL en contexto Git para que se revise; no implica que sea indebido. Las comparaciones son contra referencias locales y no certifican su vigencia remota. En PR de GitHub Actions se identifica el HEAD separado y la comparación describe el commit comprobado, que puede ser un merge temporal, no la divergencia de la rama fuente.

El análisis YAML se omite si falta PyYAML; no instalarlo automáticamente. Los enlaces se comprueban de forma básica, sin validar anclas o todos los formatos Markdown. El control de secretos es heurístico, no muestra valores y no sustituye una herramienta especializada ni la revisión de Git. Se inspeccionan archivos rastreados y no ignorados; no se recorre el historial ni se verifica contenido binario. Se señalan archivos mayores de 10 MiB como criterio preventivo. XML se comprueba de forma básica, no se ejecuta `colcon` ni se valida el esquema completo ROS. La detección de correspondencia entre rama y subsistema depende del nombre y no prueba propiedad o procedencia.

## Sincronización y limitaciones

El verificador compara destino y `origin/main` por separado y clasifica sincronización, atraso o divergencia respecto a referencias locales. Un atraso, cambios locales o conflicto posible se informa como SKIP para no bloquear commits; fallos críticos como origen incorrecto siguen siendo FAIL. La vista de conflictos usa árboles confirmados y es orientativa; no prueba ausencia de conflictos con cambios locales. Los archivos compartidos detectados requieren revisión humana. Los resultados no prueban vigencia del servidor: una actualización explícita de referencias, cuando esté autorizada, precede a la comprobación actual. En PR con HEAD separado se reporta el merge temporal como tal. No hace fetch, merge, reset, rebase ni push.

Propuesta administrativa pendiente: proteger `main` con PR, CI estable, revisión humana, rama actualizada, conversaciones resueltas, bloqueo de force push y eliminación; evaluar excepciones administrativas y revisores disponibles para no bloquear al responsable único. Las reglas no se aplican mediante esta documentación ni por el script.
