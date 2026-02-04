from pathlib import Path
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import subprocess
import sys

def run_workflow(workflow_file, source, output, exec_type, auto_build, console):
    workflow_path = Path(workflow_file)
    
    console.print(f"[cyan]Running workflow:[/cyan] {workflow_path.name}")
    console.print()
    
    if not workflow_path.exists():
        console.print(f"[red]Error:[/red] Workflow file not found")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating scripts...", total=None)
        
        try:
            result = subprocess.run(
                [sys.executable, '-c', f'import mkconcore; mkconcore.generate("{workflow_file}", "{source}", "{output}", "{exec_type}")'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                progress.update(task, description="[green]✓ Scripts generated")
            else:
                progress.update(task, description="[red]✗ Generation failed")
                console.print(f"\n[red]Error:[/red] {result.stderr}")
                return
            
        except Exception as e:
            progress.update(task, description="[red]✗ Generation failed")
            console.print(f"\n[red]Error:[/red] {str(e)}")
            return
    
    console.print()
    console.print(Panel.fit(
        f"[green]✓ Workflow generated successfully![/green]\n\n"
        f"Output directory: {output}/",
        border_style="green"
    ))
    
    if auto_build:
        console.print()
        console.print("[cyan]Building workflow...[/cyan]")
