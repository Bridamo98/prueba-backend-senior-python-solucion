from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.enums import ApplicationStatus


@dataclass(frozen=True, slots=True)
class EvaluationInput:
    amount: int
    monthly_income: int
    employment_months: int
    external_score: int

    @property
    def monthly_installment(self) -> float:
        return self.amount / 12


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    status: ApplicationStatus
    rejection_reasons: list[str] = field(default_factory=list)


class BasePolicy(ABC):
    @abstractmethod
    def evaluate(self, data: EvaluationInput) -> EvaluationResult:
        raise NotImplementedError

    @staticmethod
    def build_result(rejection_reasons: list[str]) -> EvaluationResult:
        status = (
            ApplicationStatus.APPROVED
            if not rejection_reasons
            else ApplicationStatus.REJECTED
        )
        return EvaluationResult(status=status, rejection_reasons=rejection_reasons)
