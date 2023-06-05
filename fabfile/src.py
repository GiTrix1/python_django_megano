from fabric import task

from ._utils import BASE_DIR
from ._utils import SRC_DIR
from ._utils import VENV_DIR


def handle_run_result(return_code, stdout, stderr):
    """Обрабатывает результат выполнения команды."""
    if return_code != 0:
        print(stdout)
        print(stderr)


@task
def isort(c):
    """Запускает проверку корректности импортов."""
    cmd = VENV_DIR.joinpath("isort")
    out = c.run(f"{cmd} {SRC_DIR} --src={SRC_DIR} -c --diff")
    handle_run_result(out.return_code, out.stdout, out.stderr)


@task
def pylint(c):
    """Запускает проверку стиля кода по PEP."""
    cmd = VENV_DIR.joinpath("pylint")
    out = c.run(f"{cmd} --rcfile={BASE_DIR.joinpath('.pylintrc')} {SRC_DIR}/*")
    handle_run_result(out.return_code, out.stdout, out.stderr)
