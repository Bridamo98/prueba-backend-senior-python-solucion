from enum import Enum


class ProductType(str, Enum):
    PHONE = "PHONE"
    TWIST = "TWIST"
    CARD = "CARD"


class ApplicationStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
