# PhysalisHarvest — Selective Cape Gooseberry Harvesting Robot

Macroproyecto del semillero de investigación SEIMA de la Universitaria Agustiniana para explorar la cosecha selectiva de uchuva (*Physalis peruviana* L.) mediante un robot móvil manipulador.

## Arquitectura y alcance

- **Visión y decisión:** percepción RGB-D, detección de frutos con YOLO, estimación XYZ, accesibilidad, selección y propuestas de aproximación. Corresponde al trabajo de grado de Laura Camila Rincón Malaver y Diego Alejandro Amaya Celis.
- **Brazo:** modelado, cinemática, control del manipulador e integración del efector final.
- **Locomoción:** plataforma móvil, control de motores, desplazamiento, navegación y posicionamiento.

Se prevé emplear ROS 2, Gazebo, Python, visión artificial, sensores RGB-D y sistemas embebidos según las necesidades de cada equipo. Las versiones, plataformas y dependencias aún deben acordarse y documentarse. Las carpetas son reservas de organización: no son paquetes ROS 2 funcionales ni pruebas de integración o validación física.

## Ramas y colaboración

`main` contiene versiones integradas y revisadas; `feat/vision`, `feat/arm`, `feat/locomotion` y `feat/2WD` son las ramas permanentes de desarrollo. `feat/2WD` es el banco experimental de locomoción para un chasis de dos ruedas motrices. Las ramas temporales `feature/`, `fix/`, `experiment/`, `test/` y `chore/` parten de la rama de trabajo correspondiente. Los cambios hacia `main` se proponen mediante pull request (PR), con revisión, evidencia y conflictos resueltos; no se integran automáticamente. Sincronizar periódicamente cada rama con `main` y coordinar las interfaces compartidas. Consulte [CONTRIBUTING.md](CONTRIBUTING.md).

## Estructura

```text
.github/                 Plantilla de PR y flujo de CI
ros2_ws/src/             Futuros paquetes de los tres subsistemas e interfaces
simulacion/              Gazebo y modelos
firmware/                Software embebido
hardware/                Documentación del brazo y la locomoción
docs/                    Arquitectura, contratos y pruebas
tests/                   Pruebas transversales futuras
```

Los contratos propuestos y sus decisiones pendientes están en [docs/interfaces/contratos-ros2.md](docs/interfaces/contratos-ros2.md). La integración depende de acuerdos entre equipos y evidencia de pruebas.

## Estado inicial

Esta rama incluye el [banco ROS 2 del chasis 2WD](ros2_ws/src/robot_locomocion/bench_2wd/README.md) y los [ensayos ESP32 con sus registros](firmware/bench_2wd/README.md). El banco cubre el diagnóstico XYZ y pruebas acotadas con ruedas libres. Los contratos ROS 2 comunes y las pruebas de navegación quedan pendientes. Datasets, grabaciones y pesos grandes requieren la política de datos y artefactos.
