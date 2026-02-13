cd "D:\gsoc org\concore-project\concore"
git config core.editor "notepad"
git fetch upstream
git checkout dev
git reset --hard upstream/dev
git branch -D refactor-file-io-v2 2>$null
git checkout -b refactor-file-io-v2
Write-Host "Branch ready!"
