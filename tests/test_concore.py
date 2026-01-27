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


class TestSafeLiteralEval:

    def test_reads_dictionary_from_file(self, temp_dir):
        test_file = os.path.join(temp_dir, "config.txt")
        with open(test_file, "w") as f:
            f.write("{'name': 'test', 'value': 123}")
        
        from concore import safe_literal_eval
        result = safe_literal_eval(test_file, {})
        
        assert result == {'name': 'test', 'value': 123}

    def test_returns_default_when_file_missing(self):
        from concore import safe_literal_eval
        result = safe_literal_eval("nonexistent_file.txt", "fallback")
        
        assert result == "fallback"

    def test_returns_default_for_empty_file(self, temp_dir):
        test_file = os.path.join(temp_dir, "empty.txt")
        with open(test_file, "w") as f:
            pass
        
        from concore import safe_literal_eval
        result = safe_literal_eval(test_file, "default")
        
        assert result == "default"


class TestTryparam:

    def test_returns_existing_parameter(self):
        from concore import tryparam, params
        params['my_setting'] = 'custom_value'
        
        result = tryparam('my_setting', 'default_value')
        
        assert result == 'custom_value'

    def test_returns_default_for_missing_parameter(self):
        from concore import tryparam
        result = tryparam('missing_param', 'fallback')
        
        assert result == 'fallback'


class TestZeroMQPort:

    def test_class_is_defined(self):
        from concore import ZeroMQPort
        assert ZeroMQPort is not None


class TestDefaultConfiguration:

    def test_default_input_path(self):
        from concore import inpath
        assert inpath == "./in"

    def test_default_output_path(self):
        from concore import outpath
        assert outpath == "./out"


class TestPublicAPI:

    def test_module_imports_successfully(self):
        import concore
        assert concore is not None

    def test_core_functions_exist(self):
        from concore import safe_literal_eval
        from concore import tryparam
        from concore import default_maxtime
        
        assert callable(safe_literal_eval)
        assert callable(tryparam)
        assert callable(default_maxtime)