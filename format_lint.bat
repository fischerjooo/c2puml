@echo off
echo Formatting code with Black...
python -m black c2puml/ tests/
echo Code formatting completed!