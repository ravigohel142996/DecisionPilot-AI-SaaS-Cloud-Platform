from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.entities import CSVUpload, User
from app.schemas.analysis import DecisionResponse, ScenarioRequest, ScenarioResponse
from app.services.analysis import build_realtime_metrics
from app.services.decision import decision_intelligence, simulate_scenario

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


def _latest_metrics(db: Session, company_id: int) -> dict:
    latest = db.scalar(select(CSVUpload).where(CSVUpload.company_id == company_id).order_by(desc(CSVUpload.created_at)).limit(1))
    nums = []
    if latest:
        for line in latest.analysis_summary.splitlines():
            for token in line.replace(",", " ").split():
                try:
                    nums.append(float(token.split("=")[-1]))
                except ValueError:
                    continue
    import pandas as pd

    synthetic = pd.DataFrame({"revenue": nums[:60] or [150, 170, 190], "cost": nums[:60] or [80, 88, 96]})
    return build_realtime_metrics(synthetic)


@router.get("/decision", response_model=DecisionResponse)
def get_decision_engine(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    metrics = _latest_metrics(db, current_user.company_id)
    return DecisionResponse(**decision_intelligence(metrics))


@router.post("/scenario", response_model=ScenarioResponse)
def scenario_simulator(
    payload: ScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    metrics = _latest_metrics(db, current_user.company_id)
    return ScenarioResponse(
        **simulate_scenario(
            metrics,
            payload.budget_change_pct,
            payload.demand_change_pct,
            payload.hiring_change_pct,
            payload.iterations,
        )
    )
