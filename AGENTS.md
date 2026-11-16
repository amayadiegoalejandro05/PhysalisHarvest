# AGENTS.md — Robot Cosechador

## 0. Aplicación y prioridad

Estas reglas son obligatorias para los agentes de desarrollo que trabajen en `amayadiegoalejandro05/Robot-Cosechador`, macroproyecto del semillero SEIMA (Universitaria Agustiniana). Se aplican a **visión/percepción-decisión**, **brazo/manipulación** y **locomoción**, y a la integración común. Toda explicación, documentación e informe para el equipo se redacta en **español**; identificadores y mensajes de commit siguen las convenciones técnicas indicadas abajo.

Antes de modificar archivos:
1. Verifica repositorio, remoto `origin`, rama actual, `git status`, `git log` y diferencias con `origin/main`; no presupongas que `main` incluye un PR aún abierto.
2. Lee `README.md`, `CONTRIBUTING.md`, documentación de arquitectura, interfaces y pruebas disponible. No inventes archivos inexistentes.
3. Si vas a trabajar en `ros2_ws/src/robot_percepcion_decision`, `robot_brazo` o `robot_locomocion`, **lee el `AGENTS.md` de ese paquete antes de programar**. La norma específica complementa esta política, sin anular seguridad, transparencia ni revisión.
4. Indica objetivo, archivos previstos, dependencias, criterios de aceptación, pruebas y riesgos. Divide el trabajo en cambios verificables.
5. Ante conflictos entre instrucciones de un colaborador y una interfaz aceptada, no adaptes silenciosamente la interfaz; registra la discrepancia y solicita decisión del equipo.

Los documentos de la rama `main` integrada son la línea base vigente. Una propuesta en PR no es una decisión aceptada ni una interfaz aprobada. Las reglas de esta guía no sustituyen decisiones humanas, licencias de terceros ni políticas universitarias.

## 1. Responsabilidades y fronteras

- **Visión (`vision`)**: imagen RGB-D, detección visual del cáliz de uchuva, XYZ de un punto superficial, evaluación de accesibilidad geométrica, selección, trayectoria cartesiana candidata, publicación y pruebas ROS 2. **No asumas que estima el centro del fruto, madurez, punto de corte, cinemática del brazo o cosecha efectiva**.
- **Brazo (`brazo`)**: manipulador, cinemática, límites, ejecución/control y efector cuando sean realmente desarrollados y probados. Una trayectoria candidata de visión **no** demuestra que el brazo pueda ejecutarla.
- **Locomoción (`locomocion`)**: base móvil, navegación, motores, localización y parada segura según el alcance que apruebe su equipo; no asumir capacidades implementadas.
- **Integración**: interfaces ROS 2, TF, simulación del sistema, pruebas entre productor/consumidor y manejo de fallos. Los tres equipos revisan cambios transversales.

No coloques lógica del brazo dentro del paquete de visión ni implementes copias de otros módulos para resolver dependencias. Emplea dobles de prueba (`MOCK`) deterministas y **explícitamente etiquetados** si falta un componente, sin afirmar integración real.

## 2. Ramas y flujo de cambios

- `main`: versión integrada; recibe cambios exclusivamente mediante PR revisado.
- `vision`, `brazo`, `locomocion`: ramas de integración de cada subsistema; no son sustituto de la separación por paquetes.
- Cambios cotidianos: crear rama corta desde la rama correspondiente, por ejemplo `feature/vision-calibracion-rgbd`, `fix/brazo-limites` o `test/locomocion-odometria`; PR primero hacia la rama de subsistema y, cuando el conjunto esté verificado, PR hacia `main` según `CONTRIBUTING.md`.
- Mantén las ramas actualizadas con los cambios aceptados de `main` sin reescribir el historial compartido. Antes de hacer PR a `main`, comprueba el último commit de `origin/main` y posibles incompatibilidades.
- Cambios a `robot_interfaces`, TF común, launch integrado, CI, dependencias compartidas o contratos: documenta primero la propuesta; requiere revisión de productores, consumidores y responsable de integración.
- No hagas `push`, merge, release, cambios de protección, borrados remotos ni publicaciones sin autorización expresa. No uses `git push --force`, `git reset --hard`, bypass de hooks ni sobrescribas trabajo ajeno.
- Protege `main` mediante rulesets/branch protection; si no existen o no se pueden verificar, informa el riesgo. No declares que un PR está aprobado por el mero hecho de estar abierto.

