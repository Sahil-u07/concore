@echo off
cd C:\Users\Sahil\concore
rmdir /s /q .git\rebase-merge 2>nul
del /f .git\REBASE_HEAD 2>nul
git reset --hard ad0f393
git fetch upstream
git merge upstream/dev -m "Merge upstream/dev"
git push origin feature/enhanced-workflow-validation --force-with-lease
