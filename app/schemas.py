"""Pydantic schemas for API contracts."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import ApplicationStatus, ProductType


class HealthResponse(BaseModel):
    status: str


class ApplicationCreateRequest(BaseModel):
    amount: int = Field(gt=0)
    monthly_income: int = Field(gt=0)
    employment_months: int = Field(ge=0)
    external_score: int = Field(ge=0, le=1000)
    product: ProductType


class EvaluationResultSchema(BaseModel):
    status: ApplicationStatus
    rejection_reasons: list[str] = Field(default_factory=list)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: int
    monthly_income: int
    employment_months: int
    external_score: int
    product: ProductType
    status: ApplicationStatus
    rejection_reasons: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
