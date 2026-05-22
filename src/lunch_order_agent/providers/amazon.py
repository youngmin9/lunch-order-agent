"""
역할: Amazon Fresh와 일반 Amazon 상품 구매 준비 파이프라인을 제공한다.
목적: 식료품, 가구, 전자제품, 의류, 생활용품을 키워드/가격/배송 제약으로 A/B 테스트한다.
맥락: Amazon 비공개 API나 Buy Now를 사용하지 않고, 장바구니/체크아웃 직전에서 멈춘다.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

from lunch_order_agent.models import Action, AmazonScenario, OrderPlan, PaymentPolicy
from lunch_order_agent.rules import keyword_score, normalize_text


@dataclass(frozen=True)
class AmazonRunResult:
    """역할/목적/맥락: Amazon A/B 시나리오의 정적 실행 가능성 판정 결과를 담는다."""

    scenario: str
    platform: str
    channel: str
    search_url: str
    runnable: bool
    stops_before_payment: bool
    notes: list[str]

    def as_dict(self) -> dict[str, object]:
        """테스트/리포트용 dict로 변환한다."""

        return {
            "scenario": self.scenario,
            "platform": self.platform,
            "channel": self.channel,
            "search_url": self.search_url,
            "runnable": self.runnable,
            "stops_before_payment": self.stops_before_payment,
            "notes": self.notes,
        }


def amazon_search_url(scenario: AmazonScenario, base_url: str = "https://www.amazon.com") -> str:
    """검색어 기반 Amazon 검색 URL을 만든다."""

    query = " ".join(scenario.search_terms)
    if scenario.channel in {"fresh", "whole_foods"}:
        return f"{base_url}/s?k={quote_plus(query)}&i=amazonfresh"
    return f"{base_url}/s?k={quote_plus(query)}"


def candidate_allowed(title: str, price: float, scenario: AmazonScenario) -> bool:
    """후보 상품명이 필수 키워드/금지 키워드/가격 조건을 만족하는지 판정한다."""

    normalized = normalize_text(title)
    if keyword_score(title, scenario.required_any_keywords) == 0:
        return False
    if any(normalize_text(keyword) in normalized for keyword in scenario.forbidden_keywords):
        return False
    return price <= scenario.max_price


def platform_constraints(scenario: AmazonScenario) -> list[str]:
    """플랫폼별 실행 조건과 실패 가능성을 설명한다."""

    constraints = []
    if scenario.platform == "mac_web":
        constraints.extend(
            [
                "Mac 브라우저에서 검색/비교/장바구니 준비 가능",
                "로그인, CAPTCHA, 주소/결제 확인은 사용자 입력 필요",
            ]
        )
    elif scenario.platform == "iphone_app":
        constraints.extend(
            [
                "iPhone Mirroring 또는 iPhone Amazon Shopping 앱에서 실행",
                "앱 권한, Face ID/Touch ID, 보안 확인이 뜨면 사용자 수동 처리 필요",
            ]
        )
    else:
        constraints.append("알 수 없는 플랫폼이므로 dry-run만 허용")

    if scenario.channel in {"fresh", "whole_foods"}:
        constraints.extend(
            [
                "Fresh/Whole Foods 배송창은 지역, Prime 상태, 재고, 시간대에 따라 달라짐",
                "가능한 배송창이 없거나 최소 주문/수수료 조건이 맞지 않으면 중단",
            ]
        )
    else:
        constraints.extend(
            [
                "일반 상품은 검색/장바구니는 상시 가능하지만 Same-Day/overnight 가능 여부는 checkout에서 확정",
                "Buy Now/1-Click/Subscribe & Save처럼 즉시 주문될 수 있는 버튼은 사용 금지",
            ]
        )
    constraints.extend(scenario.delivery_constraints)
    return constraints


class AmazonPurchaseProvider:
    """Amazon Fresh 및 일반 상품 구매 준비 provider."""

    name = "amazon_purchase"

    def build_plan(self, scenario: AmazonScenario) -> OrderPlan:
        """Amazon 시나리오를 사람이 검토 가능한 실행 플랜으로 변환한다."""

        search_url = amazon_search_url(scenario)
        search_terms = ", ".join(scenario.search_terms)
        required = ", ".join(scenario.required_any_keywords)
        forbidden = ", ".join(scenario.forbidden_keywords) or "없음"
        actions = [
            Action(
                "Open Amazon search",
                f"{scenario.platform}에서 검색 URL을 연다: {search_url}",
                manual_required=scenario.platform == "iphone_app",
            ),
            Action(
                "Search and compare",
                f"검색어: {search_terms}. 필수 키워드 중 하나 이상 포함: {required}.",
            ),
            Action(
                "Reject unsafe candidates",
                f"금지 키워드/조건: {forbidden}. 스폰서/광고 상품은 가격·배송 조건이 명확할 때만 후보 유지.",
            ),
            Action(
                "Apply price cap",
                f"상품가가 {scenario.currency} {scenario.max_price:,.2f} 이하인지 확인한다.",
            ),
            Action(
                "Check delivery eligibility",
                "Prime, Same-Day, Fresh/Whole Foods 배송창, 판매자 배송 조건을 checkout 직전에서 재확인한다.",
                manual_required=True,
            ),
            Action(
                "Select address",
                f"배송 주소가 '{scenario.address_label}' 라벨인지 확인한다.",
                manual_required=True,
            ),
            Action(
                "Verify payment method",
                _payment_message(scenario.payment_policy),
                manual_required=True,
            ),
            Action(
                "Stop before placing order",
                "Place your order, Buy Now, 1-Click, Subscribe & Save 확정 버튼을 누르지 않고 사용자 승인으로 넘긴다.",
                manual_required=True,
            ),
        ]
        safety_gates = [
            "Amazon 비공개 API, 세션 쿠키 탈취, 결제 자동 클릭을 사용하지 않는다.",
            "Buy Now/1-Click/Subscribe & Save/auto-buy 버튼은 자동화 금지.",
            "주소/결제수단/배송창/총액은 checkout 직전 사람이 확인한다.",
            "상품 가격 외 배송비, 세금, 팁, Fresh 수수료로 총액 상한을 넘으면 중단한다.",
            *platform_constraints(scenario),
        ]
        return OrderPlan(
            provider=f"{self.name}:{scenario.label}",
            intent_label=scenario.label,
            actions=actions,
            safety_gates=safety_gates,
            stops_before_payment=scenario.payment_policy.stop_before_payment,
        )

    def dry_run(self, scenario: AmazonScenario) -> AmazonRunResult:
        """외부 구매 없이 정적 조건과 URL 생성이 가능한지 검증한다."""

        notes = platform_constraints(scenario)
        runnable = (
            scenario.platform in {"mac_web", "iphone_app"}
            and bool(scenario.search_terms)
            and scenario.max_price > 0
            and scenario.payment_policy.require_manual_payment
            and scenario.payment_policy.stop_before_payment
        )
        return AmazonRunResult(
            scenario=scenario.label,
            platform=scenario.platform,
            channel=scenario.channel,
            search_url=amazon_search_url(scenario),
            runnable=runnable,
            stops_before_payment=scenario.payment_policy.stop_before_payment,
            notes=notes,
        )


def _payment_message(policy: PaymentPolicy) -> str:
    forbidden = ", ".join(policy.forbidden_method_contains)
    return (
        f"결제수단 텍스트에 '{policy.preferred_method_contains}' 계열이 포함되어야 한다. "
        f"{forbidden} 계열이 보이면 중단한다."
    )
