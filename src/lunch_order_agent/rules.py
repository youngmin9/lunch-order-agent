"""
역할: 메뉴 후보의 가격/키워드/결제수단 조건을 판정한다.
목적: 앱별 화면 자동화와 무관하게 동일한 주문 안전 규칙을 재사용하게 한다.
맥락: 실제 배달 앱 화면에서 읽은 텍스트나 사용자가 입력한 후보 텍스트를 평가하는 순수 함수다.
"""

from __future__ import annotations

import re


def normalize_text(value: str) -> str:
    """검색/검증 비교를 위해 공백과 대소문자를 단순화한다."""

    return re.sub(r"\s+", "", value).lower()


def keyword_score(text: str, keywords: list[str]) -> int:
    """후보 텍스트에 포함된 선호 키워드 개수를 계산한다."""

    normalized = normalize_text(text)
    return sum(1 for keyword in keywords if normalize_text(keyword) in normalized)


def matches_required_any(text: str, keywords: list[str]) -> bool:
    """필수 키워드 중 하나라도 포함되는지 확인한다."""

    return keyword_score(text, keywords) > 0


def parse_krw_price(text: str) -> int | None:
    """'13,900원' 같은 화면 텍스트에서 원화 가격을 추출한다."""

    match = re.search(r"(\d{1,3}(?:,\d{3})+|\d+)\s*원?", text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def is_price_allowed(price_krw: int | None, max_price_krw: int) -> bool:
    """가격이 없으면 자동 진행을 막고, 가격이 있으면 상한 이하인지 확인한다."""

    return price_krw is not None and price_krw <= max_price_krw


def payment_method_allowed(
    observed_text: str,
    preferred_contains: str,
    forbidden_contains: list[str],
) -> bool:
    """관찰된 결제수단 텍스트가 선호 카드이고 금지 카드가 아닌지 확인한다."""

    normalized = normalize_text(observed_text)
    if normalize_text(preferred_contains) not in normalized:
        return False
    return not any(normalize_text(forbidden) in normalized for forbidden in forbidden_contains)

