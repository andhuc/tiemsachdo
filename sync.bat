@echo off
git add .
git commit -m "import book"
git push
if errorlevel 1 pause
