import pytest
import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)


@pytest.fixture
def create_test_file(temp_dir):
    def _create_file(filename, content):
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath
    return _create_file