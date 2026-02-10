from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import CSVUpload


@dataclass(frozen=True)
class PlanPolicy:
    upload_limit: int | None


PLAN_POLICIES: dict[str, PlanPolicy] = {
    "free": PlanPolicy(upload_limit=10),
    "pro": PlanPolicy(upload_limit=250),
    "enterprise": PlanPolicy(upload_limit=None),
}


def get_plan_policy(plan_name: str) -> PlanPolicy:
    return PLAN_POLICIES.get(plan_name.lower(), PLAN_POLICIES["free"])


def assert_upload_allowed(db: Session, company_id: int, subscription_tier: str) -> None:
    policy = get_plan_policy(subscription_tier)
    if policy.upload_limit is None:
        return

    upload_count = db.scalar(select(func.count(CSVUpload.id)).where(CSVUpload.company_id == company_id)) or 0
    if upload_count >= policy.upload_limit:
        raise ValueError(
            f"Upload quota reached for '{subscription_tier}' plan. "
            f"Limit: {policy.upload_limit} uploads."
        )
