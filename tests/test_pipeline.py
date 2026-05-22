"""
역할: 배민 및 글로벌 provider 플랜 생성을 검증한다.
목적: 모든 provider가 결제 직전 중단 안전 게이트를 유지하는지 확인한다.
맥락: 실제 앱 조작 없이 설정 파일과 provider registry만 테스트한다.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from lunch_order_agent.models import OrderIntent
from lunch_order_agent.pipeline import build_plan, provider_registry


ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        raw = json.loads((ROOT / "config" / "hyehwa_poke_lunch.json").read_text())
        self.intent = OrderIntent.from_dict(raw)

    def test_baemin_plan_stops_before_payment(self) -> None:
        plan = build_plan(self.intent, "baemin_iphone_mirroring")
        self.assertTrue(plan.stops_before_payment)
        self.assertIn("baemin", plan.provider)

    def test_global_profiles_registered(self) -> None:
        registry = provider_registry()
        for provider in ["amazon_fresh", "uber_eats", "doordash", "deliveroo"]:
            self.assertIn(provider, registry)

    def test_all_enabled_providers_build_plan(self) -> None:
        for provider in self.intent.providers:
            plan = build_plan(self.intent, provider)
            self.assertTrue(plan.actions)
            self.assertTrue(plan.stops_before_payment)


if __name__ == "__main__":
    unittest.main()

