"""Enterprise feature catalog and phased rollout guidance (AI 2.0 + Phase X)."""

from __future__ import annotations

from typing import Any, Dict, List

FEATURE_CATALOG: List[Dict[str, Any]] = [
    {
        "domain": "AI Strategic Intelligence Layer",
        "items": [
            {
                "name": "Safety Maturity Score (SMS)",
                "capabilities": [
                    "Score maturity using incidents, closure speed, compliance, and recurrence",
                    "Grade model A/B/C/D at site and company levels",
                ],
                "priority": "P0",
            },
            {
                "name": "AI Executive Forecast",
                "capabilities": [
                    "Forecast 30-day incident volume",
                    "Predict next risk hotspots",
                    "Estimate severe incident probability",
                ],
                "priority": "P0",
            },
            {
                "name": "Dynamic AI Risk Engine v2",
                "capabilities": [
                    "Risk scoring using time, weather, worker count, and incident history",
                    "Risk Spike Alerts / Risk Drift Detection / Risk Trend Forecast",
                ],
                "priority": "P0",
            },
            {
                "name": "Incident Root Cause AI",
                "capabilities": [
                    "Suggest likely root causes and confidence per cause",
                    "Recommend corrective actions on incident creation",
                ],
                "priority": "P0",
            },
            {
                "name": "AI Safety Copilot",
                "capabilities": [
                    "Explain risks and required controls",
                    "Propose policies and answer safety/compliance questions",
                ],
                "priority": "P1",
            },
        ],
    },
    {
        "domain": "Enterprise Organization Engine",
        "items": [
            {
                "name": "Hierarchical Structure Engine",
                "capabilities": [
                    "Model companies, sites, departments, teams, and workers",
                    "Apply dynamic access controls based on hierarchy",
                ],
                "priority": "P0",
            },
            {
                "name": "Dynamic Role Builder",
                "capabilities": [
                    "Create custom roles",
                    "Granular permission matrix",
                    "Role templates for reuse",
                ],
                "priority": "P0",
            },
            {
                "name": "Multi-Company Mode",
                "capabilities": [
                    "Tenant data isolation (users/sites/reports)",
                    "Cross-tenant governance controls",
                ],
                "priority": "P0",
            },
            {
                "name": "Feature Flag Engine",
                "capabilities": [
                    "Enable/disable features by plan, company, and environment",
                ],
                "priority": "P1",
            },
        ],
    },
    {
        "domain": "Advanced Analytics Engine",
        "items": [
            {
                "name": "Root Cause Trend Graph",
                "capabilities": [
                    "Most frequent causes by site and by team",
                    "Trend lines over configurable periods",
                ],
                "priority": "P1",
            },
            {
                "name": "Risk Correlation Engine",
                "capabilities": [
                    "Correlate weather × incidents",
                    "Correlate working hours × risky behavior",
                    "Correlate equipment type × injuries",
                ],
                "priority": "P1",
            },
            {
                "name": "Behavior Heatmap Timeline",
                "capabilities": [
                    "Interactive unsafe behavior heatmap",
                    "Hourly/daily/weekly timeline views",
                ],
                "priority": "P1",
            },
            {
                "name": "Executive AI Summary Panel",
                "capabilities": [
                    "Top-level daily summary with recommendations",
                    "Overall safety level and improvement ratio",
                ],
                "priority": "P0",
            },
            {
                "name": "Safety Performance Index (SPI)",
                "capabilities": [
                    "0-100 score from incidents, response speed, and compliance",
                ],
                "priority": "P0",
            },
            {
                "name": "Before/After Safety Analyzer",
                "capabilities": [
                    "Compare KPI baseline before/after rollout",
                    "Quantify improvement percentage",
                ],
                "priority": "P1",
            },
            {
                "name": "Risk Simulation Mode",
                "capabilities": [
                    "What-if scenarios for workforce + climate changes",
                    "Projected operational risk impact",
                ],
                "priority": "P2",
            },
            {
                "name": "Auto-Generated Board Report",
                "capabilities": [
                    "Executive-ready report with KPI, SPI, risk forecast, incident cost",
                ],
                "priority": "P1",
            },
        ],
    },
    {
        "domain": "Autonomous Safety & Live Integration",
        "items": [
            {
                "name": "Auto-Mitigation Mode",
                "capabilities": [
                    "Auto-create incident for high-risk detections",
                    "Attach corrective action recommendation",
                    "Assign owner with SLA",
                ],
                "priority": "P0",
            },
            {
                "name": "Smart Escalation 2.0",
                "capabilities": [
                    "Escalation by risk severity, time window, and location",
                ],
                "priority": "P0",
            },
            {
                "name": "Predictive Alert Engine",
                "capabilities": [
                    "Pre-incident proactive alerts",
                    "Severity and role-aware notification routing",
                ],
                "priority": "P0",
            },
            {
                "name": "Smart Zone Lockdown",
                "capabilities": [
                    "Digitally lock dangerous zones",
                    "Prevent worker access and auto-notify teams",
                ],
                "priority": "P0",
            },
            {
                "name": "Live Sensor API",
                "capabilities": [
                    "Ingest temperature, gas, noise, vibration streams",
                    "Unified sensor data contracts",
                ],
                "priority": "P1",
            },
            {
                "name": "Camera Intelligence Dashboard",
                "capabilities": [
                    "PPE detection overview",
                    "Crowding and fall detection feed",
                ],
                "priority": "P1",
            },
            {
                "name": "Fatigue Prediction Model",
                "capabilities": [
                    "Predict fatigue before incidents",
                    "Supervisor early warning queue",
                ],
                "priority": "P1",
            },
            {
                "name": "Safety Digital Twin",
                "capabilities": [
                    "Digital twin of sites and hazards",
                    "Simulate worker density/equipment/risk",
                    "Predict incident likelihood and hotspots with optimization hints",
                ],
                "priority": "P2",
            },
        ],
    },
    {
        "domain": "Cyber, Compliance & Forensics",
        "items": [
            {
                "name": "Compliance Engine",
                "capabilities": [
                    "Coverage for ISO 45001, OSHA, ESG",
                    "Compliance ratio + weakness points",
                ],
                "priority": "P0",
            },
            {
                "name": "Forensic Audit Replay",
                "capabilities": [
                    "Replay who did what, when, and from which device",
                    "Forensic export with timeline evidence",
                ],
                "priority": "P1",
            },
            {
                "name": "AI Anomaly Login Detection",
                "capabilities": [
                    "IP and device anomaly scoring",
                    "Adaptive suspicious access handling",
                ],
                "priority": "P1",
            },
            {
                "name": "Human Risk Profile",
                "capabilities": [
                    "Per-worker risk profile from behavior, violations, and work hours",
                ],
                "priority": "P1",
            },
        ],
    },
    {
        "domain": "SaaS Monetization & Global Readiness",
        "items": [
            {
                "name": "Subscription & Billing Ready",
                "capabilities": [
                    "Basic/Pro/Enterprise plans",
                    "Feature entitlements per subscription",
                ],
                "priority": "P0",
            },
            {
                "name": "Usage-Based Billing",
                "capabilities": [
                    "Meter users, incidents, and cameras",
                    "Variable billing by consumption",
                ],
                "priority": "P1",
            },
            {
                "name": "Global Mode",
                "capabilities": [
                    "Multi-language + multi-currency + timezone-aware operations",
                ],
                "priority": "P1",
            },
            {
                "name": "PWA + Offline Sync Mode",
                "capabilities": [
                    "Offline field operations",
                    "Reliable background synchronization",
                ],
                "priority": "P1",
            },
            {
                "name": "White Label Mode",
                "capabilities": ["Tenant-level branding and UX customization"],
                "priority": "P1",
            },
            {
                "name": "IoT Integration Ready",
                "capabilities": [
                    "Device onboarding standards and integration SDK contracts",
                ],
                "priority": "P2",
            },
            {
                "name": "API Marketplace",
                "capabilities": [
                    "Partner APIs packaging, governance, and monetization",
                ],
                "priority": "P2",
            },
        ],
    },
]

