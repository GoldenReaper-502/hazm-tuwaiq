import json
from datetime import datetime, timezone
from typing import Any

from backend.platform.db import get_conn


def audit_event(
    actor: str, action: str, entity: str, entity_id: str, details: Any
) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO audit_logs(actor,action,entity,entity_id,details_json,created_at) VALUES(?,?,?,?,?,?)",
            (
                actor,
                action,
                entity,
                entity_id,
                json.dumps(details, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
