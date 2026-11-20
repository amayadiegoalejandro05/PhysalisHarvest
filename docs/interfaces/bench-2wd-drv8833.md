# Contrato experimental del banco DRV8833 v1

Windows captura RGB y profundidad con la Astra. `astra_aruco.py --ros`
envía JSON por stdin a `aruco_source` en WSL al recibir `ARUCO_READY`.
ROS 2 decide el movimiento en `controller`. El puente Windows lleva las
órdenes por USB al ESP32. Usa un único publicador y un único controlador.
El alcance es localhost, dominio 83 por defecto. Este contrato pertenece
al banco 2WD.

| Recurso ROS 2 | Tipo | Productor → consumidor | Contenido |
| --- | --- | --- | --- |
| `/bench_2wd/drv8833/aruco_target` | `geometry_msgs/msg/PointStamped` | `bench_2wd_drv8833_aruco` → `bench_2wd_drv8833_controller` | ID 0 de DICT_4X4_50, punto superficial XYZ en metros. Marco `astra_depth_optical_frame`, X a la derecha, Y abajo, Z axial hacia delante. Sello de recepción RGB en Windows. XYZ cero indica detección ausente o profundidad inválida. QoS volátil, mejor esfuerzo, profundidad 1. |
| `/bench_2wd/drv8833/state` | `std_msgs/msg/String` | `bench_2wd_drv8833_controller` → operador | `ARMED esperando_aruco`, `DRIVE F/L/R`, `STOP` con motivo. QoS volátil, fiable, profundidad 10. |
| `/bench_2wd/drv8833/enable` | `std_srvs/srv/SetBool` | `bench_2wd_drv8833_session` → `bench_2wd_drv8833_controller` | `true` arma una espera de hasta 30 s aunque falte el ArUco. `false` cancela la espera o para y desarma. El resultado corresponde a la aceptación de la solicitud ROS. Verifica el GPIO en los acuses del puente. |

Ejemplos ROS en WSL después de cargar Jazzy y el workspace:

```bash
export ROS_DOMAIN_ID=83 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
ros2 topic echo /bench_2wd/drv8833/state
ros2 service call /bench_2wd/drv8833/enable std_srvs/srv/SetBool '{data: true}'
ros2 service call /bench_2wd/drv8833/enable std_srvs/srv/SetBool '{data: false}'
```

La espera admite observaciones ausentes o Z ≤ 0,50 m con salidas en bajo.
El movimiento empieza con una lectura recibida tras armar, de hasta
180 ms y Z > 0,50 m. El productor y el controlador descartan muestras
entrantes con más de 250 ms de edad o adelantadas más de 30 ms. El
controlador refresca la dirección cada 50 ms y deja de utilizar la última
observación a los 450 ms de edad. Una observación inválida recibida, el
umbral, la expiración o una orden de parada cortan la sesión. El movimiento
se limita a 7,5 s en ROS.

El controlador emite `CMD sello_ns vence_ns orden` por stdout. El puente
rechaza órdenes que ya vencieron o pasaron más de 125 ms en la tubería.
El sello usa reloj de sistema y la duración de sesión usa reloj monótono.
El canal stdin del controlador se usa para detectar el cierre del puente,
y se bloquea una segunda instancia por usuario y dominio.

El serial USB funciona a 115200 bit/s. `ID` desarma y responde
`DRV8833_ROS_V1`. `CF`, `CL` y `CR` inician una sesión ESP32 con la
primera dirección. `F`, `L` y `R` renuevan la dirección de una sesión
vigente. `S` para y desarma. Cada mensaje termina en salto de línea. Los
acuses `OK orden GPIO` reflejan los cuatro pines en el orden 25/26/27/14.
Los patrones F, L y R son `1010`, `0110` y `1001`, respectivamente.
`0000` indica rueda libre y también se admite durante el interbloqueo.
El ESP32 impone 100 ms en bajo entre direcciones, un watchdog de 150 ms
desde la última orden y un límite de 8 s. Un comando inválido desarma y
devuelve `ERR COMMAND`. Un error de enlace o acuse cierra el puente con
un intento de parada. [Procedimiento y cableado](../../ros2_ws/src/robot_locomocion/bench_2wd_drv8833/README.md)
