"""Report package presence, build evidence and test result counts without asserting validation."""
import pathlib
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(sys.argv[1])
workspace = root / 'ros2_ws'
groups = {'robot_percepcion_decision': 'visión', 'robot_brazo': 'brazo',
          'robot_locomocion': 'locomoción', 'robot_interfaces': 'interfaces'}
manifests = sorted((workspace / 'src').rglob('package.xml'))
print(f'Paquetes ROS detectados: {len(manifests)}')
for directory, label in groups.items():
    matches = [p for p in manifests if directory in p.relative_to(workspace / 'src').parts]
    print(f'{label}: {len(matches)} paquetes' if matches else f'{label}: SKIP, sin paquete')
for manifest in manifests:
    try:
        name = ET.parse(manifest).getroot().findtext('name')
        installed = (workspace / 'install' / name / 'share' / name / 'package.xml').is_file()
        results = list((workspace / 'build' / name / 'test_results').rglob('*.xml'))
        count = sum(len(ET.parse(p).getroot().findall('.//testcase')) for p in results)
        status = f'{count} casos con resultado' if count else 'SKIP, sin casos registrados'
        print(f'{name}: compilado={"sí" if installed else "no confirmado"}; pruebas={status}')
    except (ET.ParseError, OSError, TypeError) as exc:
        print(f'FAIL: no se pudo leer {manifest}: {type(exc).__name__}')
        sys.exit(1)
print('La presencia, compilación o ejecución de pruebas no valida un subsistema.')
