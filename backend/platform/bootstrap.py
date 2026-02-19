from datetime import datetime, timezone, timedelta
import json
from backend.platform.db import init_db, get_conn
from backend.platform.auth import hash_password


def seed_demo_data() -> None:
    init_db()
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    with get_conn() as conn:
        users = [
            ("admin", "Admin@123", "Platform Admin", "admin", "HSE", "HQ"),
            ("hse", "HSE@123", "HSE Officer", "hse", "Safety", "Plant-1"),
            ("supervisor", "Sup@123", "Shift Supervisor", "supervisor", "Operations", "Plant-1"),
            ("viewer", "View@123", "Viewer", "viewer", "Management", "HQ"),
            ("auditor", "Audit@123", "Internal Auditor", "auditor", "Compliance", "HQ"),
        ]
        for u, p, fn, r, d, s in users:
            if not conn.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
                conn.execute("INSERT INTO users(username,password_hash,full_name,role,department,site) VALUES(?,?,?,?,?,?)", (u, hash_password(p), fn, r, d, s))

        if not conn.execute("SELECT 1 FROM sites").fetchone():
            conn.execute("INSERT INTO sites(name,threshold_json) VALUES(?,?)", ("Plant-1", json.dumps({"noise":85,"dust":150,"VOC":300,"temp":45,"humidity":70,"CO2":1000})))
            conn.execute("INSERT INTO sites(name,threshold_json) VALUES(?,?)", ("HQ", json.dumps({"noise":80,"dust":120,"VOC":250,"temp":40,"humidity":65,"CO2":900})))

        if not conn.execute("SELECT 1 FROM departments").fetchone():
            for dep, site in [("Operations", "Plant-1"), ("Safety", "Plant-1"), ("Maintenance", "Plant-1"), ("Management", "HQ")]:
                conn.execute("INSERT INTO departments(name,site) VALUES(?,?)", (dep, site))

        if not conn.execute("SELECT 1 FROM cameras").fetchone():
            cams = [("Gate Cam", "Plant-1", "Gate-A", "online", "rtsp://demo/gate"), ("Warehouse Cam", "Plant-1", "WH-1", "offline", "rtsp://demo/wh1")]
            for c in cams:
                conn.execute("INSERT INTO cameras(name,site,location,status,stream_url,last_health_check) VALUES(?,?,?,?,?,?)", (*c, now_iso))

        if not conn.execute("SELECT 1 FROM incidents").fetchone():
            conn.execute("INSERT INTO incidents(title,description,site,department,severity,likelihood,risk_score,status,evidence_json,corrective_actions_json,due_date,escalation_level,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         ("Forklift near miss", "Pedestrian overlap", "Plant-1", "Operations", 4, 3, 12, "open", "[]", '[{"action":"Lane separation"}]', (now + timedelta(days=2)).date().isoformat(), 1, now_iso, now_iso))

        if not conn.execute("SELECT 1 FROM observations").fetchone():
            conn.execute("INSERT INTO observations(category,location,site,observed_at,department,corrective_action,due_date,responsible_person,closed,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                         ("unsafe act", "Line-A", "Plant-1", now_iso, "Operations", "Toolbox talk", (now + timedelta(days=1)).date().isoformat(), "Ali", 0, now_iso))

        if not conn.execute("SELECT 1 FROM risks").fetchone():
            conn.execute("INSERT INTO risks(hazard,site,department,controls,severity,likelihood,residual_risk,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                         ("Work at height", "Plant-1", "Maintenance", "Harness, permit", 5, 3, 10, "open", now_iso))

        if not conn.execute("SELECT 1 FROM inspection_templates").fetchone():
            conn.execute("INSERT INTO inspection_templates(name,checklist_json,created_at) VALUES(?,?,?)", ("Daily HSE Walkdown", json.dumps(["PPE","Housekeeping","Fire exits"]), now_iso))

        if not conn.execute("SELECT 1 FROM inspections").fetchone():
            conn.execute("INSERT INTO inspections(site,department,template_id,scheduled_date,status,result_json,nonconformities_json,created_at) VALUES(?,?,?,?,?,?,?,?)",
                         ("Plant-1", "Operations", 1, (now - timedelta(days=1)).date().isoformat(), "scheduled", "{}", "[]", now_iso))

        if not conn.execute("SELECT 1 FROM environment_measurements").fetchone():
            env = [("noise", 88, "dBA"), ("CO2", 1050, "ppm"), ("temp", 39, "C")]
            for m, v, u in env:
                exceeded = 1 if (m == "noise" and v > 85) or (m == "CO2" and v > 1000) else 0
                conn.execute("INSERT INTO environment_measurements(metric,value,unit,location,site,measured_at,exceeded) VALUES(?,?,?,?,?,?,?)", (m, v, u, "Line-A", "Plant-1", now_iso, exceeded))

        if not conn.execute("SELECT 1 FROM alert_events").fetchone():
            conn.execute("INSERT INTO alert_events(rule_name,severity,payload_json,channel,created_at) VALUES(?,?,?,?,?)", ("seed_alert", "medium", json.dumps({"msg":"demo"}), "in_app", now_iso))

        if not conn.execute("SELECT 1 FROM vision_events").fetchone():
            conn.execute("INSERT INTO vision_events(event_type,camera_id,payload_json,created_at) VALUES(?,?,?,?)", ("zone_violation", 1, json.dumps({"class":"person","zone":"restricted-1"}), now_iso))

        if not conn.execute("SELECT 1 FROM rules").fetchone():
            conn.execute("INSERT INTO rules(name,condition_expr,action_expr,enabled,created_at) VALUES(?,?,?,?,?)", ("Dust Threshold", "dust>150", "create_alert+action+notify", 1, now_iso))

        if not conn.execute("SELECT 1 FROM notifications").fetchone():
            conn.execute("INSERT INTO notifications(channel,title,message,status,created_at) VALUES(?,?,?,?,?)", ("in_app", "Demo Notification", "Welcome to SMART SAFETY", "unread", now_iso))

        conn.commit()
