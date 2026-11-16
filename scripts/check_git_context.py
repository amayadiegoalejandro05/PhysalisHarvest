"""Inspect Git context without fetching, switching branches, or modifying refs."""
import argparse
import os
import re
import sys
from pathlib import Path
from check_common import Report, git

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = 'github.com/amayadiegoalejandro05/Robot-Cosechador'
SUBSYSTEMS = {'vision', 'brazo', 'locomocion'}
OWNED = {'robot_percepcion_decision': 'vision', 'robot_brazo': 'brazo', 'robot_locomocion': 'locomocion'}


def classify_path(path):
    parts = path.split('/')
    # Shared integration paths are defined by location, not assumptions about semantics.
    shared_prefixes = ('.github/', 'docs/interfaces/', 'docs/integracion/', 'ros2_ws/src/robot_interfaces/',
                       'ros2_ws/src/robot_bringup/', 'ros2_ws/src/robot_description/',
                       'ros2_ws/src/robot_integration/', 'config/tf/', 'config/frames/', 'scripts/')
    shared_files = {'AGENTS.md', 'CONTRIBUTING.md', 'requirements.txt', 'requirements-dev.txt',
                    'pyproject.toml', 'ros2_ws/rosdep.yaml', 'ros2_ws/colcon.meta'}
    if path in shared_files or any(path.startswith(prefix) for prefix in shared_prefixes):
        return 'shared'
    if len(parts) >= 4 and parts[:2] == ['ros2_ws', 'src'] and parts[2] in OWNED:
        return OWNED[parts[2]]
    return 'other'



