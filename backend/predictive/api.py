"""
HAZM TUWAIQ - Predictive Safety API
ML predictions, trend analysis, digital twins, and risk heatmaps
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from .models import (
    Prediction, TrendAnalysis, RiskHeatmap,
    SafetyTwin, ProactiveRecommendation,
    PredictionRequest, TrendAnalysisRequest,
    RiskHeatmapRequest, SafetyTwinUpdate,
    PredictionType, TimeFrame
)
from .prediction_engine import get_prediction_engine
from .trend_analyzer import get_trend_analyzer
from .safety_twin import get_safety_twin
from .risk_mapper import get_risk_mapper


# ═══════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════

router = APIRouter()

# Initialize managers
prediction_engine = get_prediction_engine()
trend_analyzer = get_trend_analyzer()
safety_twin = get_safety_twin()
risk_mapper = get_risk_mapper()


# In-memory databases
PREDICTIONS_DB: Dict[str, Prediction] = {}
TRENDS_DB: Dict[str, TrendAnalysis] = {}
HEATMAPS_DB: Dict[str, RiskHeatmap] = {}
RECOMMENDATIONS_DB: Dict[str, ProactiveRecommendation] = {}


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def create_response(
    success: bool,
    message: str,
    data: Any = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """Create unified JSON response"""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    if error:
        response["error"] = error
    
    return response


# ═══════════════════════════════════════════════════════════
# PREDICTION ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/predictions", summary="إنشاء تنبؤ - Generate Prediction")
async def create_prediction(
    request: PredictionRequest
):
    """
    Generate ML-powered safety prediction
    
    - **Incident Probability**: Predict likelihood of incidents
    - **Near-Miss Forecast**: Forecast near-miss patterns
    - **Risk Score**: Calculate comprehensive risk
    - **Confidence**: Prediction confidence level
    """
    try:
        # Generate prediction based on type
        if request.prediction_type == PredictionType.INCIDENT_PROBABILITY:
            prediction = prediction_engine.predict_incident_probability(
                target=request.target,
                organization_id=request.organization_id,
                forecast_period=request.forecast_period
            )
        
        elif request.prediction_type == PredictionType.NEAR_MISS_FORECAST:
            prediction = prediction_engine.predict_near_miss_forecast(
                target=request.target,
                organization_id=request.organization_id,
                forecast_period=request.forecast_period
            )
        
        elif request.prediction_type == PredictionType.RISK_SCORE:
            prediction = prediction_engine.predict_risk_score(
                target=request.target,
                organization_id=request.organization_id
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported prediction type: {request.prediction_type}"
            )
        
        # Store prediction
        PREDICTIONS_DB[prediction.id] = prediction
        
        return create_response(
            success=True,
            message="Prediction generated successfully",
            data={"prediction": prediction.dict()}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions", summary="قائمة التنبؤات - List Predictions")
async def list_predictions(
    organization_id: str = Query(..., description="Organization ID"),
    prediction_type: Optional[PredictionType] = None,
    target: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Get all predictions with filters"""
    try:
        predictions = [
            p for p in PREDICTIONS_DB.values()
            if p.organization_id == organization_id
        ]
        
        if prediction_type:
            predictions = [p for p in predictions if p.type == prediction_type]
        
        if target:
            predictions = [p for p in predictions if p.target == target]
        
        # Sort by creation date
        predictions = sorted(predictions, key=lambda x: x.created_at, reverse=True)
        predictions = predictions[:limit]
        
        return create_response(
            success=True,
            message=f"Retrieved {len(predictions)} predictions",
            data={
                "predictions": [p.dict() for p in predictions],
                "total": len(predictions)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{prediction_id}", summary="تفاصيل التنبؤ - Get Prediction")
async def get_prediction(prediction_id: str):
    """Get prediction details by ID"""
    try:
        prediction = PREDICTIONS_DB.get(prediction_id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        return create_response(
            success=True,
            message="Prediction retrieved",
            data={"prediction": prediction.dict()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# TREND ANALYSIS ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/trends", summary="تحليل اتجاه - Analyze Trend")
async def analyze_trend(
    request: TrendAnalysisRequest
):
    """
    Analyze historical trends with pattern detection
    
    - **Trend Direction**: Improving, degrading, or stable
    - **Pattern Detection**: Weekly peaks, seasonality
    - **Anomaly Detection**: Statistical outliers
    - **Insights**: AI-generated insights
    """
    try:
        # Analyze trend
        analysis = trend_analyzer.analyze_trend(
            metric=request.metric,
            target=request.target,
            organization_id=request.organization_id,
            time_frame=request.time_frame,
            days_back=request.days_back
        )
        
        # Store analysis
        TRENDS_DB[analysis.id] = analysis
        
        return create_response(
            success=True,
            message="Trend analysis completed",
            data={"analysis": analysis.dict()}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends", summary="قائمة التحليلات - List Trend Analyses")
async def list_trends(
    organization_id: str = Query(..., description="Organization ID"),
    metric: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Get all trend analyses"""
    try:
        trends = [
            t for t in TRENDS_DB.values()
            if t.organization_id == organization_id
        ]
        
        if metric:
            trends = [t for t in trends if t.metric == metric]
        
        trends = sorted(trends, key=lambda x: x.created_at, reverse=True)[:limit]
        
        return create_response(
            success=True,
            message=f"Retrieved {len(trends)} analyses",
            data={"trends": [t.dict() for t in trends]}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# RISK HEATMAP ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/heatmaps", summary="إنشاء خريطة مخاطر - Generate Heatmap")
async def create_heatmap(
    request: RiskHeatmapRequest
):
    """
    Generate spatial risk heatmap
    
    - **Zone Risk Scores**: Risk level per zone
    - **Hot Spots**: Highest risk areas
    - **Risk Distribution**: Risk level breakdown
    - **Visualization Data**: Color-coded mapping
    """
    try:
        # Generate heatmap
        heatmap = risk_mapper.generate_heatmap(
            site_id=request.site_id,
            organization_id=request.organization_id,
            time_period=request.time_period,
            min_risk_threshold=request.min_risk_threshold
        )
        
        # Identify patterns
        patterns = risk_mapper.identify_high_risk_patterns(heatmap)
        
        # Store heatmap
        HEATMAPS_DB[heatmap.id] = heatmap
        
        return create_response(
            success=True,
            message="Risk heatmap generated",
            data={
                "heatmap": heatmap.dict(),
                "patterns": patterns
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmaps", summary="قائمة خرائط المخاطر - List Heatmaps")
async def list_heatmaps(
    organization_id: str = Query(..., description="Organization ID"),
    site_id: Optional[str] = None
):
    """Get all risk heatmaps"""
    try:
        heatmaps = [
            h for h in HEATMAPS_DB.values()
            if h.organization_id == organization_id
        ]
        
        if site_id:
            heatmaps = [h for h in heatmaps if h.site_id == site_id]
        
        heatmaps = sorted(heatmaps, key=lambda x: x.generated_at, reverse=True)
        
        return create_response(
            success=True,
            message=f"Retrieved {len(heatmaps)} heatmaps",
            data={"heatmaps": [h.dict() for h in heatmaps]}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# DIGITAL SAFETY TWIN ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/twins", summary="إنشاء توأم رقمي - Create Digital Twin")
async def create_twin(
    twin_type: str = Query(..., description="Type: site, zone, worker, equipment"),
    twin_name: str = Query(..., description="Twin name"),
    real_entity_id: str = Query(..., description="Real entity ID"),
    organization_id: str = Query(..., description="Organization ID")
):
    """
    Create digital safety twin
    
    - **Real-time Sync**: Synchronized with real-world entity
    - **Safety Score**: Continuous safety monitoring
    - **Predictive Insights**: Future risk predictions
    - **What-If Scenarios**: Simulation capabilities
    """
    try:
        twin = safety_twin.create_twin(
            twin_type=twin_type,
            twin_name=twin_name,
            real_entity_id=real_entity_id,
            organization_id=organization_id
        )
        
        return create_response(
            success=True,
            message="Digital twin created",
            data={"twin": twin.dict()}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/twins/{twin_id}/update", summary="تحديث التوأم - Update Twin")
async def update_twin(
    twin_id: str,
    update: SafetyTwinUpdate
):
    """Update digital twin with real-time data"""
    try:
        twin = safety_twin.update_twin(
            twin_id=twin_id,
            metrics=update.metrics,
            environment=update.environment
        )
        
        return create_response(
            success=True,
            message="Twin updated",
            data={"twin": twin.dict()}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/twins/{twin_id}/simulate", summary="محاكاة سيناريو - Simulate Scenario")
async def simulate_scenario(
    twin_id: str,
    scenario_name: str = Query(..., description="Scenario name"),
    interventions: Dict[str, Any] = Query(..., description="Interventions to apply")
):
    """
    Simulate what-if scenario
    
    - **Baseline vs Projected**: Compare current vs future state
    - **Risk Reduction**: Quantify intervention impact
    - **Cost Estimation**: Implementation cost estimate
    """
    try:
        results = safety_twin.simulate_scenario(
            twin_id=twin_id,
            scenario_name=scenario_name,
            interventions=interventions
        )
        
        return create_response(
            success=True,
            message="Scenario simulated",
            data={"simulation": results}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/twins", summary="قائمة التوائم - List Twins")
async def list_twins(
    organization_id: str = Query(..., description="Organization ID"),
    twin_type: Optional[str] = None
):
    """Get all digital twins"""
    try:
        twins = safety_twin.get_all_twins(
            organization_id=organization_id,
            twin_type=twin_type
        )
        
        return create_response(
            success=True,
            message=f"Retrieved {len(twins)} twins",
            data={"twins": [t.dict() for t in twins]}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/twins/{twin_id}", summary="تفاصيل التوأم - Get Twin")
async def get_twin_details(twin_id: str):
    """Get digital twin details"""
    try:
        twin = safety_twin.get_twin(twin_id)
        
        if not twin:
            raise HTTPException(status_code=404, detail="Twin not found")
        
        return create_response(
            success=True,
            message="Twin retrieved",
            data={"twin": twin.dict()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# STATISTICS ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/stats/overview", summary="إحصائيات عامة - Overall Statistics")
async def get_stats():
    """Get comprehensive predictive module statistics"""
    try:
        prediction_stats = prediction_engine.get_stats()
        twin_stats = safety_twin.get_stats()
        mapper_stats = risk_mapper.get_stats()
        
        return create_response(
            success=True,
            message="Statistics retrieved",
            data={
                "predictions": prediction_stats,
                "digital_twins": twin_stats,
                "risk_mapping": mapper_stats,
                "total_trends": len(TRENDS_DB),
                "total_recommendations": len(RECOMMENDATIONS_DB)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
