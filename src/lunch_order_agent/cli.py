"""
역할: lunch-order-agent 명령행 인터페이스를 제공한다.
목적: 설정 JSON을 읽어 배민/iPhone Mirroring 또는 글로벌 배달 앱 주문 준비 플랜을 출력한다.
맥락: 실행 결과는 dry-run/준비 플랜이며, 결제나 비공개 API 호출을 수행하지 않는다.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lunch_order_agent.models import OrderIntent
from lunch_order_agent.pipeline import build_plan, provider_registry


def load_intent(path: Path) -> OrderIntent:
    """설정 파일을 읽어 주문 의도 모델로 변환한다."""

    return OrderIntent.from_dict(json.loads(path.read_text(encoding="utf-8")))


def build_parser() -> argparse.ArgumentParser:
    """CLI 인자 파서를 구성한다."""

    parser = argparse.ArgumentParser(description="Prepare a manual-payment lunch order plan.")
    parser.add_argument("--config", type=Path, default=Path("config/hyehwa_poke_lunch.json"))
    parser.add_argument("--provider", default="baemin_iphone_mirroring")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan and do not touch apps.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--list-providers", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 진입점."""

    args = build_parser().parse_args(argv)
    if args.list_providers:
        for provider in sorted(provider_registry()):
            print(provider)
        return 0

    intent = load_intent(args.config)
    if args.provider not in intent.providers:
        allowed = ", ".join(intent.providers)
        print(f"Provider '{args.provider}' is not enabled by config. Enabled: {allowed}", file=sys.stderr)
        return 2

    plan = build_plan(intent, args.provider)
    if args.format == "json":
        print(json.dumps(plan.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(plan.as_text())
        if args.dry_run:
            print("\nDry-run only: no app was opened and no payment was attempted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