def check(root, target=None, subsystem=None, environ=None):
    root = Path(root).resolve()
    env = os.environ if environ is None else environ
    report = Report(root)
    def run(*args): return git(root, *args)
    top = run('rev-parse', '--show-toplevel')
    if top.returncode:
        report.add('GIT-REPO', 'FAIL', 'No se encontró un repositorio Git.', 'Ejecutar en el repositorio correcto.')
        return report
    report.add('GIT-REPO', 'PASS', 'Repositorio: ' + top.stdout.strip(), 'Confirmar el directorio de trabajo.')
    remote = run('remote', 'get-url', 'origin')
    url = remote.stdout.strip()
    valid = url in (f'https://{EXPECTED}', f'https://{EXPECTED}.git', f'git@{EXPECTED.replace("/", ":", 1)}', f'git@{EXPECTED.replace("/", ":", 1)}.git', f'ssh://git@{EXPECTED}', f'ssh://git@{EXPECTED}.git')
    report.add('GIT-ORIGIN', 'PASS' if valid else 'FAIL', 'origin: ' + (url or 'no disponible'), 'Corregir origin antes de operaciones remotas.' if not valid else 'Verificar el destino antes de operar remotamente.')
    head = run('rev-parse', '--verify', 'HEAD')
    sha = head.stdout.strip()
    report.add('GIT-HEAD', 'PASS' if head.returncode == 0 and re.fullmatch(r'[0-9a-f]{40,64}', sha) else 'FAIL', 'HEAD: ' + (sha or 'no disponible'), 'Crear o recuperar un commit válido.' if head.returncode else 'Registrar este SHA en la evidencia.')
    branch_result = run('symbolic-ref', '--quiet', '--short', 'HEAD')
    branch = branch_result.stdout.strip()
    is_pr = env.get('GITHUB_ACTIONS') == 'true' and env.get('GITHUB_EVENT_NAME') in ('pull_request', 'pull_request_target')
    source = env.get('GITHUB_HEAD_REF', '') if is_pr else branch
    if branch:
        report.add('GIT-BRANCH', 'PASS', 'Rama activa: ' + branch, 'Confirmar la rama antes de modificar.')
    elif is_pr and source:
        report.add('GIT-BRANCH', 'SKIP', 'HEAD separado en validación de PR; rama declarada: ' + source, 'No tratar el commit temporal como HEAD de la rama fuente.')
    else:
        report.add('GIT-BRANCH', 'SKIP', 'HEAD separado; no hay rama activa.', 'Especificar el contexto antes de integrar.')
    upstream = run('rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{upstream}') if branch else None
    tracking = upstream.stdout.strip() if upstream and upstream.returncode == 0 else ''
    report.add('GIT-UPSTREAM', 'PASS' if tracking else 'SKIP', 'Seguimiento: ' + tracking if tracking else 'No hay seguimiento configurado o HEAD está separado.', 'Configurar seguimiento cuando se publique la rama.' if not tracking else 'Actualizar referencias antes de integrar.')
    status = run('status', '--porcelain=v1', '--untracked-files=all')
    if status.returncode: report.add('GIT-WORKTREE', 'FAIL', 'No se pudo leer el estado.', 'Revisar el repositorio.')
    elif status.stdout: report.add('GIT-WORKTREE', 'SKIP', 'Hay cambios locales sin confirmar o archivos no rastreados (no se enumeran).', 'Revisar git status y conservar los cambios antes de integrar.')
    else: report.add('GIT-WORKTREE', 'PASS', 'Árbol de trabajo limpio.', 'Mantener evidencia de cambios.')
    def compare(identifier, ref, label):
        if not ref:
            report.add(identifier, 'SKIP', f'{label} no especificado o no disponible.', 'Indicar referencia y actualizarla cuando proceda.')
            return
        exists = run('rev-parse', '--verify', '--quiet', ref + '^{commit}')
        if exists.returncode:
            report.add(identifier, 'SKIP', f'Referencia {ref} no disponible localmente.', 'Consultar el remoto verificado y hacer fetch antes de integrar.')
            return
        count = run('rev-list', '--left-right', '--count', f'{ref}...HEAD')
        if count.returncode:
            report.add(identifier, 'FAIL', f'No se pudo comparar con {ref}.', 'Revisar el historial y repositorio.')
            return
        behind, ahead = map(int, count.stdout.split())
        # For a PR merge checkout HEAD already contains the base; this is not source branch divergence.
        suffix = ' Comparación del checkout de PR, no necesariamente de la rama fuente.' if is_pr and not branch else ''
        shallow = run('rev-parse', '--is-shallow-repository').stdout.strip() == 'true'
        state = 'SKIP' if behind or shallow or (is_pr and not branch) else 'PASS'
        relation = 'divergente' if behind and ahead else ('atrasada' if behind else ('adelantada' if ahead else 'sincronizada con referencia local'))
        if shallow: suffix += ' Historial superficial: la comparación puede estar incompleta.'
        report.add(identifier, state, f'{ref}: {relation}; HEAD detrás {behind}, delante {ahead} commits.' + suffix, 'Sincronizar o revisar la base antes de integrar; fetch puede revelar cambios nuevos.' if behind else 'Actualizar referencias antes de integrar; no se consulta la red.')
    compare('GIT-TRACKING-DIVERGENCE', tracking, 'Seguimiento')
    target_name = target or (env.get('GITHUB_BASE_REF') if is_pr else None)
    if not target_name and source in SUBSYSTEMS | {'main'}: target_name = 'main' if source != 'main' else 'main'
    target_ref = target_name if target_name and (target_name.startswith('origin/') or target_name.startswith('refs/')) else ('origin/' + target_name if target_name else None)
    compare('GIT-TARGET-DIVERGENCE', target_ref, 'Destino')
    compare('GIT-MAIN-DIVERGENCE', 'origin/main', 'main')
    # A dry comparison of committed trees is advisory, never a merge or a guarantee.
    if not target_ref or (is_pr and not branch):
        report.add('GIT-CONFLICTS', 'SKIP', 'Destino o rama fuente no verificable en este checkout.', 'Comparar la rama fuente en un clon completo.')
    else:
        base = run('merge-base', 'HEAD', target_ref)
        if base.returncode:
            report.add('GIT-CONFLICTS', 'SKIP', 'No se encontró ancestro común local.', 'Actualizar referencias y revisar historial.')
        else:
            preview = run('merge-tree', base.stdout.strip(), 'HEAD', target_ref)
            if preview.returncode:
                report.add('GIT-CONFLICTS', 'SKIP', 'No fue posible calcular una vista previa.', 'Revisar integración en un entorno aislado.')
            elif '<<<<<<< ' in preview.stdout:
                report.add('GIT-CONFLICTS', 'SKIP', 'Posibles conflictos en árboles confirmados.', 'Revisar y resolver con responsables antes del PR.')
            else:
                report.add('GIT-CONFLICTS', 'PASS', 'No se detectaron marcadores de conflicto en árboles confirmados.', 'Repetir con referencias actuales; no cubre cambios locales ni garantiza integración.')
    changes = set()
    for args in [('diff', '--name-only', 'HEAD'), ('diff', '--cached', '--name-only'), ('ls-files', '--others', '--exclude-standard')]:
        result = run(*args)
        if result.returncode == 0: changes.update(result.stdout.splitlines())
    for ref in {target_ref, 'origin/main'} - {None}:
        base = run('merge-base', 'HEAD', ref)
        if base.returncode == 0:
            result = run('diff', '--name-only', base.stdout.strip(), ref)
            if result.returncode == 0: changes.update(result.stdout.splitlines())
            own = run('diff', '--name-only', base.stdout.strip(), 'HEAD')
            if own.returncode == 0: changes.update(own.stdout.splitlines())
    grouped = {group: sorted(p for p in changes if classify_path(p) == group) for group in ('vision', 'brazo', 'locomocion', 'shared', 'other')}
    risky = grouped['shared']
    owners = [group for group in ('vision', 'brazo', 'locomocion') if grouped[group]]
    report.add('GIT-OWNERS', 'PASS' if owners else 'SKIP', '; '.join(f'{owner}: {", ".join(grouped[owner])}' for owner in owners) if owners else 'No se detectaron rutas exclusivas de subsistema.', 'Revisar propiedad y semántica de los cambios.')
    report.add('GIT-SHARED', 'SKIP' if risky else 'PASS', 'Rutas compartidas para revisar: ' + ', '.join(risky) if risky else 'Sin rutas compartidas conocidas en los cambios examinados.', 'Solicitar revisión de integración y equipos afectados.' if risky else 'La clasificación por rutas no garantiza compatibilidad ROS ni detecta toda dependencia.')
    cross = len(owners) > 1 or bool(risky and owners)
    report.add('GIT-CROSS', 'SKIP' if cross else 'PASS', 'Cambios en varios subsistemas o en subsistema e integración compartida.' if cross else 'No se detectó combinación transversal por rutas.', 'Solicitar revisión conjunta de los equipos afectados.' if cross else 'Revisar manualmente el impacto semántico.')
    if grouped['other']:
        report.add('GIT-OTHER', 'SKIP', 'Rutas no clasificadas: ' + ', '.join(grouped['other']), 'Determinar responsables y posible impacto transversal manualmente.')
    recognized = source in SUBSYSTEMS | {'main'} or bool(re.fullmatch(r'(feature|fix|experiment|test)/[A-Za-z0-9._/-]+', source))
    if not source:
        report.add('GIT-SUBSYSTEM', 'SKIP', 'No se conoce la rama fuente.', 'Indicar la rama y el subsistema.')
    elif not recognized:
        report.add('GIT-SUBSYSTEM', 'FAIL', 'Rama no reconocida: ' + source, 'Usar una rama principal o prefijo temporal permitido.')
    else:
        markers = {name for name in SUBSYSTEMS if re.search(r'(^|[/_.-])' + name + r'($|[/_.-])', source)}
        if source in SUBSYSTEMS: markers.add(source)
        if subsystem and (markers and markers != {subsystem} or source == 'main'):
            report.add('GIT-SUBSYSTEM', 'FAIL', f'Rama {source} incompatible con subsistema {subsystem}.', 'Usar una rama del subsistema indicado.')
        elif subsystem and not markers:
            report.add('GIT-SUBSYSTEM', 'SKIP', f'{source} no identifica un subsistema en su nombre.', 'Confirmar manualmente su procedencia y destino.')
        elif not markers:
            report.add('GIT-SUBSYSTEM', 'SKIP', f'Rama reconocida: {source}; no se identifica un subsistema.', 'Confirmar manualmente que corresponde a cambios compartidos y su destino.')
        else:
            report.add('GIT-SUBSYSTEM', 'PASS', f'Rama reconocida: {source}; subsistemas nombrados: {", ".join(sorted(markers)) or "compartido/no indicado"}.', 'Confirmar el destino de los cambios compartidos.')
    report.add('GIT-FRESHNESS', 'SKIP', 'Las referencias locales no prueban el estado actual del servidor.', 'Ejecutar git fetch origin y repetir antes de integrar.')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--target', help='Rama destino, por ejemplo main o vision')
    parser.add_argument('--subsystem', choices=sorted(SUBSYSTEMS))
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    sys.exit(check(args.root, args.target, args.subsystem).finish(args.json))