PHASES: List[Dict[str, Any]] = [
    {
        "phase": "Phase 1 - Core Enterprise Control (0-45 days)",
        "focus": [
            "P0 governance and alerts",
            "executive intelligence baseline",
            "tenant + billing foundations",
        ],
        "deliverables": [
            "Safety Maturity Score + AI Executive Forecast",
            "Hierarchical Structure Engine + Dynamic Role Builder",
            "Auto-Mitigation + Smart Escalation 2.0 + Predictive Alert Engine",
            "Compliance Engine + SPI + Executive AI Summary",
            "Subscription & Billing Ready",
        ],
    },
    {
        "phase": "Phase 2 - Operational Intelligence (45-120 days)",
        "focus": ["P1 analytics depth", "security forensics", "field optimization"],
        "deliverables": [
            "Root Cause Trend Graph + Risk Correlation Engine",
            "Behavior Heatmap Timeline + Auto-Generated Board Report",
            "Live Sensor API + Camera Intelligence Dashboard",
            "Human Risk Profile + Fatigue Prediction Model",
            "Forensic Audit Replay + AI Anomaly Login Detection",
            "Global Mode + PWA/Offline + Usage-Based Billing",
        ],
    },
    {
        "phase": "Phase X - Strategic Differentiation (120+ days)",
        "focus": ["P2 simulation and platform moat", "investor-grade differentiation"],
        "deliverables": [
            "Safety Digital Twin",
            "Risk Simulation Mode (advanced scenarios)",
            "IoT Integration Ready (ecosystem scale)",
            "API Marketplace",
        ],
    },
]


