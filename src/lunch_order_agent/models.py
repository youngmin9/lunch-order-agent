"""
역할: 점심 주문 의도, 결제 정책, 실행 플랜의 공통 데이터 모델을 정의한다.
목적: 배민/iPhone Mirroring과 글로벌 배달 앱 provider가 같은 안전 규칙을 공유하게 한다.
맥락: 결제는 자동화하지 않으며, 모든 provider는 결제 직전 사용자 승인 단계에서 멈춘다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PaymentPolicy:
    """역할/목적/맥락: 결제수단 검증과 수동 결제 게이트를 표현한다."""

    preferred_method_contains: str
    forbidden_method_contains: list[str]
    require_manual_payment: bool = True
    stop_before_payment: bool = True


@dataclass(frozen=True)
class Schedule:
    """역할/목적/맥락: 실행 가능한 요일/시각/타임존을 표현한다."""

    days: list[str]
    time: str
    timezone: str


@dataclass(frozen=True)
class OrderIntent:
    """역할/목적/맥락: 사용자가 원하는 메뉴/주소/가격 조건을 provider 독립적으로 표현한다."""

    label: str
    schedule: Schedule
    service_area: str
    store_query_terms: list[str]
    required_any_keywords: list[str]
    preferred_keywords: list[str]
    max_item_price_krw: int
    address_label: str
    payment_policy: PaymentPolicy
    providers: list[str]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "OrderIntent":
        """설정 JSON을 안전한 dataclass 구조로 변환한다."""

        schedule = raw["schedule"]
        payment = raw["payment_policy"]
        return cls(
            label=raw["label"],
            schedule=Schedule(
                days=list(schedule["days"]),
                time=schedule["time"],
                timezone=schedule["timezone"],
            ),
            service_area=raw["service_area"],
            store_query_terms=list(raw["store_query_terms"]),
            required_any_keywords=list(raw["required_any_keywords"]),
            preferred_keywords=list(raw["preferred_keywords"]),
            max_item_price_krw=int(raw["max_item_price_krw"]),
            address_label=raw["address_label"],
            payment_policy=PaymentPolicy(
                preferred_method_contains=payment["preferred_method_contains"],
                forbidden_method_contains=list(payment["forbidden_method_contains"]),
                require_manual_payment=bool(payment.get("require_manual_payment", True)),
                stop_before_payment=bool(payment.get("stop_before_payment", True)),
            ),
            providers=list(raw["providers"]),
        )


@dataclass(frozen=True)
class Action:
    """역할/목적/맥락: provider가 수행하거나 사용자에게 요청할 한 단계를 표현한다."""

    title: str
    detail: str
    manual_required: bool = False


@dataclass(frozen=True)
class OrderPlan:
    """역할/목적/맥락: 주문 준비 절차와 안전 게이트를 사람이 확인 가능한 형태로 묶는다."""

    provider: str
    intent_label: str
    actions: list[Action]
    safety_gates: list[str]
    stops_before_payment: bool

    def as_text(self) -> str:
        """CLI 출력용 텍스트 플랜을 생성한다."""

        lines = [
            f"Provider: {self.provider}",
            f"Intent: {self.intent_label}",
            f"Stops before payment: {self.stops_before_payment}",
            "",
            "Actions:",
        ]
        for index, action in enumerate(self.actions, start=1):
            suffix = " [manual]" if action.manual_required else ""
            lines.append(f"{index}. {action.title}{suffix}")
            lines.append(f"   {action.detail}")
        lines.append("")
        lines.append("Safety gates:")
        for gate in self.safety_gates:
            lines.append(f"- {gate}")
        return "\n".join(lines)

    def as_dict(self) -> dict[str, Any]:
        """JSON 출력용 dict를 생성한다."""

        return {
            "provider": self.provider,
            "intent_label": self.intent_label,
            "stops_before_payment": self.stops_before_payment,
            "actions": [action.__dict__ for action in self.actions],
            "safety_gates": self.safety_gates,
        }


@dataclass(frozen=True)
class AmazonScenario:
    """역할/목적/맥락: Amazon Fresh/일반 상품 A/B 테스트 한 케이스를 표현한다."""

    label: str
    category: str
    channel: str
    platform: str
    search_terms: list[str]
    required_any_keywords: list[str]
    forbidden_keywords: list[str]
    max_price: float
    currency: str
    address_label: str
    delivery_constraints: list[str]
    payment_policy: PaymentPolicy

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "AmazonScenario":
        """설정 JSON의 scenario 항목을 dataclass로 변환한다."""

        payment = raw["payment_policy"]
        return cls(
            label=raw["label"],
            category=raw["category"],
            channel=raw["channel"],
            platform=raw["platform"],
            search_terms=list(raw["search_terms"]),
            required_any_keywords=list(raw["required_any_keywords"]),
            forbidden_keywords=list(raw.get("forbidden_keywords", [])),
            max_price=float(raw["max_price"]),
            currency=raw["currency"],
            address_label=raw["address_label"],
            delivery_constraints=list(raw["delivery_constraints"]),
            payment_policy=PaymentPolicy(
                preferred_method_contains=payment["preferred_method_contains"],
                forbidden_method_contains=list(payment["forbidden_method_contains"]),
                require_manual_payment=bool(payment.get("require_manual_payment", True)),
                stop_before_payment=bool(payment.get("stop_before_payment", True)),
            ),
        )
