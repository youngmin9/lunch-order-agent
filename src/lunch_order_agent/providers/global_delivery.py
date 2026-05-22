"""
역할: Amazon Fresh 등 글로벌 배달/장보기 앱의 키워드 주문 준비 플랜을 만든다.
목적: 지역별 앱이 달라도 동일한 메뉴 키워드, 가격 상한, 주소 라벨, 수동 결제 게이트를 재사용한다.
맥락: 각 글로벌 provider는 웹/앱 검색 전략만 다르고 결제 자동화 금지 원칙은 동일하다.
"""

from __future__ import annotations

from dataclasses import dataclass

from lunch_order_agent.models import Action, OrderIntent, OrderPlan


@dataclass(frozen=True)
class GlobalProfile:
    """역할/목적/맥락: 글로벌 배달 provider별 검색/주소/장바구니 특징을 표현한다."""

    name: str
    display_name: str
    channel: str
    search_hint: str
    address_hint: str


PROFILES: dict[str, GlobalProfile] = {
    "amazon_fresh": GlobalProfile(
        name="amazon_fresh",
        display_name="Amazon Fresh / Whole Foods Market",
        channel="web_or_app",
        search_hint="grocery search에서 high protein salad, chicken breast salad, smoked duck salad 계열을 검색한다.",
        address_hint="배송 주소/장바구니 주소가 회사 또는 업무 주소 프로필인지 확인한다.",
    ),
    "uber_eats": GlobalProfile(
        name="uber_eats",
        display_name="Uber Eats",
        channel="web_or_app",
        search_hint="restaurant search에서 poke, salad, high protein, chicken breast를 검색한다.",
        address_hint="saved place 중 work/company label을 선택한다.",
    ),
    "doordash": GlobalProfile(
        name="doordash",
        display_name="DoorDash",
        channel="web_or_app",
        search_hint="store/menu search에서 salad, poke, chicken protein 키워드를 검색한다.",
        address_hint="saved address 중 work label을 선택한다.",
    ),
    "deliveroo": GlobalProfile(
        name="deliveroo",
        display_name="Deliveroo",
        channel="web_or_app",
        search_hint="restaurant search에서 salad/poke/protein bowl 키워드를 검색한다.",
        address_hint="saved address 중 office/work label을 선택한다.",
    ),
    "generic_delivery_app": GlobalProfile(
        name="generic_delivery_app",
        display_name="Generic delivery app",
        channel="web_or_app",
        search_hint="앱의 검색창에서 지역, 음식 종류, 단백질 키워드를 조합해 검색한다.",
        address_hint="최근 주소 또는 저장 주소 중 업무/회사 라벨을 선택한다.",
    ),
}


def global_profiles() -> list[str]:
    """등록된 글로벌 provider 이름을 반환한다."""

    return list(PROFILES)


class GlobalKeywordDeliveryProvider:
    """글로벌 배달/장보기 앱용 키워드 기반 provider."""

    def __init__(self, profile_name: str) -> None:
        if profile_name not in PROFILES:
            raise ValueError(f"Unknown global profile: {profile_name}")
        self.profile = PROFILES[profile_name]
        self.name = profile_name

    def build_plan(self, intent: OrderIntent) -> OrderPlan:
        """글로벌 앱에서 동일한 키워드/가격/주소/결제 정책을 적용하는 플랜을 만든다."""

        preferred_keywords = ", ".join(intent.preferred_keywords)
        forbidden = ", ".join(intent.payment_policy.forbidden_method_contains)
        preferred_payment = intent.payment_policy.preferred_method_contains
        actions = [
            Action(
                f"Open {self.profile.display_name}",
                f"{self.profile.channel} 경로로 서비스를 열고 로그인/지역 접근 권한을 확인한다.",
                manual_required=True,
            ),
            Action(
                "Apply delivery area",
                f"{intent.service_area} 또는 현재 업무 위치 주변으로 배달/픽업 가능 범위를 맞춘다.",
            ),
            Action(
                "Search by keywords",
                f"{self.profile.search_hint} 선호 키워드: {preferred_keywords}.",
            ),
            Action(
                "Filter by price",
                f"상품/메뉴 가격이 {intent.max_item_price_krw:,}원 상당 이하인지 확인한다.",
            ),
            Action(
                "Select work address",
                f"{self.profile.address_hint} 목표 라벨: {intent.address_label}.",
                manual_required=True,
            ),
            Action(
                "Verify payment preference",
                (
                    f"결제수단이 '{preferred_payment}' 계열인지 확인한다. "
                    f"{forbidden} 계열이 보이면 결제 단계로 진행하지 않는다."
                ),
                manual_required=True,
            ),
            Action(
                "Stop before final payment",
                "장바구니/주문 확인 화면에서 멈추고 사용자가 직접 결제한다.",
                manual_required=True,
            ),
        ]
        safety_gates = [
            "지역/통화/배달 가능 여부가 다르면 중단한다.",
            "자동 결제, 자동 팁 선택, 자동 구독 가입을 하지 않는다.",
            "가격/수수료/배달비가 상한을 넘으면 사용자 확인으로 전환한다.",
            "주소 라벨이 회사/work로 확인되지 않으면 중단한다.",
        ]
        return OrderPlan(
            provider=self.name,
            intent_label=intent.label,
            actions=actions,
            safety_gates=safety_gates,
            stops_before_payment=intent.payment_policy.stop_before_payment,
        )
