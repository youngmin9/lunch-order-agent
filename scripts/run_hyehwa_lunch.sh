#!/usr/bin/env bash
# 역할: 혜화 점심 주문 dry-run 플랜을 실행한다.
# 목적: LaunchAgent나 수동 실행에서 동일한 명령을 재사용하게 한다.
# 맥락: 결제는 자동화하지 않으며, 출력된 플랜을 보고 사용자가 직접 결제한다.
set -euo pipefail

cd "$(dirname "$0")/.."
exec .venv/bin/lunch-order-agent \
  --config config/hyehwa_poke_lunch.json \
  --provider baemin_iphone_mirroring \
  --dry-run

