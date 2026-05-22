"""
역할: 배달의민족을 iPhone Mirroring으로 조작하기 위한 안전한 주문 준비 플랜을 만든다.
목적: 비공개 API 없이 앱 화면 기반으로 가게/메뉴/주소/결제수단 확인 절차를 표준화한다.
맥락: 자동 결제는 하지 않으며, 신한 카드 확인 후 사용자가 직접 결제 버튼을 누르게 한다.
"""

from __future__ import annotations

from lunch_order_agent.models import Action, OrderIntent, OrderPlan


class BaeminIphoneMirroringProvider:
    """배달의민족 iPhone Mirroring provider."""

    name = "baemin_iphone_mirroring"

    def build_plan(self, intent: OrderIntent) -> OrderPlan:
        """혜화 포케/샐러드 주문을 결제 직전까지 준비하는 단계 목록을 만든다."""

        query = " OR ".join(intent.store_query_terms)
        keyword_text = ", ".join(intent.required_any_keywords)
        preferred = intent.payment_policy.preferred_method_contains
        forbidden = ", ".join(intent.payment_policy.forbidden_method_contains)
        actions = [
            Action(
                "Open iPhone Mirroring",
                "Mac에서 iPhone Mirroring을 열고 iPhone 잠금/네트워크 상태를 확인한다.",
            ),
            Action(
                "Open Baemin app",
                "iPhone Mirroring 안에서 배달의민족 앱을 연다. 로그인/본인확인 팝업이 있으면 사용자에게 넘긴다.",
                manual_required=True,
            ),
            Action(
                "Search Hyehwa poke stores",
                f"검색어 후보를 순서대로 사용한다: {query}. 혜화 근처 포케/샐러드 가게만 유지한다.",
            ),
            Action(
                "Filter menu candidates",
                (
                    f"메뉴 텍스트에서 '{keyword_text}' 중 하나 이상을 포함하고 "
                    f"표시 가격이 {intent.max_item_price_krw:,}원 이하인 후보만 고른다."
                ),
            ),
            Action(
                "Select delivery address",
                f"최근 배달지에서 '{intent.address_label}' 라벨 주소를 선택한다.",
                manual_required=True,
            ),
            Action(
                "Check payment method",
                (
                    f"결제수단 텍스트에 '{preferred}'이 포함되어야 한다. "
                    f"{forbidden} 계열이 보이면 중단하고 사용자가 직접 신한 카드로 바꾼다."
                ),
                manual_required=True,
            ),
            Action(
                "Stop before payment",
                "주문 확인 화면에서 멈추고 사용자에게 최종 결제 확인을 요청한다. 결제 버튼은 자동 클릭하지 않는다.",
                manual_required=True,
            ),
        ]
        safety_gates = [
            "비공개 배민 API를 호출하지 않는다.",
            "카드번호/주소 원문/계정 비밀번호를 저장하지 않는다.",
            "배달비, 옵션 추가금, 최소주문금액 때문에 14,000원을 넘으면 중단한다.",
            "결제수단이 신한으로 확인되지 않거나 KB/국민이면 중단한다.",
            "최종 결제 버튼은 사용자만 누른다.",
        ]
        return OrderPlan(
            provider=self.name,
            intent_label=intent.label,
            actions=actions,
            safety_gates=safety_gates,
            stops_before_payment=intent.payment_policy.stop_before_payment,
        )
