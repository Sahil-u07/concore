from pathlib import Path
from bs4 import BeautifulSoup
from rich.panel import Panel
from rich.table import Table
from collections import defaultdict, deque
import re

def detect_cycles(adjacency, node_ids, node_id_to_label):
    """Detect cycles in the graph using DFS."""
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in adjacency.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path):
                    return True
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle_nodes = path[cycle_start:]
                cycle_labels = [node_id_to_label.get(n, n) for n in cycle_nodes]
                cycles.append(' → '.join(cycle_labels) + f' → {cycle_labels[0]}')
                return True
        
        path.pop()
        rec_stack.remove(node)
        return False
    
    for node in node_ids:
        if node not in visited:
            dfs(node, [])
    
    return cycles

def validate_workflow(workflow_file, console):
    workflow_path = Path(workflow_file)
    
    console.print(f"[cyan]Validating:[/cyan] {workflow_path.name}")
    console.print()
    
    errors = []
    warnings = []
    info = []
    node_id_to_label = {}
    
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
        node_label_counts = defaultdict(int)
        
        for node in nodes:
            try:
                node_id = node.get('id')
                label_tag = node.find('y:NodeLabel')
                if label_tag and label_tag.text:
                    label = label_tag.text.strip()
                    node_labels.append(label)
                    node_label_counts[label] += 1
                    if node_id:
                        node_id_to_label[node_id] = label
                    
                    if ':' not in label:
                        warnings.append(f"Node '{label}' missing format 'ID:filename'")
                    else:
                        parts = label.split(':', 1)  # Split only on first colon
                        if len(parts) != 2:
                            warnings.append(f"Node '{label}' has invalid format")
                        else:
                            node_id_part, filename = parts
                            if not filename:
                                errors.append(f"Node '{label}' has no filename")
                            elif not any(filename.endswith(ext) for ext in ['.py', '.cpp', '.hpp', '.c', '.h', '.m', '.v', '.java']):
                                warnings.append(f"Node '{label}' file '{filename}' has unusual extension")
        
        # Build adjacency list for cycle detection
        adjacency = defaultdict(list)
        
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
            else:
                adjacency[source].append(target)
            
            # Check for self-loops
            if source == target:
                warnings.append(f"Self-loop detected: {node_id_to_label.get(source, source)} → {node_id_to_label.get(source, source)}")
        
        # Detect unreachable nodes
        if nodes and edges:
            reachable = set()
            sources_only = set()
            targets_only = set()
            
            for edge in edges:
                source = edge.get('source')
                target = edge.get('target')
                if source:
                    sources_only.add(source)
                if target:
                    targets_only.add(target)
            
            # Nodes that only appear as sources (no incoming edges)
            entry_nodes = sources_only - targets_only
            
            # Nodes that only appear as targets (no outgoing edges)
            exit_nodes = targets_only - sources_only
            
            # BFS from entry nodes to find all reachable
            from collections import deque
            if entry_nodes:
                queue = deque(entry_nodes)
                visited = set(entry_nodes)
                
                while queue:
                    current = queue.popleft()
                    reachable.add(current)
                    for neighbor in adjacency.get(current, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                unreachable = node_ids - reachable
                if unreachable:
                    for node_id in unreachable:
                        label = node_id_to_label.get(node_id, node_id)
                        warnings.append(f"Unreachable node: {label}")
            
            if entry_nodes:
                info.append(f"Entry point(s): {', '.join([node_id_to_label.get(n, n) for n in entry_nodes])}")
            if exit_nodes:
                info.append(f"Exit point(s): {', '.join([node_id_to_label.get(n, n) for n in exit_nodes])}")
        
        # Detect simple cycles (warning, not error - cycles may be intentional)
        cycles_found = detect_cycles(adjacency, node_ids, node_id_to_label)
        if cycles_found:
            for cycle_info in cycles_found[:3]:  # Show first 3 cycles
                warnings.append(f"Cycle detected: {cycle_info}")
            if len(cycles_found) > 3:
                warnings.append(f"...and {len(cycles_found) - 3} more cycle(s)
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
        
        show_results(console, errors, warnings, info)
        
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] File not found: {workflow_path}")
    except Exception as e:
        console.print(f"[red]Validation failed:[/red] {str(e)}")

def show_results(console, errors, warnings, info):
    if errors:
        console.print("[red]✗ Validation failed[/red]\n")
        for error in errors:
            console.print(f"  [red]✗[/red] {error}")
    else:
        console.print("[green]✓ Validation passed[/green]\n")
    
    if warnings:
        console.print()
        for warning in warnings:
            console.print(f"  [yellow]⚠[/yellow] {warning}")
    
    if info:
        console.print()
        for item in info:
            console.print(f"  [blue]ℹ[/blue] {item}")
    
    console.print()
    
    if not errors:
        console.print(Panel.fit(
            "[green]✓[/green] Workflow is valid and ready to run",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            f"[red]Found {len(errors)} error(s)[/red]\n"
            "Fix the errors above before running the workflow",
            border_style="red"
        ))
