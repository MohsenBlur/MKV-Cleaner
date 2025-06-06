import os
import sys
from pathlib import Path

os.environ.setdefault('MKVCLEANER_SKIP_BOOTSTRAP', '1')

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.config import AppConfig


@pytest.fixture
def defaults():
    return AppConfig()
