import pytest
import os

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


class TestParseParams:

    def test_simple_key_value_pairs(self):
        from concore import parse_params
        params = parse_params("a=1;b=2")
        assert params == {"a": 1, "b": 2}

    def test_preserves_whitespace_in_values(self):
        from concore import parse_params
        params = parse_params("label = hello world ; x = 5")
        assert params["label"] == "hello world"
        assert params["x"] == 5

    def test_embedded_equals_in_value(self):
        from concore import parse_params
        params = parse_params("url=https://example.com?a=1&b=2")
        assert params["url"] == "https://example.com?a=1&b=2"

    def test_numeric_and_list_coercion(self):
        from concore import parse_params
        params = parse_params("delay=5;coeffs=[1,2,3]")
        assert params["delay"] == 5
        assert params["coeffs"] == [1, 2, 3]

    def test_dict_literal_backward_compatibility(self):
        from concore import parse_params
        params = parse_params("{'a': 1, 'b': 2}")
        assert params == {"a": 1, "b": 2}

    def test_windows_quoted_input(self):
        from concore import parse_params
        s = "\"a=1;b=2\""
        s = s[1:-1]  # simulate quote stripping before parse_params
        params = parse_params(s)
        assert params == {"a": 1, "b": 2}