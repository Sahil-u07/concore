import subprocess
import os

os.chdir(r'C:\Users\Sahil\concore')

# Abort rebase
subprocess.run(['git', 'rebase', '--abort'], capture_output=True)

# Check status
result = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
