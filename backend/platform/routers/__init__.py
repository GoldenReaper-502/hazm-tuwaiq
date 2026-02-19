from .core_api import router as core_router
from .health import router as health_router
from .auth import router as auth_router
from .governance import router as governance_router
from .incidents import router as incidents_router
from .observations import router as observations_router
from .environment import router as environment_router
from .behavior_analytics import router as behavior_router
from .alerts import router as alerts_router
from .reports import router as reports_router
from .predictive import router as predictive_router
from .integrations import router as integrations_router
from .training import router as training_router
from .ptw import router as ptw_router
from .risk import router as risk_router
from .vision import router as vision_router
from .dashboard import router as dashboard_router
from .recommendations import router as recommendations_router
from .cameras import router as cameras_router
from .assistant import router as assistant_router
from .risks import router as risks_router
from .inspections import router as inspections_router
from .behavior import router as behavior_v2_router
from .rules import router as rules_router
from .notifications import router as notifications_router
from .ops import router as ops_router

ALL_ROUTERS = [
    core_router, health_router, auth_router, governance_router, cameras_router,
    incidents_router, observations_router, behavior_v2_router, risks_router, risk_router,
    inspections_router, environment_router, behavior_router, alerts_router, reports_router,
    predictive_router, integrations_router, training_router, ptw_router, vision_router,
    assistant_router, rules_router, notifications_router, ops_router,
    dashboard_router, recommendations_router,
]
