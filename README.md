# Robot Cosechador

Macroproyecto del semillero de investigación SEIMA de la Universitaria Agustiniana para explorar la cosecha selectiva de uchuva (*Physalis peruviana* L.) mediante un robot móvil manipulador.

## Arquitectura y alcance

- **Visión y decisión:** percepción RGB-D, detección de frutos con YOLO, estimación XYZ, accesibilidad, selección y propuestas de aproximación. Corresponde al trabajo de grado de Laura Camila Rincón Malaver y Diego Alejandro Amaya Celis.
- **Brazo:** modelado, cinemática, control del manipulador e integración del efector final.
- **Locomoción:** plataforma móvil, control de motores, desplazamiento, navegación y posicionamiento.

Se prevé emplear ROS 2, Gazebo, Python, visión artificial, sensores RGB-D y sistemas embebidos según las necesidades de cada equipo. Las versiones, plataformas y dependencias aún deben acordarse y documentarse. Las carpetas son reservas de organización: no son paquetes ROS 2 funcionales ni pruebas de integración o validación física.

## Ramas y colaboración

`main` contiene versiones integradas y revisadas; `vision`, `brazo` y `locomocion` son ramas de desarrollo de los respectivos equipos. Las ramas temporales `feature/`, `fix/` y `experiment/` parten de la rama de trabajo correspondiente. Los cambios hacia `main` se proponen mediante pull request (PR), con revisión, evidencia y conflictos resueltos; no se integran automáticamente. Sincronizar periódicamente cada rama con `main` y coordinar las interfaces compartidas. Consulte [CONTRIBUTING.md](CONTRIBUTING.md).

## Estructura

```text
.github/                 Plantilla de PR y futuros flujos de CI
ros2_ws/src/             Futuros paquetes de los tres subsistemas e interfaces
simulacion/              Gazebo y modelos
firmware/                Software embebido
hardware/                Documentación del brazo y la locomoción
docs/                    Arquitectura, contratos y pruebas
tests/                   Pruebas transversales futuras
```

Los contratos propuestos y sus decisiones pendientes están en [docs/interfaces/contratos-ros2.md](docs/interfaces/contratos-ros2.md). La integración depende de acuerdos entre equipos y evidencia de pruebas.

## Estado inicial

Repositorio en organización inicial. No se declara implementado ni validado ningún subsistema en esta base; no hay CI ni interfaces ROS 2 definitivas. La política de datos y artefactos debe definirse antes de incorporar datasets, grabaciones o pesos grandes.
