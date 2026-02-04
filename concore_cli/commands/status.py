from rich.table import Table
from rich.panel import Panel
import psutil
import os

def show_status(console):
    console.print()
    console.print("[bold cyan]Concore Process Status[/bold cyan]")
    console.print()
    
    current_pid = os.getpid()
    concore_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'concore' in cmdline.lower() and proc.info['pid'] != current_pid:
                    concore_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if not concore_processes:
        console.print("[yellow]No running concore processes found[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("PID", style="cyan", width=8)
    table.add_column("Name", style="white")
    table.add_column("Command", style="green")
    
    for proc in concore_processes:
        try:
            info = proc.info
            pid = str(info['pid'])
            name = info['name']
            cmd = ' '.join(info['cmdline'][:3]) if len(info['cmdline']) > 3 else ' '.join(info['cmdline'])
            
            table.add_row(pid, name, cmd)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    console.print(table)
    console.print()
