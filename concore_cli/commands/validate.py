from pathlib import Path
from bs4 import BeautifulSoup
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
import re
from collections import defaultdict, deque
from typing import List, Set, Tuple, Dict


def detect_cycles(nodes_dict: Dict[str, str], edges: List[Tuple[str, str]]) -> List[List[str]]:
    """
    Detect all cycles in the workflow graph using DFS.
    
    Args:
        nodes_dict: Mapping of node IDs to labels
        edges: List of (source_id, target_id) tuples
    
    Returns:
        List of cycles, where each cycle is a list of node IDs
    """
    # Build adjacency list
    graph = defaultdict(list)
    for source, target in edges:
        graph[source].append(target)
    
    cycles = []
    visited = set()
    rec_stack = set()
    path = []
    
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
        
        path.pop()
        rec_stack.remove(node)
    
    # Run DFS from each unvisited node
    for node in nodes_dict.keys():
        if node not in visited:
            dfs(node)
    
    return cycles


def analyze_control_loop(cycle: List[str], nodes_dict: Dict[str, str]) -> Dict:
    """
    Analyze if a cycle represents a valid control loop.
    
    A valid control loop typically has:
    - A controller node (contains 'control', 'controller', 'pid', 'mpc')
    - A plant/PM node (contains 'pm', 'plant', 'model')
    - At least 2 nodes (for feedback)
    
    Returns:
        Dict with analysis results
    """
    # Get unique nodes in cycle (cycle has duplicate first/last node)
    unique_nodes = []
    seen = set()
    for node_id in cycle:
        if node_id not in seen:
            unique_nodes.append(node_id)
            seen.add(node_id)
    
    node_labels = [nodes_dict.get(node_id, '').lower() for node_id in unique_nodes if node_id in nodes_dict]
    
    # Keywords for different node types
    controller_keywords = ['control', 'controller', 'pid', 'mpc', 'observer', 'regulator']
    plant_keywords = ['pm', 'plant', 'model', 'physio', 'cardiac', 'neural']
    
    has_controller = any(any(keyword in label for keyword in controller_keywords) for label in node_labels)
    has_plant = any(any(keyword in label for keyword in plant_keywords) for label in node_labels)
    
    cycle_length = len(unique_nodes)
    
    analysis = {
        'is_valid_control_loop': has_controller and has_plant and cycle_length >= 2,
        'has_controller': has_controller,
        'has_plant': has_plant,
        'length': cycle_length,
        'nodes': [nodes_dict.get(nid, nid) for nid in unique_nodes]
    }
    
    return analysis


def check_graph_connectivity(nodes_dict: Dict[str, str], edges: List[Tuple[str, str]]) -> Tuple[bool, List[str]]:
    """
    Check if all nodes are reachable in the graph.
    
    Returns:
        (is_fully_connected, list_of_unreachable_nodes)
    """
    if not nodes_dict:
        return True, []
    
    # Build adjacency list (undirected for connectivity check)
    graph = defaultdict(set)
    for source, target in edges:
        graph[source].add(target)
        graph[target].add(source)
    
    # BFS from first node
    start_node = next(iter(nodes_dict.keys()))
    visited = set()
    queue = deque([start_node])
    
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                queue.append(neighbor)
    
    unreachable = [nodes_dict[nid] for nid in nodes_dict.keys() if nid not in visited]
    
    return len(unreachable) == 0, unreachable


