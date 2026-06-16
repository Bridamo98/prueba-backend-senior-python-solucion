from app.strategies.base import BasePolicy, EvaluationInput, EvaluationResult


class TwistPolicy(BasePolicy):
    def evaluate(self, data: EvaluationInput) -> EvaluationResult:
        rejection_reasons: list[str] = []

        if data.external_score < 600:
            rejection_reasons.append("EXTERNAL_SCORE_BELOW_600")

        if data.monthly_installment > data.monthly_income * 0.35:
            rejection_reasons.append("INSTALLMENT_EXCEEDS_35_PERCENT_INCOME")

        return self.build_result(rejection_reasons)
