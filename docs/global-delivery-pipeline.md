# Global Delivery Pipeline

## 확장 완료 범위

이 레포는 배민 전용 흐름과 별도로 글로벌 배달/장보기 앱용 키워드 파이프라인을 포함합니다.

지원 provider:

- `amazon_fresh`
- `amazon_purchase`
- `uber_eats`
- `doordash`
- `deliveroo`
- `generic_delivery_app`

## 공통 조건

- 지역/배달 가능 범위를 먼저 확인합니다.
- 메뉴/상품명에서 단백질·샐러드 키워드를 검색합니다.
- 가격 상한을 넘으면 중단합니다.
- 주소는 회사/work 라벨을 확인합니다.
- 결제는 사용자 수동 승인으로 남깁니다.

## Amazon 계열

`amazon_fresh` provider는 Amazon Fresh 또는 Whole Foods Market 같은 장보기/식료품 주문 흐름을 대상으로 합니다.

예시:

```bash
lunch-order-agent --config config/hyehwa_poke_lunch.json --provider amazon_fresh --dry-run
```

`amazon_purchase` provider는 Fresh 장보기와 일반 Amazon 상품 구매를 A/B 테스트합니다.
이 provider는 별도 설정 파일의 시나리오를 읽으며, 실제 구매 버튼을 누르지 않습니다.

```bash
lunch-order-agent --provider amazon_purchase --amazon-ab-config config/amazon_purchase_ab_tests.json --dry-run
lunch-order-agent --provider amazon_purchase --amazon-ab-config config/amazon_purchase_ab_tests.json --amazon-scenario fresh-high-protein-salad-mac --dry-run
```

검색 키워드 예시:

- high protein salad
- chicken breast salad
- smoked duck salad
- protein bowl

일반 상품 A/B 카테고리:

- 가구: ergonomic office chair
- 전자제품: USB C charger, 65W GaN, PD
- 의류: basic white t shirt, cotton
- 생활용품: paper towels

플랫폼 조건:

- `mac_web`: 브라우저 검색/비교/장바구니 준비까지 가능. 로그인, CAPTCHA, 주소/결제 확인은 사용자 입력 필요.
- `iphone_app`: iPhone Mirroring 또는 iPhone Amazon Shopping 앱을 통해 실행. Face ID/Touch ID/보안 확인은 사용자 수동 처리.
- Fresh/Whole Foods: 배송창, Prime/지역, 재고, 최소 주문/수수료가 맞지 않으면 실패로 기록하고 주문 진행 금지.
- 일반 상품: 검색/장바구니 준비는 상시 가능하나 Same-Day/overnight 배송 가능 여부는 checkout 직전 확정.
- `Buy Now`, `Place your order`, `1-Click`, `Subscribe & Save` 확정 버튼은 자동 클릭 금지.

상세 테스트 케이스는 [Amazon Purchase Pipeline](amazon-purchase-pipeline.md)을 기준으로 관리합니다.

## 레스토랑 배달 앱

`uber_eats`, `doordash`, `deliveroo` provider는 레스토랑 검색과 메뉴 검색을 전제로 합니다.

```bash
lunch-order-agent --config config/hyehwa_poke_lunch.json --provider uber_eats --dry-run
```

## 새 provider 추가 방법

1. `src/lunch_order_agent/providers/global_delivery.py`의 `PROFILES`에 새 profile을 추가합니다.
2. `config/*.json`의 `providers`에 profile 이름을 추가합니다.
3. `python -m unittest discover -s tests`로 회귀 검증합니다.
