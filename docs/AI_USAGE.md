# Registro de uso de IA

El 19 de noviembre de 2026, Codex preparó el paquete y la documentación del banco ROS 2 en `ros2_ws/src/robot_locomocion/bench_2wd/`. El responsable suministró el montaje y la referencia de calibración. La verificación de software y sus límites se entregan con el cambio. El ensayo físico y la revisión humana quedan pendientes.

En esta etapa se utilizó Codex para diseñar e implementar verificadores locales, pruebas y esta documentación. La revisión humana, los acuerdos entre equipos y la aceptación del cambio están pendientes. Las verificaciones ejecutadas y sus limitaciones se informan en la entrega; la referencia estructurada figura en `ai_usage.json`.

También se utilizó Codex para preparar el workflow de CI y su documentación. La ejecución en GitHub, la revisión humana y la aceptación siguen pendientes hasta contar con evidencia real.

La primera ejecución del PR #2 completó estáticos y resumen; el job ROS omitió compilación y pruebas por no haber paquetes. Codex preparó correcciones de la puerta de pruebas ROS y una propuesta de integración posterior; su revisión humana y evidencia de ejecución actualizada quedan pendientes.

La segunda ejecución del PR demostró el fallo y la corrección en el paquete temporal de CI; la validación ROS del robot y la revisión humana siguen pendientes.

Codex asistió en la estructura documental de los subsistemas y el entorno de referencia; los requisitos fueron suministrados por el responsable y la revisión humana está pendiente.

Codex asistió en la corrección del estado de CI del README principal solicitada por el responsable; la revisión humana está pendiente.

Codex asistió en la política de sincronización y verificaciones Git; revisión humana y adopción pendientes.

Codex asistió en la clasificación de rutas y el procedimiento de sincronización solicitado; revisión humana pendiente.

Codex asistió en los cambios de nomenclatura, CI, verificador de contexto Git, pruebas y documentación de PhysalisHarvest. El responsable definió los requisitos y conserva la revisión e integración. Los resultados se registran en el PR de migración.

El 19 de noviembre de 2026, Codex asistió en el banco 2WD, la captura y el análisis puntual de calibración, el transporte ROS/USB, los sketches y clientes de diagnóstico, y la consolidación de los registros textuales. El operador confirmó el cableado declarado, supervisó la alimentación y el corte, preparó las mediciones y observó el giro. [Resultados y límites](../firmware/bench_2wd/README.md).
