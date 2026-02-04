from pathlib import Path
from rich.panel import Panel
import shutil
import os

def init_project(name, template, console):
    project_path = Path(name)
    
    if project_path.exists():
        console.print(f"[red]Error:[/red] Directory '{name}' already exists")
        return
    
    console.print(f"[cyan]Creating project:[/cyan] {name}")
    console.print()
    
    project_path.mkdir(parents=True)
    (project_path / 'src').mkdir()
    (project_path / 'out').mkdir()
    (project_path / 'in').mkdir()
    
    sample_workflow = '''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="workflow" edgedefault="directed">
    <node id="n0">
      <data key="d0">
        <y:ShapeNode>
          <y:NodeLabel>1:controller.py</y:NodeLabel>
        </y:ShapeNode>
      </data>
    </node>
    <node id="n1">
      <data key="d0">
        <y:ShapeNode>
          <y:NodeLabel>2:plant.py</y:NodeLabel>
        </y:ShapeNode>
      </data>
    </node>
    <edge id="e0" source="n0" target="n1">
      <data key="d1">
        <y:PolyLineEdge>
          <y:EdgeLabel>control_output</y:EdgeLabel>
        </y:PolyLineEdge>
      </data>
    </edge>
    <edge id="e1" source="n1" target="n0">
      <data key="d1">
        <y:PolyLineEdge>
          <y:EdgeLabel>sensor_data</y:EdgeLabel>
        </y:PolyLineEdge>
      </data>
    </edge>
  </graph>
</graphml>'''
    
    with open(project_path / 'workflow.graphml', 'w') as f:
        f.write(sample_workflow)
    
    console.print(f"[green]✓[/green] Created project structure")
    console.print(f"  [dim]├──[/dim] src/")
    console.print(f"  [dim]├──[/dim] in/")
    console.print(f"  [dim]├──[/dim] out/")
    console.print(f"  [dim]└──[/dim] workflow.graphml")
    console.print()
    console.print(Panel.fit(
        f"[green]Project created successfully![/green]\n\n"
        f"Next steps:\n"
        f"  1. cd {name}\n"
        f"  2. Add your source files to src/\n"
        f"  3. concore run workflow.graphml",
        border_style="green"
    ))
