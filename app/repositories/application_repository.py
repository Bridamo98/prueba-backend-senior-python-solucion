from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import ApplicationStatus, ProductType
from app.models import Application


class ApplicationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        amount: int,
        monthly_income: int,
        employment_months: int,
        external_score: int,
        product: ProductType,
        status: ApplicationStatus,
        rejection_reasons: list[str] | None = None,
    ) -> Application:
        application = Application(
            amount=amount,
            monthly_income=monthly_income,
            employment_months=employment_months,
            external_score=external_score,
            product=product,
            status=status,
            rejection_reasons=rejection_reasons or [],
        )
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_by_id(self, application_id: int) -> Application | None:
        return self.db.get(Application, application_id)

    def list_applications(
        self,
        *,
        status: ApplicationStatus | None = None,
        product: ProductType | None = None,
    ) -> list[Application]:
        stmt = select(Application).order_by(Application.id.asc())

        if status is not None:
            stmt = stmt.where(Application.status == status)

        if product is not None:
            stmt = stmt.where(Application.product == product)

        return self.db.scalars(stmt).all()

    def update_decision(
        self,
        application: Application,
        *,
        status: ApplicationStatus,
        rejection_reasons: list[str],
    ) -> Application:
        application.status = status
        application.rejection_reasons = rejection_reasons
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application