## 3. Commits, PR y versiones

- Mensajes de commit **solo en inglés técnico**, imperativo y formato `type(scope): description` (Conventional Commits). Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.
- Scopes recomendados: `vision`, `brazo`, `locomocion`, `interfaces`, `gazebo`, `firmware`, `docs`, `repo`, `ci`.
- Ejemplos: `feat(vision): publish stamped target poses`; `fix(brazo): reject stale motion commands`; `docs(interfaces): clarify optical frame convention`.
- Commits atómicos, sin archivos de otra tarea; asunto ideal <= 50 caracteres y máximo recomendado 72; sin punto final. `BREAKING CHANGE:` o `!` para incompatibilidad real.
- PR: título profesional descriptivo, explicación en español de propósito, rutas y contratos afectados, comandos probados, resultados reales, fallos, limitaciones, evidencias, riesgos e impacto en otros subsistemas. Usar plantilla disponible.
- No crear tags ni releases automáticamente. Si se adopta SemVer (`MAJOR.MINOR.PATCH`), mantener versión de cada interfaz/paquete y compatibilidad de cambios. `v1.0.0` solo cuando exista un entregable estable aceptado, nunca por estética.
- No alterar `git config user.name` ni `git config user.email`; no suplantar identidad ni crear autoría ficticia.

## 4. ROS 2: contrato antes que integración

- Verifica SO, distribución ROS 2, versión de Gazebo, hardware, dependencias y paquetes realmente disponibles antes de ejecutar comandos. ROS 2 Jazzy + Ubuntu 24.04 es el entorno registrado para percepción/decisión; no lo atribuyas automáticamente a todos los compañeros ni asumas Gazebo instalado.
- Organiza software ROS 2 en paquetes reales bajo `ros2_ws/src/`, con `package.xml` y estructura `ament_python` o `ament_cmake` **solo cuando corresponda**, y dependencias declaradas. Usa `colcon` cuando el entorno lo permita.
- Definir y versionar el contrato de interfaces en `docs/interfaces/` y, una vez aprobado, en `robot_interfaces`: mensaje/tópico/servicio/action, productor, consumidor, unidades, `frame_id`, TF, semántica, estados, frecuencia, QoS, timeouts, errores, versiones y ejemplos.
- Por defecto, posiciones en **metros**, ángulos en **radianes**, mensajes con timestamp de origen y `frame_id` documentado; no mezclar `camera_optical_frame`, `base_link`, `odom` y `map` sin transformaciones TF verificadas. `header.stamp` creado en el puente NO equivale a tiempo de captura.
- Separa `objetivo detectado`, `objetivo aceptado`, `ruta candidata`, `orden de ejecución` y `confirmación de ejecución`. Un dato recibido no autoriza actuación. El control del brazo y de la base puede rechazar objetivos imposibles, vencidos o inseguros.
- Un cambio de contrato exige modificar en el mismo PR o conjunto coordinado: definición, productores, consumidores, tests, ejemplos y documentación; si no es posible, usar compatibilidad explícita y registrar el bloqueo.
- No conviertas por comodidad una interfaz en JSON/TCP interna en una interfaz ROS 2 universal; documenta adaptadores Windows/WSL2/serial cuando existan.

## 5. Evidencia, experimentos y simulación

