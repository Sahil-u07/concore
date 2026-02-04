from rich.panel import Panel
import psutil
import os
import signal

def stop_all(console):
    console.print()
    console.print("[cyan]Stopping all concore processes...[/cyan]")
    console.print()
    
    current_pid = os.getpid()
    stopped = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'concore' in cmdline.lower() and proc.info['pid'] != current_pid:
                    proc.terminate()
                    stopped += 1
                    console.print(f"[green]✓[/green] Stopped process {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            pass
    
    if stopped == 0:
        console.print("[yellow]No processes to stop[/yellow]")
    else:
        console.print()
        console.print(Panel.fit(
            f"[green]Stopped {stopped} process(es)[/green]",
            border_style="green"
        ))
