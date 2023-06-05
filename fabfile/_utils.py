from pathlib import Path
import sys


BASE_DIR = Path(__file__).parent.parent
PROJECT_NAME = "market"

VENV_DIR = Path(sys.executable).parent
SRC_DIR = BASE_DIR.joinpath(PROJECT_NAME)
