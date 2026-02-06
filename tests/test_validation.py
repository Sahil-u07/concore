import pytest
import tempfile
from pathlib import Path
from concore_cli.commands.validate import (
    detect_cycles,
    analyze_control_loop,
    check_graph_connectivity
)


class TestCycleDetection:
    """Test cycle detection in workflow graphs"""
    
    def test_simple_cycle(self):
        """Test detection of a simple 2-node cycle"""
        nodes = {'n1': 'N1:controller.py', 'n2': 'N2:pm.py'}
        edges = [('n1', 'n2'), ('n2', 'n1')]
        
        cycles = detect_cycles(nodes, edges)
        
        assert len(cycles) == 1
        assert set(cycles[0]) == {'n1', 'n2'}
    
    def test_no_cycle_dag(self):
        """Test that DAG (no cycles) returns empty list"""
        nodes = {'n1': 'N1:node1.py', 'n2': 'N2:node2.py', 'n3': 'N3:node3.py'}
        edges = [('n1', 'n2'), ('n2', 'n3')]
        
        cycles = detect_cycles(nodes, edges)
        
        assert len(cycles) == 0
    
    def test_self_loop(self):
        """Test detection of self-loop"""
        nodes = {'n1': 'N1:node.py'}
        edges = [('n1', 'n1')]
        
        cycles = detect_cycles(nodes, edges)
        
        assert len(cycles) == 1
    
    def test_complex_graph_multiple_cycles(self):
        """Test detection of multiple cycles"""
        nodes = {
            'n1': 'N1:controller.py',
            'n2': 'N2:pm.py',
            'n3': 'N3:observer.py',
            'n4': 'N4:plant.py'
        }
        edges = [
            ('n1', 'n2'),
            ('n2', 'n1'),  # Cycle 1: n1 <-> n2
            ('n3', 'n4'),
            ('n4', 'n3'),  # Cycle 2: n3 <-> n4
        ]
        
        cycles = detect_cycles(nodes, edges)
        
        assert len(cycles) >= 2


class TestControlLoopAnalysis:
    """Test control loop validation"""
    
    def test_valid_control_loop(self):
        """Test that controller + plant is recognized as valid control loop"""
        nodes = {'n1': 'N1:controller.py', 'n2': 'N2:pm.py'}
        cycle = ['n1', 'n2', 'n1']
        
        analysis = analyze_control_loop(cycle, nodes)
        
        assert analysis['is_valid_control_loop'] is True
        assert analysis['has_controller'] is True
        assert analysis['has_plant'] is True
        assert analysis['length'] == 2
    
    def test_pid_controller_recognized(self):
        """Test that PID controller is recognized"""
        nodes = {'n1': 'N1:pid_controller.py', 'n2': 'N2:cardiac_model.py'}
        cycle = ['n1', 'n2', 'n1']
        
        analysis = analyze_control_loop(cycle, nodes)
        
        assert analysis['has_controller'] is True
    
    def test_mpc_controller_recognized(self):
        """Test that MPC controller is recognized"""
        nodes = {'n1': 'N1:mpc_regulator.py', 'n2': 'N2:neural_plant.py'}
        cycle = ['n1', 'n2', 'n1']
        
        analysis = analyze_control_loop(cycle, nodes)
        
        assert analysis['has_controller'] is True
        assert analysis['has_plant'] is True
    
    def test_invalid_loop_no_controller(self):
        """Test that loop without controller is invalid"""
        nodes = {'n1': 'N1:data.py', 'n2': 'N2:pm.py'}
        cycle = ['n1', 'n2', 'n1']
        
        analysis = analyze_control_loop(cycle, nodes)
        
        assert analysis['is_valid_control_loop'] is False
        assert analysis['has_controller'] is False
    
    def test_invalid_loop_no_plant(self):
        """Test that loop without plant is invalid"""
        nodes = {'n1': 'N1:controller.py', 'n2': 'N2:data.py'}
        cycle = ['n1', 'n2', 'n1']
        
        analysis = analyze_control_loop(cycle, nodes)
        
        assert analysis['is_valid_control_loop'] is False
        assert analysis['has_plant'] is False
    
    def test_three_node_control_loop(self):
        """Test valid control loop with 3 nodes"""
        nodes = {
            'n1': 'N1:controller.py',
            'n2': 'N2:pm.py',
            'n3': 'N3:observer.py'
        }
        cycle = ['n1', 'n2', 'n3', 'n1']
        
        analysis = analyze_control_loop(cycle, nodes)
        
        assert analysis['is_valid_control_loop'] is True
        assert analysis['length'] == 3


class TestGraphConnectivity:
    """Test graph connectivity checks"""
    
    def test_fully_connected_graph(self):
        """Test that connected graph is recognized"""
        nodes = {'n1': 'N1:node1.py', 'n2': 'N2:node2.py', 'n3': 'N3:node3.py'}
        edges = [('n1', 'n2'), ('n2', 'n3')]
        
        is_connected, unreachable = check_graph_connectivity(nodes, edges)
        
        assert is_connected is True
        assert len(unreachable) == 0
    
    def test_disconnected_graph(self):
        """Test that disconnected nodes are detected"""
        nodes = {
            'n1': 'N1:node1.py',
            'n2': 'N2:node2.py',
            'n3': 'N3:isolated.py'
        }
        edges = [('n1', 'n2')]  # n3 is isolated
        
        is_connected, unreachable = check_graph_connectivity(nodes, edges)
        
        assert is_connected is False
        assert len(unreachable) == 1
        assert 'N3:isolated.py' in unreachable
    
    def test_empty_graph(self):
        """Test empty graph"""
        nodes = {}
        edges = []
        
        is_connected, unreachable = check_graph_connectivity(nodes, edges)
        
        assert is_connected is True
        assert len(unreachable) == 0
    
    def test_single_node(self):
        """Test graph with single node"""
        nodes = {'n1': 'N1:node.py'}
        edges = []
        
        is_connected, unreachable = check_graph_connectivity(nodes, edges)
        
        assert is_connected is True


class TestIntegrationValidation:
    """Integration tests for full validation workflow"""
    
    def test_validate_control_loop_workflow(self):
        """Test validation of a real control loop GraphML"""
        graphml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" 
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <key for="edge" id="d10" yfiles.type="edgegraphics"/>
  <graph id="G" edgedefault="directed">
    <node id="n1">
      <data key="d6">
        <y:ShapeNode>
          <y:NodeLabel>N1:controller.py</y:NodeLabel>
        </y:ShapeNode>
      </data>
    </node>
    <node id="n2">
      <data key="d6">
        <y:ShapeNode>
          <y:NodeLabel>N2:pm.py</y:NodeLabel>
        </y:ShapeNode>
      </data>
    </node>
    <edge source="n1" target="n2">
      <data key="d10">
        <y:PolyLineEdge>
          <y:EdgeLabel>vol1</y:EdgeLabel>
        </y:PolyLineEdge>
      </data>
    </edge>
    <edge source="n2" target="n1">
      <data key="d10">
        <y:PolyLineEdge>
          <y:EdgeLabel>vol2</y:EdgeLabel>
        </y:PolyLineEdge>
      </data>
    </edge>
  </graph>
</graphml>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False) as f:
            f.write(graphml_content)
            temp_file = f.name
        
        try:
            # This would test the full validate_workflow function
            # For now, just verify the file was created
            assert Path(temp_file).exists()
        finally:
            Path(temp_file).unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
