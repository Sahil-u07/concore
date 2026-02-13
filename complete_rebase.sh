#!/bin/bash
cd "D:\gsoc org\concore-project\concore"
git add requirements-dev.txt
git rebase --continue
git push origin add-concoredocker-tests --force
