import pytest
import os
import numpy as np

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

    @pytest.fixture(autouse=True)
    def reset_params(self):
        from concore import params
        original_params = params.copy()
        yield
        params.clear()
        params.update(original_params)

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
        from concore import safe_literal_eval
        assert safe_literal_eval is not None

    def test_core_functions_exist(self):
        from concore import safe_literal_eval, tryparam, default_maxtime
        
        assert callable(safe_literal_eval)
        assert callable(tryparam)
        assert callable(default_maxtime)


class TestNumpyConversion:
    def test_convert_scalar(self):
        from concore import convert_numpy_to_python
        val = np.float64(3.14)
        res = convert_numpy_to_python(val)
        assert type(res) == float
        assert res == 3.14

    def test_convert_list_and_dict(self):
        from concore import convert_numpy_to_python
        data = {
            'a': np.int32(10),
            'b': [np.float64(1.1), np.float64(2.2)]
        }
        res = convert_numpy_to_python(data)
        assert type(res['a']) == int
        assert type(res['b'][0]) == float
        assert res['b'][1] == 2.2

class TestInitVal:
    @pytest.fixture(autouse=True)
    def reset_simtime(self):
        import concore
        old_simtime = concore.simtime
        yield
        concore.simtime = old_simtime

    def test_initval_updates_simtime(self):
        import concore
        concore.simtime = 0
        # initval takes string repr of a list [time, val1, val2...]
        result = concore.initval("[100, 'data']")
        
        assert concore.simtime == 100
        assert result == ['data']

    def test_initval_handles_bad_input(self):
        import concore
        concore.simtime = 0
        # Input that isn't a list
        result = concore.initval("not_a_list")
        assert concore.simtime == 0
        assert result == []

class TestDefaultMaxTime:
    def test_uses_file_value(self, temp_dir, monkeypatch):
        import concore
        # Mock the path to maxtime file
        maxtime_file = os.path.join(temp_dir, "concore.maxtime")
        with open(maxtime_file, "w") as f:
            f.write("500")
        
        monkeypatch.setattr(concore, 'concore_maxtime_file', maxtime_file)
        concore.default_maxtime(100)
        
        assert concore.maxtime == 500

    def test_uses_default_when_missing(self, monkeypatch):
        import concore
        monkeypatch.setattr(concore, 'concore_maxtime_file', "missing_file")
        concore.default_maxtime(999)
        assert concore.maxtime == 999

class TestUnchanged:
    @pytest.fixture(autouse=True)
    def reset_globals(self):
        import concore
        old_s = concore.s
        old_olds = concore.olds
        yield
        concore.s = old_s
        concore.olds = old_olds

    def test_unchanged_returns_true_if_same(self):
        import concore
        concore.s = "same"
        concore.olds = "same"
        
        # Should return True and reset s to empty
        assert concore.unchanged() is True
        assert concore.s == ''

    def test_unchanged_returns_false_if_diff(self):
        import concore
        concore.s = "new"
        concore.olds = "old"
        
        assert concore.unchanged() is False
        assert concore.olds == "new"