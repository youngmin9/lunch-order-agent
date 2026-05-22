# Lunch Order Agent

평일 점심 주문을 "결제 직전"까지 준비하는 안전한 로컬 에이전트입니다.

기본 예시는 다음 조건을 사용합니다.

- 시간: 평일 11:00, Asia/Seoul
- 위치/가게군: 혜화 근처 포케/샐러드 가게
- 가격: 메뉴 14,000원 이하
- 키워드: 고단백, 닭가슴살, 오리훈제, 샐러드, 포케
- 주소: 최근 배달지 중 `회사` 라벨
- 결제: 최종 결제는 사용자가 직접 수행
- 결제수단 확인: `신한` 포함 결제수단 선호, `KB`/`국민` 결제수단이면 중단

이 레포는 배달 앱의 비공개 API를 호출하거나 결제를 자동 실행하지 않습니다. 앱 화면을 준비하고, 주문 조건을 검증하고, 결제 직전에서 멈추도록 설계되어 있습니다.

## 빠른 시작

```bash
git clone https://github.com/youngmin9/lunch-order-agent.git
cd lunch-order-agent
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

기본 혜화 점심 플랜을 dry-run으로 확인합니다.

```bash
lunch-order-agent --config config/hyehwa_poke_lunch.json --provider baemin_iphone_mirroring --dry-run
```

글로벌 배달/장보기 앱 확장 플랜을 확인합니다.

```bash
lunch-order-agent --config config/hyehwa_poke_lunch.json --provider amazon_fresh --dry-run
lunch-order-agent --config config/hyehwa_poke_lunch.json --provider uber_eats --dry-run
lunch-order-agent --config config/hyehwa_poke_lunch.json --provider doordash --dry-run
lunch-order-agent --config config/hyehwa_poke_lunch.json --provider deliveroo --dry-run
```

지원 provider 목록을 봅니다.

```bash
lunch-order-agent --list-providers
```

## 실제 사용 전 체크

1. iPhone Mirroring이 Mac에서 열리고 iPhone 잠금 해제가 되어 있어야 합니다.
2. 배달의민족 앱에 `회사` 라벨 주소가 최근 배달지로 남아 있어야 합니다.
3. 결제수단 목록에서 `신한` 카드가 선택 가능해야 합니다.
4. `KB`/`국민` 카드가 기본 결제수단이면 자동 진행하지 말고 사용자가 직접 바꿉니다.
5. 최종 `결제하기` 버튼은 사용자가 직접 누릅니다.

## LaunchAgent 예시

`examples/com.youngmin9.lunch-order-agent.plist`를 `~/Library/LaunchAgents/`로 복사하고 경로를 본인 checkout 경로로 바꿉니다.

```bash
cp examples/com.youngmin9.lunch-order-agent.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.youngmin9.lunch-order-agent.plist
```

이 예시는 월-금 11:00에 실행되도록 구성되어 있습니다.

## 안전 원칙

- 카드번호, 배민 계정, 배달 주소 원문을 저장하지 않습니다.
- 비공개 API 리버스엔지니어링을 하지 않습니다.
- 결제를 자동 클릭하지 않습니다.
- 메뉴 품절, 배달비, 최소주문금액, 옵션 추가금이 있으면 사용자 확인으로 전환합니다.
- 앱 화면 인식이 실패하면 fallback으로 주문 후보와 체크리스트만 출력합니다.

## 문서

- [Architecture](docs/architecture.md)
- [iPhone Mirroring Runbook](docs/iphone-mirroring-runbook.md)
- [Global Delivery Pipeline](docs/global-delivery-pipeline.md)
