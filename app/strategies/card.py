from app.strategies.base import BasePolicy, EvaluationInput, EvaluationResult


class CardPolicy(BasePolicy):
    def evaluate(self, data: EvaluationInput) -> EvaluationResult:
        is_approved = data.external_score >= 550 or (
            data.external_score >= 500 and data.monthly_income >= 3_000_000
        )

        if is_approved:
            return self.build_result([])

        if data.external_score < 500:
            reasons = ["EXTERNAL_SCORE_BELOW_500"]
        else:
            reasons = ["EXTERNAL_SCORE_BELOW_550_AND_INCOME_BELOW_3000000"]

        return self.build_result(reasons)
