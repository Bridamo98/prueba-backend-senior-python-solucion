from app.strategies.base import BasePolicy, EvaluationInput, EvaluationResult


class PhonePolicy(BasePolicy):
    def evaluate(self, data: EvaluationInput) -> EvaluationResult:
        rejection_reasons: list[str] = []

        if data.external_score < 700:
            rejection_reasons.append("EXTERNAL_SCORE_BELOW_700")

        if data.employment_months < 12:
            rejection_reasons.append("EMPLOYMENT_MONTHS_BELOW_12")

        if data.monthly_installment > data.monthly_income * 0.25:
            rejection_reasons.append("INSTALLMENT_EXCEEDS_25_PERCENT_INCOME")

        return self.build_result(rejection_reasons)