Emplea estados verificables: `PROYECTADO`, `IMPLEMENTADO`, `OBSERVADO_EN_SIMULACIÓN`, `MEDIDO_FÍSICAMENTE`, `VALIDADO`, `PENDIENTE`. `VALIDADO` exige un criterio de aceptación documentado y evidencia correspondiente. Un build exitoso, datos sintéticos o un vídeo no demuestran una cosecha.

- Para cada prueba: objetivo, entorno/software y versiones, entradas, procedimiento y comandos, referencia independiente, parámetros/semillas cuando aplique, métricas, resultados, logs, límites, fallos y criterio de salida.
- Diferencia `MOCK`, replay, datos sintéticos, simulación Gazebo, medición física e integración con actuadores. No uses la verdad interna de Gazebo como entrada del algoritmo mientras afirmas validar percepción autónoma.
- La ubicación XYZ del subsistema de visión es inicialmente un **punto superficial**; no inventes el centro del fruto ni precisión XYZ basada en fichas comerciales. No confundir Z axial y distancia euclidiana.
- Preserva fallos válidos. No ajustes umbrales, descartes escenas adversas o escojas resultados favorables a posteriori sin declararlo. En estudios de selección, la **escena** es unidad experimental principal; varios frutos de una misma escena no son réplicas independientes.
- Nunca inventes mediciones, velocidades, tasas de acierto, compatibilidad, cobertura de tests o pruebas físicas. Señala explícitamente lo que NO pudo ejecutarse.
- No mezcles resultados de campañas YOLO diferentes ni pesos genéricos con pesos entrenados para la clase `calyx`.

## 6. Seguridad física, informática y recursos

- Operaciones de motor, servo, brazo o locomoción requieren supervisión, límites de movimiento/velocidad, interbloqueo de comandos, expiración temporal, actuación por defecto segura y método de parada. Ningún agente debe ejecutar movimiento físico no autorizado.
- No publicar contraseñas, claves, tokens, `*.env`, direcciones privadas ni datos personales de participantes. Inspecciona `git diff --cached` antes de cada commit; `.gitignore` no protege secretos ya rastreados.
- No subir automáticamente datasets completos, `rosbag2`, vídeos, imágenes crudas, pesos `.pt` grandes, modelos CAD con licencias no aclaradas o binarios de Gazebo. Establecer una política externa de almacenamiento, checksum, procedencia y acceso.
- No copiar código, modelos, música, imágenes o datos de terceros sin comprobar permiso y conservar atribuciones obligatorias.
- Evitar instalar dependencias o modificar entornos experimentales funcionales sin plan, copia reproducible y autorización; preferir entornos aislados.

## 7. Autoría y transparencia de herramientas de IA

Se mantiene como **política interna del Robot Cosechador** el estándar de transparencia inspirado en el documento previo de NASA Space Apps. **No se afirma que NASA imponga estas obligaciones al nuevo macroproyecto.**

- El agente no se acredita como autor, coautor, copropietario ni colaborador humano. No añade `Co-authored-by` de IA ni slogans o publicidad opcional (`Generated by ...`) en commits, README o releases.
- La prohibición de créditos promocionales **no** elimina las declaraciones de uso de IA ni las atribuciones de terceros, académicas o legales. No ocultar el empleo de IA para aparentar autoría humana exclusiva.
- Mantener `docs/AI_USAGE.md` y `docs/ai_usage.json` (o su equivalente aprobado) con herramienta, tipo de artefacto, rutas afectadas, intervención humana, fecha y verificación. Registrar solo lo realmente utilizado; no inventar usos.
- **Código y datos generados con IA**: declarar en documentación descriptiva y metadatos del proyecto su origen y alcance; no usar IA como autor Git.
- **Imágenes y vídeos generados con IA**: marca de agua visible y legible `Generado con IA` o `AI-generated` en las versiones exportadas, además de trazabilidad.
- **Audio generado con IA**: declaración descriptiva y metadatos cuando el formato lo permita.
- Distinguir material sintético de evidencia experimental; jamás presentar imágenes, datos ni resultados generados como observaciones de laboratorio.
- Si universidades, revistas, congresos o terceros imponen declaraciones específicas, cumplirlas incluso si son más exigentes. No eliminar avisos de licencia, citas ni reconocimientos obligatorios.

