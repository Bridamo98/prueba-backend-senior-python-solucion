from app.enums import ProductType
from app.strategies.base import BasePolicy
from app.strategies.card import CardPolicy
from app.strategies.phone import PhonePolicy
from app.strategies.twist import TwistPolicy


class PolicyFactory:
    _registry: dict[ProductType, BasePolicy] = {
        ProductType.PHONE: PhonePolicy(),
        ProductType.TWIST: TwistPolicy(),
        ProductType.CARD: CardPolicy(),
    }

    @classmethod
    def get_policy(cls, product: ProductType) -> BasePolicy:
        try:
            return cls._registry[product]
        except KeyError as exc:
            raise ValueError(f"Unsupported product type: {product}") from exc


def get_policy_for_product(product: ProductType) -> BasePolicy:
    return PolicyFactory.get_policy(product)
