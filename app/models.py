from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import ApplicationStatus, ProductType


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_income: Mapped[int] = mapped_column(Integer, nullable=False)
    employment_months: Mapped[int] = mapped_column(Integer, nullable=False)
    external_score: Mapped[int] = mapped_column(Integer, nullable=False)
    product: Mapped[ProductType] = mapped_column(
        Enum(ProductType, name="product_type"), nullable=False
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"), nullable=False
    )
    rejection_reasons: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
