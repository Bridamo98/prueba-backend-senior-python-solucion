from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import ApplicationStatus, ProductType
from app.repositories import ApplicationRepository
from app.schemas import (
    ApplicationCreateRequest,
    ApplicationListResponse,
    ApplicationResponse,
)
from app.services import ApplicationNotFoundError, ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


def get_application_service(db: Session = Depends(get_db)) -> ApplicationService:
    repository = ApplicationRepository(db)
    return ApplicationService(repository)


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_application(
    payload: ApplicationCreateRequest,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    application = service.create_application(payload)
    return ApplicationResponse.model_validate(application)


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    try:
        application = service.get_application_or_raise(application_id)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Application not found") from exc

    return ApplicationResponse.model_validate(application)


@router.post("/{application_id}/reevaluate", response_model=ApplicationResponse)
def reevaluate_application(
    application_id: int,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    try:
        application = service.reevaluate(application_id)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Application not found") from exc

    return ApplicationResponse.model_validate(application)


@router.get("", response_model=ApplicationListResponse)
def list_applications(
    status: ApplicationStatus | None = None,
    product: ProductType | None = None,
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationListResponse:
    applications = service.list_applications(status=status, product=product)
    return ApplicationListResponse(
        items=[ApplicationResponse.model_validate(item) for item in applications]
    )
