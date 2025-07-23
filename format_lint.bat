@echo off
echo Formatting code with Black...
python -m black c_to_plantuml/ tests/
echo Code formatting completed!