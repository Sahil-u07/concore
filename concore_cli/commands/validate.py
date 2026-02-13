from pathlib import Path
from bs4 import BeautifulSoup
from rich.panel import Panel
from rich.table import Table
import re
import xml.etree.ElementTree as ET

def validate_workflow(workflow_file, source_dir, console):
    workflow_path = Path(workflow_file)
    source_root = (workflow_path.parent / source_dir)
    
    console.print(f"[cyan]Validating:[/cyan] {workflow_path.name}")
    console.print()
    
    errors = []
    warnings = []
    info = []
    
    def finalize():
        show_results(console, errors, warnings, info)
        return len(errors) == 0

    try:
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        if not content.strip():
            errors.append("File is empty")
            return finalize()
        
        # strict XML syntax check
        try:
            ET.fromstring(content)
        except ET.ParseError as e:
            errors.append(f"Invalid XML: {str(e)}")
            return finalize()
        
        try:
            soup = BeautifulSoup(content, 'xml')
        except Exception as e:
            errors.append(f"Invalid XML: {str(e)}")
            return finalize()
        
        root = soup.find('graphml')
        if not root:
            errors.append("Not a valid GraphML file - missing <graphml> root element")
            return finalize()
            
        # check the graph attributes
        graph = soup.find('graph')
        if not graph:
             errors.append("Missing <graph> element")
        else:
             edgedefault = graph.get('edgedefault')
             if not edgedefault:
                 errors.append("Graph missing required 'edgedefault' attribute")
             elif edgedefault not in ['directed', 'undirected']:
                 errors.append(f"Invalid edgedefault value '{edgedefault}' (must be 'directed' or 'undirected')")
        
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

        if not source_root.exists():
            warnings.append(f"Source directory not found: {source_root}")
        
        node_labels = []
        for node in nodes:
            #check the node id
            node_id = node.get('id')
            if not node_id:
                errors.append("Node missing required 'id' attribute")
                #skip further checks for this node to avoid noise
                continue

            try:
                #robust find: try with namespace prefix first, then without
                label_tag = node.find('y:NodeLabel')
                if not label_tag:
                    label_tag = node.find('NodeLabel')
                
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
                            nodeId_part, filename = parts
                            if not filename:
                                errors.append(f"Node '{label}' has no filename")
                            elif not any(filename.endswith(ext) for ext in ['.py', '.cpp', '.m', '.v', '.java']):
                                warnings.append(f"Node '{label}' has unusual file extension")
                            elif source_root.exists():
                                file_path = source_root / filename
                                if not file_path.exists():
                                    errors.append(f"Missing source file: {filename}")
                else:
                    warnings.append(f"Node {node_id} has no label")
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
                if not label_tag:
                    label_tag = edge.find('EdgeLabel')
                    
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
        
        return finalize()

    except FileNotFoundError:
        console.print(f"[red]Error:[/red] File not found: {workflow_path}")
        return False
    except Exception as e:
        console.print(f"[red]Validation failed:[/red] {str(e)}")
        return False

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
