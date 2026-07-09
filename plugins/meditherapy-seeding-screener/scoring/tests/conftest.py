"""pytest 부트스트랩 — src/ 를 sys.path에 올려 `from scoring....` import 가능하게."""
import os
import sys
import json
import pytest

_SRC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

_ONTOLOGY_PATH = os.path.join(_SRC, "rules", "ontology.json")


@pytest.fixture(scope="session")
def ontology():
    with open(_ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