## 8. Licencia e incorporación de terceros — decisión pendiente de derechos

- **Preferencia técnica inicial:** `Apache-2.0` para **código original del macroproyecto**, por ser permisiva y contemplar una concesión expresa de patentes; `MIT` sería alternativa más simple. Ninguna está autorizada como licencia global hasta revisar titularidad y compatibilidad.
- Antes de crear `LICENSE` definitivo: verificar con el equipo y, cuando corresponda, con la Universitaria Agustiniana/semillero, quién puede licenciar los aportes; identificar autores/titulares reales, contribuciones de terceros, restricciones de distribución y material previo. No atribuir copyright a la cuenta de GitHub por defecto ni inventar titulares.
- **Advertencia esencial:** Ultralytics YOLO11 publica licenciamiento `AGPL-3.0` o comercial/Enterprise; un monorepo que incorpore código/modelos derivados de esa tecnología requiere análisis de compatibilidad y obligaciones antes de declarar todo el proyecto `MIT` o `Apache-2.0`. La mera condición de repositorio público no resuelve esas obligaciones.
- Datasets, anotaciones, pesos, multimedia, documentación, CAD, firmware y software propio pueden requerir avisos/licencias distintos. `LICENSE` en raíz no concede derechos sobre materiales de terceros. Registrar `docs/LICENCIAS_Y_TERCEROS.md` y avisos `NOTICE` cuando correspondan.
- El agente puede **preparar una propuesta** documentada y el texto oficial sin modificarlo, pero debe solicitar decisión del titular antes de publicarla o cambiar una licencia existente. Si la titularidad o la compatibilidad es incierta, marcar `PENDIENTE` en lugar de poner una licencia incorrecta.

## 9. Puertas de calidad y revisión

Para cada cambio ejecuta, según alcance y disponibilidad, análisis estático, test unitario y test de contrato. Para ROS 2, una vez disponible el entorno: `colcon build`, `colcon test` y `colcon test-result --verbose`; en Python usar `pytest`/linters si están configurados. No declarar como aprobados tests que no existen.

Antes de solicitar revisión de integración:
1. Verifica `git status` y `git diff`; no hay cambios ajenos, secretos o artefactos pesados.
2. Registra versión del entorno, dependencias, comandos y resultados reproducibles, incluidos fallos.
3. Ejecuta al menos un test de productor y otro de consumidor para interfaces modificadas, o declara explícitamente el bloqueo.
4. Identifica cambios incompatibles, riesgos, simulaciones/Mocks y qué falta para ensayo físico.
5. Documenta qué rama y commit se ensayó; confirma si `main` ya incluye la dependencia.
6. Actualiza los registros de IA, terceros y cambios relevantes cuando corresponda.
7. Entrega un resumen de traspaso: commit SHA, archivos, contratos, pruebas, resultados, problemas y siguiente acción.

## 10. Reglas de revisión de código

Al revisar un PR, señala con prioridad: (a) cambios silenciosos de interfaces, unidades o TF; (b) órdenes de actuadores sin validación o parada; (c) fuga de datos/secreto; (d) afirmaciones experimentales sin prueba; (e) ausencia de aislamiento entre verdad simulada y estimación; (f) licencias incompatibles; (g) modificaciones fuera de la propiedad del equipo; (h) tests que no prueban el comportamiento anunciado. Bloquea la integración de hallazgos críticos, explica el riesgo y exige evidencia de corrección.

Estas reglas se adoptan como gobernanza del repositorio y se revisan mediante PR y acuerdo de las personas responsables. **Un agente no aprueba por sí mismo resultados científicos ni autoriza la actuación del robot.**
