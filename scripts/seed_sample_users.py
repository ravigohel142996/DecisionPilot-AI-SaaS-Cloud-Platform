"""Seed sample VisionPilot users for demo environments."""

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import Base, SessionLocal, engine
from app.models.entities import Company, User


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        company = db.scalar(select(Company).where(Company.name == "VisionPilot Demo Corp"))
        if not company:
            company = Company(name="VisionPilot Demo Corp", subscription_tier="enterprise", subscription_status="active")
            db.add(company)
            db.flush()

        users = [
            ("ceo@visionpilot.ai", "CEO User", "ceo"),
            ("cto@visionpilot.ai", "CTO User", "cto"),
            ("manager@visionpilot.ai", "Manager User", "manager"),
            ("analyst@visionpilot.ai", "Analyst User", "analyst"),
        ]

        for email, full_name, role in users:
            existing = db.scalar(select(User).where(User.email == email))
            if existing:
                continue
            db.add(
                User(
                    email=email,
                    full_name=full_name,
                    role=role,
                    hashed_password=get_password_hash("VisionPilot#2026"),
                    company_id=company.id,
                )
            )

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
