from app.enums import ApplicationStatus
from app.strategies.base import EvaluationInput
from app.strategies.card import CardPolicy
from app.strategies.phone import PhonePolicy
from app.strategies.twist import TwistPolicy


def test_phone_policy_approves_when_all_rules_pass():
    policy = PhonePolicy()
    data = EvaluationInput(
        amount=1_200_000,
        monthly_income=4_000_000,
        employment_months=18,
        external_score=720,
    )

    result = policy.evaluate(data)

    assert result.status == ApplicationStatus.APPROVED
    assert result.rejection_reasons == []


def test_phone_policy_rejects_when_rules_fail():
    policy = PhonePolicy()
    data = EvaluationInput(
        amount=6_000_000,
        monthly_income=1_500_000,
        employment_months=6,
        external_score=680,
    )

    result = policy.evaluate(data)

    assert result.status == ApplicationStatus.REJECTED
    assert set(result.rejection_reasons) == {
        "EXTERNAL_SCORE_BELOW_700",
        "EMPLOYMENT_MONTHS_BELOW_12",
        "INSTALLMENT_EXCEEDS_25_PERCENT_INCOME",
    }


def test_twist_policy_approves_when_all_rules_pass():
    policy = TwistPolicy()
    data = EvaluationInput(
        amount=1_200_000,
        monthly_income=2_000_000,
        employment_months=2,
        external_score=650,
    )

    result = policy.evaluate(data)

    assert result.status == ApplicationStatus.APPROVED
    assert result.rejection_reasons == []


def test_twist_policy_rejects_when_rules_fail():
    policy = TwistPolicy()
    data = EvaluationInput(
        amount=7_000_000,
        monthly_income=1_500_000,
        employment_months=2,
        external_score=590,
    )

    result = policy.evaluate(data)

    assert result.status == ApplicationStatus.REJECTED
    assert set(result.rejection_reasons) == {
        "EXTERNAL_SCORE_BELOW_600",
        "INSTALLMENT_EXCEEDS_35_PERCENT_INCOME",
    }


def test_card_policy_approves_with_score_550_or_higher():
    policy = CardPolicy()
    data = EvaluationInput(
        amount=1_200_000,
        monthly_income=1_000_000,
        employment_months=1,
        external_score=560,
    )

    result = policy.evaluate(data)

    assert result.status == ApplicationStatus.APPROVED
    assert result.rejection_reasons == []


def test_card_policy_approves_with_score_500_and_income_3000000_or_higher():
    policy = CardPolicy()
    data = EvaluationInput(
        amount=1_200_000,
        monthly_income=3_000_000,
        employment_months=1,
        external_score=520,
    )

    result = policy.evaluate(data)

    assert result.status == ApplicationStatus.APPROVED
    assert result.rejection_reasons == []


def test_card_policy_rejects_when_score_between_500_and_549_and_income_below_3000000():
    policy = CardPolicy()
    data = EvaluationInput(
        amount=1_200_000,
        monthly_income=2_500_000,
        employment_months=1,
        external_score=520,
    )

    result = policy.evaluate(data)

    assert result.status == ApplicationStatus.REJECTED
    assert result.rejection_reasons == [
        "EXTERNAL_SCORE_BELOW_550_AND_INCOME_BELOW_3000000"
    ]


def test_card_policy_rejects_when_score_below_500():
    policy = CardPolicy()
    data = EvaluationInput(
        amount=1_200_000,
        monthly_income=10_000_000,
        employment_months=1,
        external_score=480,
    )

    result = policy.evaluate(data)

    assert result.status == ApplicationStatus.REJECTED
    assert result.rejection_reasons == ["EXTERNAL_SCORE_BELOW_500"]
