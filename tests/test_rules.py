"""
역할: 가격/키워드/결제수단 규칙을 검증한다.
목적: provider가 바뀌어도 안전 게이트가 유지되는지 보장한다.
맥락: 외부 앱이나 네트워크 없이 순수 함수만 테스트한다.
"""

from __future__ import annotations

import unittest

from lunch_order_agent.rules import (
    is_price_allowed,
    matches_required_any,
    parse_krw_price,
    payment_method_allowed,
)


class RuleTests(unittest.TestCase):
    def test_parse_krw_price(self) -> None:
        self.assertEqual(parse_krw_price("고단백 닭가슴살 포케 13,900원"), 13900)

    def test_price_limit_blocks_missing_or_high_price(self) -> None:
        self.assertTrue(is_price_allowed(13000, 14000))
        self.assertFalse(is_price_allowed(15000, 14000))
        self.assertFalse(is_price_allowed(None, 14000))

    def test_keyword_match(self) -> None:
        self.assertTrue(matches_required_any("오리훈제 샐러드", ["닭가슴살", "오리훈제"]))
        self.assertFalse(matches_required_any("파스타", ["닭가슴살", "오리훈제"]))

    def test_payment_policy(self) -> None:
        self.assertTrue(payment_method_allowed("신한카드 1234", "신한", ["KB", "국민"]))
        self.assertFalse(payment_method_allowed("KB국민카드", "신한", ["KB", "국민"]))


if __name__ == "__main__":
    unittest.main()

