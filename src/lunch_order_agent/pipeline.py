"""
역할: 주문 의도와 provider를 결합해 실행 플랜을 만든다.
목적: 배민/iPhone Mirroring과 글로벌 배달 앱 확장을 동일한 CLI에서 사용할 수 있게 한다.
맥락: 이 계층은 앱을 직접 조작하지 않고 provider가 반환한 안전한 단계 목록을 조합한다.
"""

from __future__ import annotations

from lunch_order_agent.models import OrderIntent, OrderPlan
from lunch_order_agent.providers.baemin_iphone_mirroring import BaeminIphoneMirroringProvider
from lunch_order_agent.providers.base import Provider
from lunch_order_agent.providers.global_delivery import GlobalKeywordDeliveryProvider, global_profiles


def provider_registry() -> dict[str, Provider]:
    """사용 가능한 provider 인스턴스를 반환한다."""

    registry: dict[str, Provider] = {
        "baemin_iphone_mirroring": BaeminIphoneMirroringProvider(),
    }
    for profile_name in global_profiles():
        registry[profile_name] = GlobalKeywordDeliveryProvider(profile_name)
    return registry


def build_plan(intent: OrderIntent, provider_name: str) -> OrderPlan:
    """설정된 provider 이름으로 결제 직전까지의 주문 준비 플랜을 생성한다."""

    registry = provider_registry()
    if provider_name not in registry:
        available = ", ".join(sorted(registry))
        raise ValueError(f"Unknown provider '{provider_name}'. Available: {available}")
    return registry[provider_name].build_plan(intent)

