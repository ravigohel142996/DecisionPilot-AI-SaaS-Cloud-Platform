from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models.entities import APIMetric, BillingEvent, Company, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview")
def admin_overview(current_user: User = Depends(require_roles("ceo", "cto")), db: Session = Depends(get_db)):
    company_id = current_user.company_id
    total_users = db.scalar(select(func.count(User.id)).where(User.company_id == company_id)) or 0
    total_events = db.scalar(select(func.count(BillingEvent.id)).where(BillingEvent.company_id == company_id)) or 0
    avg_latency = db.scalar(select(func.avg(APIMetric.latency_ms)).where(APIMetric.company_id == company_id)) or 0
    company = db.get(Company, company_id)

    return {
        "company": company.name if company else "Unknown",
        "subscription": {
            "tier": company.subscription_tier if company else "free",
            "status": company.subscription_status if company else "trialing",
        },
        "user_count": total_users,
        "billing_events": total_events,
        "api_avg_latency_ms": round(float(avg_latency), 2),
    }
