# Global Delivery Pipeline

## 확장 완료 범위

이 레포는 배민 전용 흐름과 별도로 글로벌 배달/장보기 앱용 키워드 파이프라인을 포함합니다.

지원 provider:

- `amazon_fresh`
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

검색 키워드 예시:

- high protein salad
- chicken breast salad
- smoked duck salad
- protein bowl

## 레스토랑 배달 앱

`uber_eats`, `doordash`, `deliveroo` provider는 레스토랑 검색과 메뉴 검색을 전제로 합니다.

```bash
lunch-order-agent --config config/hyehwa_poke_lunch.json --provider uber_eats --dry-run
```

## 새 provider 추가 방법

1. `src/lunch_order_agent/providers/global_delivery.py`의 `PROFILES`에 새 profile을 추가합니다.
2. `config/*.json`의 `providers`에 profile 이름을 추가합니다.
3. `python -m unittest discover -s tests`로 회귀 검증합니다.