def validate_workflow(workflow_file, console):
    workflow_path = Path(workflow_file)
    
    console.print(f"[cyan]Validating:[/cyan] {workflow_path.name}")
    console.print()
    
    errors = []
    warnings = []
    info = []
    
    try:
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        if not content.strip():
            errors.append("File is empty")
            return show_results(console, errors, warnings, info)
        
        try:
            soup = BeautifulSoup(content, 'xml')
        except Exception as e:
            errors.append(f"Invalid XML: {str(e)}")
            return show_results(console, errors, warnings, info)
        
        if not soup.find('graphml'):
            errors.append("Not a valid GraphML file - missing <graphml> root element")
            return show_results(console, errors, warnings, info)
        
        nodes = soup.find_all('node')
        edges = soup.find_all('edge')
        
        if len(nodes) == 0:
            warnings.append("No nodes found in workflow")
        else:
            info.append(f"Found {len(nodes)} node(s)")
        
        if len(edges) == 0:
            warnings.append("No edges found in workflow")
        else:
            info.append(f"Found {len(edges)} edge(s)")
        
        node_labels = []
        for node in nodes:
            try:
                label_tag = node.find('y:NodeLabel')
                if label_tag and label_tag.text:
                    label = label_tag.text.strip()
                    node_labels.append(label)
                    
                    if ':' not in label:
                        warnings.append(f"Node '{label}' missing format 'ID:filename'")
                    else:
                        parts = label.split(':')
                        if len(parts) != 2:
                            warnings.append(f"Node '{label}' has invalid format")
                        else:
                            node_id, filename = parts
                            if not filename:
                                errors.append(f"Node '{label}' has no filename")
                            elif not any(filename.endswith(ext) for ext in ['.py', '.cpp', '.m', '.v', '.java']):
                                warnings.append(f"Node '{label}' has unusual file extension")
                else:
                    warnings.append(f"Node {node.get('id', 'unknown')} has no label")
            except Exception as e:
                warnings.append(f"Error parsing node: {str(e)}")
        
        node_ids = {node.get('id') for node in nodes if node.get('id')}
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            
            if not source or not target:
                errors.append("Edge missing source or target")
                continue
            
            if source not in node_ids:
                errors.append(f"Edge references non-existent source node: {source}")
            if target not in node_ids:
                errors.append(f"Edge references non-existent target node: {target}")
        
        edge_label_regex = re.compile(r"0x([a-fA-F0-9]+)_(\S+)")
        zmq_edges = 0
        file_edges = 0
        
        for edge in edges:
            try:
                label_tag = edge.find('y:EdgeLabel')
                if label_tag and label_tag.text:
                    if edge_label_regex.match(label_tag.text.strip()):
                        zmq_edges += 1
                    else:
                        file_edges += 1
            except:
                pass
        
        if zmq_edges > 0:
            info.append(f"ZMQ-based edges: {zmq_edges}")
        if file_edges > 0:
            info.append(f"File-based edges: {file_edges}")
        
        # NEW: Advanced graph analysis
        # Build edge list for cycle detection
        edge_list = []
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            if source and target and source in node_ids and target in node_ids:
                edge_list.append((source, target))
        
        # Build node dictionary (id -> label)
        node_id_to_label = {}
        for node in nodes:
            node_id = node.get('id')
            if node_id:
                label_tag = node.find('y:NodeLabel')
                if label_tag and label_tag.text:
                    node_id_to_label[node_id] = label_tag.text.strip()
                else:
                    node_id_to_label[node_id] = node_id
        
        # Check connectivity
        is_connected, unreachable = check_graph_connectivity(node_id_to_label, edge_list)
        if not is_connected:
            for node_label in unreachable:
                warnings.append(f"Unreachable node: {node_label}")
        
        # Detect cycles
        cycles = detect_cycles(node_id_to_label, edge_list)
        
        if cycles:
            info.append(f"Found {len(cycles)} cycle(s) in workflow")
            
            # Analyze each cycle
            control_loops = []
            other_cycles = []
            
            for cycle in cycles:
                analysis = analyze_control_loop(cycle, node_id_to_label)
                if analysis['is_valid_control_loop']:
                    control_loops.append(analysis)
                else:
                    other_cycles.append(analysis)
            
            if control_loops:
                info.append(f"Valid control loops: {len(control_loops)}")
                console.print()
                console.print("[green]Control Loops Detected:[/green]")
                for i, loop in enumerate(control_loops, 1):
                    console.print(f"  [green]Loop {i}:[/green] {' -> '.join(loop['nodes'])} -> [cycle]")
            
            if other_cycles:
                warnings.append(f"Non-standard cycles detected: {len(other_cycles)}")
                console.print()
                console.print("[yellow]! Non-Standard Cycles:[/yellow]")
                for i, cycle_info in enumerate(other_cycles, 1):
                    cycle_desc = ' -> '.join(cycle_info['nodes'])
                    console.print(f"  [yellow]Cycle {i}:[/yellow] {cycle_desc} -> [cycle]")
                    
                    if not cycle_info['has_controller']:
                        console.print(f"    [dim]Missing controller node[/dim]")
                    if not cycle_info['has_plant']:
                        console.print(f"    [dim]Missing plant/PM node[/dim]")
        else:
            info.append("No cycles detected (DAG workflow)")
            warnings.append("Workflow has no feedback loops - not a control system")
        
        show_results(console, errors, warnings, info)
        
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] File not found: {workflow_path}")
    except Exception as e:
        console.print(f"[red]Validation failed:[/red] {str(e)}")

def show_results(console, errors, warnings, info):
    if errors:
        console.print("[red]X Validation failed[/red]\n")
        for error in errors:
            console.print(f"  [red]X[/red] {error}")
    else:
        console.print("[green]OK Validation passed[/green]\n")
    
    if warnings:
        console.print()
        for warning in warnings:
            console.print(f"  [yellow]![/yellow] {warning}")
    
    if info:
        console.print()
        for item in info:
            console.print(f"  [blue]i[/blue] {item}")
    
    console.print()
    
    if not errors:
        console.print(Panel.fit(
            "[green]OK[/green] Workflow is valid and ready to run",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            f"[red]Found {len(errors)} error(s)[/red]\n"
            "Fix the errors above before running the workflow",
            border_style="red"
        ))
