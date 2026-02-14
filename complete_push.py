import subprocess
import sys
import os

os.chdir(r'C:\Users\Sahil\concore')

print("Aborting rebase and recovering branch state...")

# Method 1: Direct HEAD manipulation
with open('.git/HEAD', 'w') as f:
    f.write('ref: refs/heads/feature/enhanced-workflow-validation\n')

# Remove rebase state
import shutil
try:
    shutil.rmtree('.git/rebase-merge')
    print("✓ Removed rebase-merge directory")
except:
    pass

try:
    os.remove('.git/REBASE_HEAD')
    print("✓ Removed REBASE_HEAD")
except:
    pass

# Reset to original HEAD
result = subprocess.run(['git', 'reset', '--hard', 'ad0f393'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)

# Check status
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print("\nCurrent status:")
print(result.stdout)

# Fetch upstream
print("\nFetching upstream...")
result = subprocess.run(['git', 'fetch', 'upstream'], capture_output=True, text=True)
if result.returncode != 0:
    print(result.stderr)

# Merge upstream/dev
print("\nMerging upstream/dev...")
result = subprocess.run(['git', 'merge', 'upstream/dev', '-m', 'Merge upstream/dev'], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("Merge conflicts or error:")
    print(result.stderr)
    sys.exit(1)

# Push
print("\nPushing to origin...")
result = subprocess.run(['git', 'push', 'origin', 'feature/enhanced-workflow-validation', '--force-with-lease'], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
    sys.exit(1)

print("\n✓ Successfully pushed!")
