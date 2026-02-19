@echo off
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
set PYTHONPATH=.
python -c "from backend.platform.bootstrap import seed_demo_data; seed_demo_data(); print('Seed completed')"
