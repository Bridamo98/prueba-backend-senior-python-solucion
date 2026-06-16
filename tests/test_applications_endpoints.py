import pytest
from fastapi.testclient import TestClient


def _create_application(client: TestClient, payload: dict) -> dict:
    response = client.post("/applications", json=payload)
    assert response.status_code == 201
    return response.json()


def _phone_approved_payload() -> dict:
    return {
        "amount": 1_200_000,
        "monthly_income": 4_000_000,
        "employment_months": 18,
        "external_score": 720,
        "product": "PHONE",
    }


def _phone_rejected_payload() -> dict:
    return {
        "amount": 6_000_000,
        "monthly_income": 1_500_000,
        "employment_months": 6,
        "external_score": 680,
        "product": "PHONE",
    }


def _twist_approved_payload() -> dict:
    return {
        "amount": 1_200_000,
        "monthly_income": 2_000_000,
        "employment_months": 2,
        "external_score": 650,
        "product": "TWIST",
    }


def _twist_rejected_payload() -> dict:
    return {
        "amount": 7_000_000,
        "monthly_income": 1_500_000,
        "employment_months": 2,
        "external_score": 590,
        "product": "TWIST",
    }


def _card_rejected_payload() -> dict:
    return {
        "amount": 1_200_000,
        "monthly_income": 2_500_000,
        "employment_months": 1,
        "external_score": 520,
        "product": "CARD",
    }


def test_post_applications_persists_and_returns_decision(client: TestClient):
    created = _create_application(client, _phone_approved_payload())

    assert created["status"] == "APPROVED"
    assert created["rejection_reasons"] == []
    assert created["product"] == "PHONE"

    app_id = created["id"]
    get_response = client.get(f"/applications/{app_id}")
    assert get_response.status_code == 200

    fetched = get_response.json()
    assert fetched["id"] == app_id
    assert fetched["amount"] == 1_200_000
    assert fetched["monthly_income"] == 4_000_000
    assert fetched["employment_months"] == 18
    assert fetched["external_score"] == 720
    assert fetched["product"] == "PHONE"
    assert fetched["status"] == "APPROVED"


def test_get_application_returns_404_when_not_found(client: TestClient):
    response = client.get("/applications/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application not found"}


def test_post_reevaluate_recalculates_existing_application(client: TestClient):
    created = _create_application(client, _card_rejected_payload())

    response = client.post(f"/applications/{created['id']}/reevaluate")
    assert response.status_code == 200

    reevaluated = response.json()
    assert reevaluated["id"] == created["id"]
    assert reevaluated["product"] == "CARD"
    assert reevaluated["status"] == "REJECTED"
    assert reevaluated["rejection_reasons"] == [
        "EXTERNAL_SCORE_BELOW_550_AND_INCOME_BELOW_3000000"
    ]


def test_post_reevaluate_returns_404_when_not_found(client: TestClient):
    response = client.post("/applications/9999/reevaluate")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application not found"}


def test_get_applications_lists_with_optional_filters(client: TestClient):
    twist_created = _create_application(client, _twist_approved_payload())
    phone_created = _create_application(client, _phone_rejected_payload())
    card_created = _create_application(client, _card_rejected_payload())

    all_response = client.get("/applications")
    assert all_response.status_code == 200
    all_items = all_response.json()["items"]
    assert [item["id"] for item in all_items] == [
        twist_created["id"],
        phone_created["id"],
        card_created["id"],
    ]

    rejected_response = client.get("/applications?status=REJECTED")
    assert rejected_response.status_code == 200
    rejected_items = rejected_response.json()["items"]
    assert len(rejected_items) == 2
    assert all(item["status"] == "REJECTED" for item in rejected_items)

    twist_response = client.get("/applications?product=TWIST")
    assert twist_response.status_code == 200
    twist_items = twist_response.json()["items"]
    assert len(twist_items) == 1
    assert twist_items[0]["id"] == twist_created["id"]

    approved_twist_response = client.get(
        "/applications?status=APPROVED&product=TWIST"
    )
    assert approved_twist_response.status_code == 200
    approved_twist_items = approved_twist_response.json()["items"]
    assert len(approved_twist_items) == 1
    assert approved_twist_items[0]["id"] == twist_created["id"]
    assert approved_twist_items[0]["status"] == "APPROVED"


@pytest.mark.parametrize(
    ("payload", "expected_reasons"),
    [
        (
            _phone_rejected_payload(),
            {
                "EXTERNAL_SCORE_BELOW_700",
                "EMPLOYMENT_MONTHS_BELOW_12",
                "INSTALLMENT_EXCEEDS_25_PERCENT_INCOME",
            },
        ),
        (
            _twist_rejected_payload(),
            {
                "EXTERNAL_SCORE_BELOW_600",
                "INSTALLMENT_EXCEEDS_35_PERCENT_INCOME",
            },
        ),
        (
            _card_rejected_payload(),
            {"EXTERNAL_SCORE_BELOW_550_AND_INCOME_BELOW_3000000"},
        ),
    ],
    ids=["phone", "twist", "card"],
)
def test_post_applications_rejects_by_policy(
    client: TestClient,
    payload: dict,
    expected_reasons: set[str],
):
    created = _create_application(client, payload)

    assert created["status"] == "REJECTED"
    assert set(created["rejection_reasons"]) == expected_reasons
