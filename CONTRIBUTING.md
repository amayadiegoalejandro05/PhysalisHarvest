# Contribuir

## Flujo de trabajo

1. Actualice sus referencias con `git fetch origin`. Parta de `origin/feat/vision`, `origin/feat/arm`, `origin/feat/locomotion` u `origin/feat/2WD`, según el subsistema; cree una rama temporal descriptiva, por ejemplo `git switch -c feature/vision-seleccion origin/feat/vision`.
2. Realice cambios acotados y commits descriptivos en inglés técnico, por ejemplo `git commit -m "docs(vision): describe selection criteria"`. No incluya secretos, entornos, datos ni artefactos pesados sin política acordada.
3. Sincronice periódicamente su rama de subsistema con `main`: actualice referencias y proponga mediante PR los cambios de `main` hacia la rama del subsistema. Resuelva conflictos y coordine cambios compartidos. Evite reescribir historial compartido.
4. Publique su rama temporal y abra un PR hacia su rama de subsistema. Complete la plantilla, describa pruebas y limitaciones y solicite revisión. Para integrar en `main`, abra un PR desde la rama de subsistema, solicite revisión y resuelva conversaciones y conflictos antes del merge. Nunca integre trabajo directamente en `main` ni active merge automático sin revisión.
5. Acuerde con los tres equipos cualquier cambio a `robot_interfaces`, marcos, unidades o semántica. Registre decisiones y compatibilidad antes de implementar contratos.

## Evidencia y datos

Documente comandos, entorno, resultados, fallos y límites de pruebas reproducibles. No confunda simulación con validación física. Mantenga credenciales fuera de Git; un `.gitignore` no protege secretos ya rastreados. Datasets, bolsas ROS, grabaciones y pesos requieren una política compartida de almacenamiento, acceso, versiones y licencias antes de incorporarlos.

## Integración continua

Los PR hacia las ramas principales y los push a ellas ejecutan la propuesta de CI. En el PR consulte **Checks**; en **Actions**, abra la ejecución, revise el resumen, cada job y sus artefactos. Un job ROS verde con `SKIP` indica ausencia de paquetes, no validación. Ante un fallo, revise el primer paso fallido y sus logs, corrija el cambio y vuelva a ejecutar. Los comandos locales y límites están en [verificación local](docs/pruebas/verificacion-local.md) y [CI](docs/pruebas/ci.md).

## Comprobación antes de commit y PR

Siga la sección 11 de [AGENTS.md](AGENTS.md). Verifique `origin`, estado y SHA; cuando esté autorizado y sea posible ejecute `git fetch origin` y después `python scripts/check_git_context.py --target feat/vision --subsystem vision` (ajuste destino y subsistema). Repita con `main` para cambios transversales. Registre adelantados, atrasados, conflictos posibles, archivos compartidos y si la información es local o actualizada. Estar atrasado no obliga a hacer merge antes de cada commit; antes de integrar, revise compatibilidad y solicite revisión.

Use `feature/`, `fix/`, `experiment/`, `test/` y `chore/` para ramas temporales. Los identificadores `vision`, `arm`, `locomotion` y `2WD` indican el destino del subsistema. Para cambios transversales, parta de `main` y especifique `--target main`. La incorporación de resultados 2WD a `feat/locomotion` o `main` exige revisión, pruebas y aprobación explícita. Los PR de subsistemas hacia `main` requieren CI aplicable, SHA documentados y revisión; contratos requieren acuerdo de productores y consumidores. La comprobación local y las instrucciones no son protección GitHub: las reglas administrativas son las que pueden exigir PR, CI, revisión, actualización, conversaciones resueltas y prohibición de force push. Véase [verificación local](docs/pruebas/verificacion-local.md).
