# Instrucciones: Locomoción

La política general está en [AGENTS.md](../../../AGENTS.md); las [interfaces propuestas](../../../docs/interfaces/contratos-ros2.md) aún requieren acuerdo. Las instrucciones locales la complementan; mantienen sus reglas de seguridad, IA, licencias y revisión.

## Alcance

Responsabilidad: plataforma móvil, desplazamiento, localización, control y seguridad. No asumir que la plataforma puede moverse o navegar; no controla el manipulador ni decide el objetivo visual.

## Trabajo y evidencia

- Documentar condiciones para permitir, detener o rechazar movimientos, límites, vigencia, supervisión y parada segura. No ejecutar desplazamientos físicos no autorizados.
- Acuerde cambios compartidos con los equipos afectados antes de implementar contratos. No convierta recepción de datos en autorización de movimiento.
- Conserve trazabilidad de IA y licencias según la política general; no incorpore materiales externos sin comprobar derechos.
- Documente entorno, comandos, evidencia, fallos y limitaciones; distinga MOCK, simulación y pruebas físicas. No afirme validación sin criterios y evidencia.
- Use ramas y PR revisados según la política general; no altere experimentos o trabajo ajeno.
