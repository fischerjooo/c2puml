@echo off
echo Formatting code with Black...
python -m black src/ tests/
echo Code formatting completed!