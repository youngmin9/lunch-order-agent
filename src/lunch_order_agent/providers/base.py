"""
역할: 모든 배달 provider가 구현해야 하는 최소 인터페이스를 정의한다.
목적: 배민 iPhone Mirroring과 글로벌 앱 확장을 같은 파이프라인에 연결한다.
맥락: 각 provider는 실제 주문 실행 대신 사람이 검토할 단계와 안전 게이트를 반환한다.
"""

from __future__ import annotations

from typing import Protocol

from lunch_order_agent.models import OrderIntent, OrderPlan


class Provider(Protocol):
    """역할/목적/맥락: provider 구현체가 주문 준비 플랜을 만들 수 있음을 표현한다."""

    name: str

    def build_plan(self, intent: OrderIntent) -> OrderPlan:
        """주문 의도를 provider별 단계로 변환한다."""

