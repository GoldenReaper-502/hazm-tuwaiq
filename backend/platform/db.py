import sqlite3
from pathlib import Path
from contextlib import contextmanager
from backend.platform.config import settings

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS sites (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE,threshold_json TEXT)""",
    """CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,site TEXT)""",
    """CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,password_hash TEXT,full_name TEXT,role TEXT,department TEXT,site TEXT DEFAULT 'HQ')""",
    """CREATE TABLE IF NOT EXISTS cameras (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,site TEXT,location TEXT,status TEXT DEFAULT 'online',stream_url TEXT,last_health_check TEXT)""",
    """CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,description TEXT,site TEXT,department TEXT,severity INTEGER,likelihood INTEGER,risk_score INTEGER,status TEXT,evidence_json TEXT,corrective_actions_json TEXT,due_date TEXT,escalation_level INTEGER DEFAULT 0,created_at TEXT,updated_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS incident_actions (id INTEGER PRIMARY KEY AUTOINCREMENT,incident_id INTEGER,action_text TEXT,owner TEXT,due_date TEXT,status TEXT DEFAULT 'open',created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS observations (id INTEGER PRIMARY KEY AUTOINCREMENT,category TEXT,location TEXT,site TEXT,observed_at TEXT,department TEXT,corrective_action TEXT,due_date TEXT,responsible_person TEXT,closed INTEGER DEFAULT 0,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS risks (id INTEGER PRIMARY KEY AUTOINCREMENT,hazard TEXT,site TEXT,department TEXT,controls TEXT,severity INTEGER,likelihood INTEGER,residual_risk INTEGER,status TEXT DEFAULT 'open',created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS inspection_templates (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,checklist_json TEXT,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS inspections (id INTEGER PRIMARY KEY AUTOINCREMENT,site TEXT,department TEXT,template_id INTEGER,scheduled_date TEXT,status TEXT DEFAULT 'scheduled',result_json TEXT,nonconformities_json TEXT,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS environment_measurements (id INTEGER PRIMARY KEY AUTOINCREMENT,metric TEXT,value REAL,unit TEXT,location TEXT,site TEXT,measured_at TEXT,exceeded INTEGER DEFAULT 0)""",
    """CREATE TABLE IF NOT EXISTS alert_events (id INTEGER PRIMARY KEY AUTOINCREMENT,rule_name TEXT,severity TEXT,payload_json TEXT,channel TEXT,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS vision_events (id INTEGER PRIMARY KEY AUTOINCREMENT,event_type TEXT,camera_id INTEGER,payload_json TEXT,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS trainings (id INTEGER PRIMARY KEY AUTOINCREMENT,employee_name TEXT,course_name TEXT,expires_at TEXT,completed_at TEXT,compliant INTEGER DEFAULT 1)""",
    """CREATE TABLE IF NOT EXISTS ptw_permits (id INTEGER PRIMARY KEY AUTOINCREMENT,work_type TEXT,checklist_json TEXT,status TEXT,approver TEXT,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS policies (id INTEGER PRIMARY KEY AUTOINCREMENT,site TEXT,name TEXT,description TEXT,active INTEGER DEFAULT 1,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT,actor TEXT,action TEXT,entity TEXT,entity_id TEXT,details_json TEXT,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS compliance_checklists (id INTEGER PRIMARY KEY AUTOINCREMENT,site TEXT,item TEXT,status TEXT,owner TEXT,due_date TEXT,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS reports_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT,report_type TEXT,payload_json TEXT,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS rules (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,condition_expr TEXT,action_expr TEXT,enabled INTEGER DEFAULT 1,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS rule_events (id INTEGER PRIMARY KEY AUTOINCREMENT,rule_id INTEGER,status TEXT,payload_json TEXT,created_at TEXT)""",
    """CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT,channel TEXT,title TEXT,message TEXT,status TEXT DEFAULT 'unread',created_at TEXT)""",
]


def init_db() -> None:
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.db_path) as conn:
        cur = conn.cursor()
        for stmt in SCHEMA:
            cur.execute(stmt)
        conn.commit()


@contextmanager
def get_conn():
    init_db()
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
