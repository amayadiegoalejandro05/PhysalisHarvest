# Propuesta de CI para revisión

El workflow se ejecuta en PR hacia `main`, `vision`, `brazo` y `locomocion`, en push a estas ramas y manualmente. El job estático reutiliza los verificadores y sus pruebas, con Python y PyYAML en un entorno aislado del runner. Las acciones se fijan por commit y el token tiene únicamente permiso de lectura de contenido.

El job ROS usa la imagen `ros:jazzy-ros-base` fijada al digest observado en la primera ejecución de Actions. Si no hay `package.xml` en `ros2_ws/src`, muestra **SKIP** y no afirma validación ROS. Si aparecen manifiestos, instala colcon y rosdep, resuelve dependencias declaradas, compila, inspecciona definiciones `msg`, `srv` y `action`, ejecuta `colcon test --return-code-on-test-failure` y conserva logs y resultados XML incluso si falla. Se informa el inventario por subsistema, instalación y casos con resultados; instalación o casos registrados no implican validación. Apt y rosdep siguen resolviendo versiones variables, por lo que no se garantiza reproducibilidad bit a bit.

La puerta ROS aislada genera un paquete CMake temporal ajeno al robot: comprueba que una prueba intencionalmente fallida haga fallar el comando compartido y que la prueba corregida pase. Guarda ambos logs. La detección de resultados por paquete se basa en XML de `build/<paquete>/test_results`; si un sistema de pruebas no genera ese formato aparece sin casos registrados y requiere revisión manual. Los paquetes fuera de los cuatro directorios previstos se enumeran, pero no se asignan a un subsistema.

Los contratos compartidos siguen siendo propuestas. Las pruebas de tipos, unidades, marcos, tiempos, estados y compatibilidad productor/consumidor se incorporarán cuando los equipos aprueben y construyan las interfaces. La CI no ejecuta hardware físico. La inspección de tipos por sí sola no verifica semántica ni seguridad.

En GitHub, abra el PR y seleccione **Checks** para ver cada job; o abra **Actions**, seleccione la ejecución y revise el resumen, los pasos y los artefactos `informe-estatico` y, cuando aplique, `logs-ros`. El resumen distingue el SHA fuente del PR, el SHA base y el SHA evaluado, que puede ser el merge temporal. Ante un fallo, revise el primer paso fallido y su log, corrija el problema en la rama y repita. Si un job se omite o termina antes de detectar paquetes, revise su estado y no lo interprete como validación.

Las acciones y sus imágenes externas necesitan red y servicios disponibles. No se han configurado checks obligatorios ni protecciones con este cambio; primero se requiere observar una ejecución real en GitHub y revisión de los equipos.

## Política propuesta de checks

Tras comprobar ejecuciones reales y revisar su estabilidad, considerar obligatorios por separado **Verificación estática y pruebas** y **Prueba controlada de puerta ROS**. El job **ROS 2 Jazzy** debe informar SKIP cuando no existan paquetes; considerarlo obligatorio para detectar fallos de infraestructura y compilación solo tras ensayar la ruta con paquetes reales, sin interpretar un SKIP como validación. El **Resumen y trazabilidad** es informativo y no debe ser el único check obligatorio. La conformidad de contratos seguirá informativa o ausente hasta acordar interfaces y pruebas. Esta propuesta no modifica protecciones.

En la primera ejecución del PR #2 (commit fuente `e904f6a`, base `634030c`, merge temporal `0677f3b`) los jobs estático y resumen pasaron, y ROS omitió compilación y pruebas porque no había paquetes. Esa ejecución no probó la puerta de errores ROS. Las correcciones posteriores necesitan nueva evidencia en Actions.
