# Architecture

## 역할

이 레포는 배달 앱 주문을 결제 직전까지 준비하는 로컬 에이전트 템플릿입니다.

## 목적

반복 점심 주문을 조건 기반으로 줄이되, 결제/주소/카드 선택 같은 고위험 단계는 사람이 확인하게 합니다.

## 통신 방식

- CLI 실행은 동기 방식입니다.
- LaunchAgent 사용 시 macOS가 정해진 시각에 CLI를 실행합니다.
- 배달 앱과의 통신은 비공개 API 호출이 아니라 iPhone Mirroring 또는 사용자가 여는 웹/앱 화면을 전제로 합니다.
- 큐/이벤트 저장소는 기본 사용하지 않습니다.

## 플로우

1. LaunchAgent 또는 사용자가 `lunch-order-agent`를 실행합니다.
2. CLI가 `config/*.json`을 읽어 `OrderIntent`를 생성합니다.
3. provider registry가 `baemin_iphone_mirroring`, `amazon_fresh`, `uber_eats` 등 provider를 선택합니다.
4. provider가 메뉴 검색, 가격 필터, 주소 라벨 확인, 결제수단 확인, 결제 직전 중단 단계로 구성된 `OrderPlan`을 생성합니다.
5. 사용자가 iPhone Mirroring 또는 해당 앱에서 결제를 직접 완료합니다.

## 데이터 참조

- DB 없음
- 비밀값 없음
- 결제정보 저장 없음
- 주소 원문 저장 없음
- source of truth는 `config/*.json`과 provider 구현 파일입니다.

## 스키마 근거

- 주문 의도 스키마: `src/lunch_order_agent/models.py`
- 배민/iPhone Mirroring provider: `src/lunch_order_agent/providers/baemin_iphone_mirroring.py`
- 글로벌 provider: `src/lunch_order_agent/providers/global_delivery.py`

## 실패 지점과 보상 처리

- 앱 로그인/본인확인 필요: 사용자 수동 처리로 전환
- 메뉴 품절/가격 초과: 후보 선택 중단
- 주소 라벨 불명확: 사용자 수동 선택 요구
- 결제수단이 신한이 아니거나 KB/국민: 중단
- iPhone Mirroring 연결 실패: dry-run 플랜과 체크리스트만 출력