def _count_priorities(catalog: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"P0": 0, "P1": 0, "P2": 0}
    for group in catalog:
        for item in group["items"]:
            priority = item.get("priority", "P2")
            counts[priority] = counts.get(priority, 0) + 1
    return counts


def get_enterprise_features() -> Dict[str, Any]:
    """Return enterprise feature catalog and suggested implementation sequence."""
    total_features = sum(len(group["items"]) for group in FEATURE_CATALOG)
    return {
        "title": "HAZM TUWAIQ Enterprise Upgrade Roadmap (AI 2.0 + Phase X)",
        "catalog": FEATURE_CATALOG,
        "phased_rollout": PHASES,
        "priority_breakdown": _count_priorities(FEATURE_CATALOG),
        "total_domains": len(FEATURE_CATALOG),
        "total_features": total_features,
    }


def calculate_safety_maturity_score(
    incidents: int,
    avg_closure_hours: float,
    compliance_rate: float,
    recurrence_rate: float,
) -> Dict[str, Any]:
    """Calculate Safety Maturity Score (SMS) and grade (A/B/C/D)."""
    incident_penalty = min(incidents * 2.0, 40.0)
    closure_penalty = min(avg_closure_hours / 3.0, 25.0)
    recurrence_penalty = min(recurrence_rate * 0.25, 20.0)
    compliance_bonus = min(compliance_rate * 0.35, 35.0)

    raw_score = 100.0 - incident_penalty - closure_penalty - recurrence_penalty + compliance_bonus
    score = max(0.0, min(100.0, round(raw_score, 2)))

    if score >= 85:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 55:
        grade = "C"
    else:
        grade = "D"

    return {
        "sms_score": score,
        "grade": grade,
        "drivers": {
            "incident_penalty": round(incident_penalty, 2),
            "closure_penalty": round(closure_penalty, 2),
            "recurrence_penalty": round(recurrence_penalty, 2),
            "compliance_bonus": round(compliance_bonus, 2),
        },
    }


def generate_ai_executive_forecast(
    last_30d_incidents: int,
    open_high_risk_zones: int,
    severe_incident_rate: float,
) -> Dict[str, Any]:
    """Generate a lightweight executive forecast for next 30 days."""
    forecast_incidents = max(0, round(last_30d_incidents * 1.08 + open_high_risk_zones * 0.7))
    severe_probability = max(0.0, min(1.0, round((severe_incident_rate / 100.0) + (open_high_risk_zones * 0.03), 3)))

    return {
        "forecast_window_days": 30,
        "predicted_incidents": forecast_incidents,
        "severe_incident_probability": severe_probability,
        "next_risk_hotspots": [
            "Zone-A" if open_high_risk_zones > 0 else "Stable",
            "Night Shift" if last_30d_incidents >= 10 else "Routine Ops",
        ],
    }


def calculate_usage_billing_estimate(
    plan: str,
    users: int,
    incidents: int,
    cameras: int,
) -> Dict[str, Any]:
    """Estimate usage-based monthly billing by plan."""
    base_prices = {"basic": 199.0, "pro": 499.0, "enterprise": 1299.0}
    plan_key = plan.lower()
    base = base_prices.get(plan_key, base_prices["pro"])

    usage = (users * 2.5) + (incidents * 0.8) + (cameras * 4.0)
    total = round(base + usage, 2)
    return {
        "plan": plan_key,
        "base_cost": round(base, 2),
        "usage_cost": round(usage, 2),
        "estimated_monthly_total": total,
        "currency": "USD",
    }


def build_board_report(
    kpi: Dict[str, Any],
    spi: float,
    risk_forecast: Dict[str, Any],
    incident_cost: float,
) -> Dict[str, Any]:
    """Generate an executive-ready board report payload."""
    return {
        "kpi": kpi,
        "spi": round(spi, 2),
        "risk_forecast": risk_forecast,
        "cost_of_incidents": round(incident_cost, 2),
        "summary": {
            "overall_status": "strong" if spi >= 80 else "watch",
            "recommendation": "Scale preventive controls" if spi >= 80 else "Increase mitigation and supervision",
        },
    }
