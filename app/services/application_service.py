from app.enums import ApplicationStatus, ProductType
from app.models import Application
from app.repositories import ApplicationRepository
from app.schemas import ApplicationCreateRequest
from app.strategies.base import EvaluationInput, EvaluationResult
from app.strategies.factory import get_policy_for_product


class ApplicationNotFoundError(Exception):
    pass


class ApplicationService:
    def __init__(self, repository: ApplicationRepository) -> None:
        self.repository = repository

    def create_application(self, payload: ApplicationCreateRequest) -> Application:
        result = self._evaluate(
            amount=payload.amount,
            monthly_income=payload.monthly_income,
            employment_months=payload.employment_months,
            external_score=payload.external_score,
            product=payload.product,
        )
        return self.repository.create(
            amount=payload.amount,
            monthly_income=payload.monthly_income,
            employment_months=payload.employment_months,
            external_score=payload.external_score,
            product=payload.product,
            status=result.status,
            rejection_reasons=result.rejection_reasons,
        )

    def get_application(self, application_id: int) -> Application | None:
        return self.repository.get_by_id(application_id)

    def get_application_or_raise(self, application_id: int) -> Application:
        application = self.get_application(application_id)
        if application is None:
            raise ApplicationNotFoundError(f"Application not found: {application_id}")
        return application

    def list_applications(
        self,
        *,
        status: ApplicationStatus | None = None,
        product: ProductType | None = None,
    ) -> list[Application]:
        return self.repository.list_applications(status=status, product=product)

    def reevaluate(self, application_id: int) -> Application:
        application = self.get_application_or_raise(application_id)
        result = self._evaluate(
            amount=application.amount,
            monthly_income=application.monthly_income,
            employment_months=application.employment_months,
            external_score=application.external_score,
            product=application.product,
        )
        return self.repository.update_decision(
            application,
            status=result.status,
            rejection_reasons=result.rejection_reasons,
        )

    def _evaluate(
        self,
        *,
        amount: int,
        monthly_income: int,
        employment_months: int,
        external_score: int,
        product: ProductType,
    ) -> EvaluationResult:
        policy = get_policy_for_product(product)
        evaluation_input = EvaluationInput(
            amount=amount,
            monthly_income=monthly_income,
            employment_months=employment_months,
            external_score=external_score,
        )
        return policy.evaluate(evaluation_input)
