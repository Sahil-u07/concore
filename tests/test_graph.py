import unittest
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner
from concore_cli.cli import cli

class TestGraphValidation(unittest.TestCase):
    
    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            
    def create_graph_file(self, filename, content):
        filepath = Path(self.temp_dir) / filename
        with open(filepath, 'w') as f:
            f.write(content)
        return str(filepath)

    def test_validate_corrupted_xml(self):
        content = '<graphml><node id="n0">'
        filepath = self.create_graph_file('corrupted.graphml', content)
        
        result = self.runner.invoke(cli, ['validate', filepath])
        
        self.assertIn('Validation failed', result.output)
        self.assertIn('Invalid XML', result.output)

    def test_validate_empty_file(self):
        filepath = self.create_graph_file('empty.graphml', '')
        
        result = self.runner.invoke(cli, ['validate', filepath])
        
        self.assertIn('Validation failed', result.output)
        self.assertIn('File is empty', result.output)
    
    def test_validate_missing_node_id(self):
        content = '''
        <graphml xmlns:y="http://www.yworks.com/xml/graphml">
            <graph id="G" edgedefault="directed">
                <node>
                    <data key="d0"><y:NodeLabel>n0:script.py</y:NodeLabel></data>
                </node>
            </graph>
        </graphml>
        '''
        filepath = self.create_graph_file('missing_id.graphml', content)
        result = self.runner.invoke(cli, ['validate', filepath])
        self.assertIn('Validation failed', result.output)
        self.assertIn("Node missing required 'id' attribute", result.output)

    def test_validate_missing_edgedefault(self):
        content = '''
        <graphml xmlns:y="http://www.yworks.com/xml/graphml">
            <graph id="G">
                <node id="n0">
                    <data key="d0"><y:NodeLabel>n0:script.py</y:NodeLabel></data>
                </node>
            </graph>
        </graphml>
        '''
        filepath = self.create_graph_file('missing_default.graphml', content)
        result = self.runner.invoke(cli, ['validate', filepath])
        self.assertIn('Validation failed', result.output)
        self.assertIn("Graph missing required 'edgedefault'", result.output)

    def test_validate_missing_root_element(self):
        content = '<?xml version="1.0"?><other_root></other_root>'
        filepath = self.create_graph_file('not_graphml.xml', content)
        
        result = self.runner.invoke(cli, ['validate', filepath])
        
        self.assertIn('Validation failed', result.output)
        self.assertIn('missing <graphml> root element', result.output)

    def test_validate_broken_edges(self):
        content = '''
        <graphml xmlns:y="http://www.yworks.com/xml/graphml">
            <graph id="G" edgedefault="directed">
                <node id="n0">
                    <data key="d0"><y:NodeLabel>n0:script.py</y:NodeLabel></data>
                </node>
                <edge source="n0" target="n1"/>
            </graph>
        </graphml>
        '''
        filepath = self.create_graph_file('bad_edge.graphml', content)
        
        result = self.runner.invoke(cli, ['validate', filepath])
        
        self.assertIn('Validation failed', result.output)
        self.assertIn('Edge references non-existent target node', result.output)

    def test_validate_node_missing_filename(self):
        content = '''
        <graphml xmlns:y="http://www.yworks.com/xml/graphml">
            <graph id="G" edgedefault="directed">
                <node id="n0">
                    <data key="d0"><y:NodeLabel>n0:</y:NodeLabel></data>
                </node>
            </graph>
        </graphml>
        '''
        filepath = self.create_graph_file('bad_node.graphml', content)
        
        result = self.runner.invoke(cli, ['validate', filepath])
        
        self.assertIn('Validation failed', result.output)
        self.assertIn('has no filename', result.output)

    def test_validate_unsafe_node_label(self):
        content = '''
        <graphml xmlns:y="http://www.yworks.com/xml/graphml">
            <graph id="G" edgedefault="directed">
                <node id="n0">
                    <data key="d0"><y:NodeLabel>n0;rm -rf /:script.py</y:NodeLabel></data>
                </node>
            </graph>
        </graphml>
        '''
        filepath = self.create_graph_file('injection.graphml', content)

        result = self.runner.invoke(cli, ['validate', filepath])

        self.assertIn('Validation failed', result.output)
        self.assertIn('unsafe shell characters', result.output)

    def test_validate_valid_graph(self):
        content = '''
        <graphml xmlns:y="http://www.yworks.com/xml/graphml">
            <graph id="G" edgedefault="directed">
                <node id="n0">
                    <data key="d0"><y:NodeLabel>n0:script.py</y:NodeLabel></data>
                </node>
            </graph>
        </graphml>
        '''
        filepath = self.create_graph_file('valid.graphml', content)
        
        result = self.runner.invoke(cli, ['validate', filepath])
        
        self.assertIn('Validation passed', result.output)
        self.assertIn('Workflow is valid', result.output)

if __name__ == '__main__':
    unittest.main()