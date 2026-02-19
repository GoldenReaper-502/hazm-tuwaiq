@echo off
call .venv\Scripts\activate
python -m http.server 4173 --directory frontend
