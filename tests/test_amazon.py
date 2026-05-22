"""
역할: Amazon Fresh 및 일반 상품 구매 준비 파이프라인을 검증한다.
목적: 카테고리별 A/B 시나리오가 검색/필터/결제 중단 조건을 안정적으로 유지하게 한다.
맥락: 실제 Amazon 계정, 장바구니, 결제는 사용하지 않고 정적 dry-run 결과만 검사한다.
"""

from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path

from lunch_order_agent.cli import load_amazon_scenarios, main
from lunch_order_agent.providers.amazon import (
    AmazonPurchaseProvider,
    amazon_search_url,
    candidate_allowed,
)


ROOT = Path(__file__).resolve().parents[1]
AMAZON_CONFIG = ROOT / "config" / "amazon_purchase_ab_tests.json"


class AmazonPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenarios = load_amazon_scenarios(AMAZON_CONFIG)
        self.by_label = {scenario.label: scenario for scenario in self.scenarios}

    def test_all_ab_scenarios_stop_before_payment(self) -> None:
        provider = AmazonPurchaseProvider()
        self.assertGreaterEqual(len(self.scenarios), 6)
        for scenario in self.scenarios:
            with self.subTest(scenario=scenario.label):
                result = provider.dry_run(scenario)
                plan = provider.build_plan(scenario)
                self.assertTrue(result.runnable)
                self.assertTrue(result.stops_before_payment)
                self.assertTrue(plan.stops_before_payment)
                self.assertIn("Place your order", plan.as_text())

    def test_fresh_search_uses_amazon_fresh_index(self) -> None:
        scenario = self.by_label["fresh-high-protein-salad-mac"]
        self.assertIn("i=amazonfresh", amazon_search_url(scenario))

    def test_retail_search_omits_fresh_index(self) -> None:
        scenario = self.by_label["electronics-usbc-charger-mac"]
        url = amazon_search_url(scenario)
        self.assertIn("USB+C+charger", url)
        self.assertNotIn("i=amazonfresh", url)

    def test_candidate_filter_respects_keywords_price_and_forbidden_terms(self) -> None:
        scenario = self.by_label["electronics-usbc-charger-mac"]
        self.assertTrue(candidate_allowed("65W GaN USB C PD charger", 39.99, scenario))
        self.assertFalse(candidate_allowed("65W GaN USB C PD charger", 49.99, scenario))
        self.assertFalse(candidate_allowed("wireless charging pad", 20.0, scenario))
        self.assertFalse(candidate_allowed("65W GaN USB C charger for parts", 9.99, scenario))

    def test_cli_outputs_selected_amazon_json(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(
                [
                    "--provider",
                    "amazon_purchase",
                    "--amazon-ab-config",
                    str(AMAZON_CONFIG),
                    "--amazon-scenario",
                    "household-paper-towels-mac",
                    "--format",
                    "json",
                    "--dry-run",
                ]
            )
        self.assertEqual(code, 0)
        output = stdout.getvalue()
        self.assertIn("household-paper-towels-mac", output)
        self.assertIn("Stop before placing order", output)


if __name__ == "__main__":
    unittest.main()
