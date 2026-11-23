# PhysalisHarvest — Selective Cape Gooseberry Harvesting Robot

Macroproyecto del semillero de investigación SEIMA de la Universitaria Agustiniana para explorar la cosecha selectiva de uchuva (*Physalis peruviana* L.) mediante un robot móvil manipulador.

## Arquitectura y alcance

- **Visión y decisión:** percepción RGB-D, detección de frutos con YOLO, estimación XYZ, accesibilidad, selección y propuestas de aproximación. Corresponde al trabajo de grado de Laura Camila Rincón Malaver y Diego Alejandro Amaya Celis.
- **Brazo:** modelado, cinemática, control del manipulador e integración del efector final.
- **Locomoción:** plataforma móvil, control de motores, desplazamiento, navegación y posicionamiento.

Se prevé emplear ROS 2, Gazebo, Python, visión artificial, sensores RGB-D y sistemas embebidos según las necesidades de cada equipo. El banco 2WD usa ROS 2 Jazzy y tiene dependencias y pruebas propias. La integración de los tres subsistemas se documenta por separado.

## Ramas y colaboración

`main` contiene versiones integradas y revisadas; `feat/vision`, `feat/arm`, `feat/locomotion` y `feat/2WD` son las ramas permanentes de desarrollo. `feat/2WD` es el banco experimental de locomoción para un chasis de dos ruedas motrices. Las ramas temporales `feature/`, `fix/`, `experiment/`, `test/` y `chore/` parten de la rama de trabajo correspondiente. Los cambios hacia `main` se proponen mediante pull request (PR), con revisión, evidencia y conflictos resueltos; no se integran automáticamente. Sincronizar periódicamente cada rama con `main` y coordinar las interfaces compartidas. Consulte [CONTRIBUTING.md](CONTRIBUTING.md).

## Estructura

```text
.github/                 Plantilla de PR y flujo de CI
ros2_ws/src/             Subsistemas, interfaces y paquetes ROS 2 del banco
simulacion/              Gazebo y modelos
firmware/                Software embebido
hardware/                Documentación del brazo y la locomoción
docs/                    Arquitectura, contratos y pruebas
tests/                   Pruebas transversales futuras
```

Los contratos propuestos y sus decisiones pendientes están en [docs/interfaces/contratos-ros2.md](docs/interfaces/contratos-ros2.md). La integración depende de acuerdos entre equipos y evidencia de pruebas.

## Banco 2WD en esta rama

Desde PowerShell en la raíz, abre la consola Windows en modo desconectado:

```powershell
& .\.venv-astra\Scripts\python.exe -B .\firmware\bench_2wd\tools\consola_2wd.py --vista-previa
```

Para operar el banco, usa el mismo comando sin `--vista-previa` y sigue
la [secuencia de la consola](ros2_ws/src/robot_locomocion/bench_2wd_drv8833/README.md#consola-windows).

El [procedimiento DRV8833](ros2_ws/src/robot_locomocion/bench_2wd_drv8833/README.md)
cubre la instalación desde un clon, el cableado, el firmware ESP32 y los
comandos para dirigir el banco al primer ArUco válido observado. Consulta el [contrato ROS 2
y serial](docs/interfaces/bench-2wd-drv8833.md) y el [diagnóstico RGB-D](ros2_ws/src/robot_locomocion/bench_2wd/README.md).
La ruta de varios marcadores queda pendiente de prueba física.
Los [ensayos históricos del banco](firmware/bench_2wd/README.md)
conservan sus resultados y límites.
