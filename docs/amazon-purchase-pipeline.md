# Amazon Purchase Pipeline

## 역할 / 목적 / 맥락

역할: Amazon Fresh와 일반 Amazon 상품 구매 준비 흐름을 카테고리별 A/B 테스트로 정의한다.

목적: 식료품, 가구, 전자제품, 의류, 생활용품을 키워드/가격/배송 조건으로 비교하고 결제 직전까지 안전하게 준비한다.

맥락: 이 파이프라인은 Amazon 비공개 API, 세션 쿠키, 결제 자동 클릭을 사용하지 않는다. 최종 `Place your order`, `Buy Now`, `1-Click`, `Subscribe & Save` 확정은 사용자가 직접 처리한다.

## 아키텍처 플로우

통신 방식: 동기 CLI dry-run. 큐/이벤트는 사용하지 않는다.

요청 진입점: `lunch-order-agent --provider amazon_purchase --amazon-ab-config config/amazon_purchase_ab_tests.json`

처리 계층: `src/lunch_order_agent/cli.py`가 설정을 읽고 `src/lunch_order_agent/providers/amazon.py`의 `AmazonPurchaseProvider`로 전달한다.

외부 연동/저장소: 외부 API 호출과 DB 저장소를 사용하지 않는다. 검색 URL만 생성하고 사용자가 브라우저 또는 iPhone 앱에서 확인한다.

스키마 근거: `src/lunch_order_agent/models.py`의 `AmazonScenario`, `PaymentPolicy`가 source of truth다. 별도 DBML/ERD는 없다.

실패/보상 처리: 로그인, CAPTCHA, Face ID/Touch ID, 배송창 없음, 가격 초과, 주소/결제수단 불일치, 총액 초과가 발생하면 자동 진행을 중단하고 사용자가 직접 확인한다.

## 실행 명령

전체 A/B 시나리오:

```bash
lunch-order-agent --provider amazon_purchase --amazon-ab-config config/amazon_purchase_ab_tests.json --dry-run
```

특정 시나리오 JSON 출력:

```bash
lunch-order-agent --provider amazon_purchase --amazon-ab-config config/amazon_purchase_ab_tests.json --amazon-scenario electronics-usbc-charger-mac --format json
```

테스트:

```bash
python -m unittest discover -s tests
```

## A/B 테스트 케이스

| 시나리오 | 채널 | 플랫폼 | 카테고리 | 성공 기준 | 중단 조건 |
| --- | --- | --- | --- | --- | --- |
| `fresh-high-protein-salad-mac` | Fresh | Mac Web | 식료품 | `i=amazonfresh` 검색 URL 생성, 고단백/닭가슴살/샐러드 후보 필터, 결제 직전 중단 | Fresh 배송창 없음, 총액 상한 초과, 신한 결제수단 미확인 |
| `fresh-high-protein-salad-iphone` | Fresh | iPhone App | 식료품 | iPhone Mirroring/앱 실행 체크리스트 생성, 보안 확인 수동 처리 표시 | Face ID/Touch ID 미통과, Fresh 진입 실패, 배송창 없음 |
| `furniture-ergonomic-chair-mac` | Retail | Mac Web | 가구 | 의자 검색 URL 생성, 가격/배송/조립 옵션 수동 확인 단계 포함 | 대형 배송일 불명확, 설치 서비스 자동 선택, 반품 비용 미확인 |
| `electronics-usbc-charger-mac` | Retail | Mac Web | 전자제품 | 65W/GaN/USB C/PD 후보 필터와 Same-Day 확인 단계 포함 | 안전 인증/정격 미확인, checkout에서 Same-Day 해제 |
| `clothing-basic-shirt-iphone` | Retail | iPhone App | 의류 | 사이즈/색상/반품 가능 여부 수동 확인 단계 포함 | final sale, non-returnable, Buy Now 유도 |
| `household-paper-towels-mac` | Retail | Mac Web | 생활용품 | Subscribe & Save 회피와 one-time purchase 확인 단계 포함 | Subscribe-only, 대량 묶음 총액/보관 조건 미확인 |

## 플랫폼별 조건

Mac Web:

- 검색 URL 생성과 후보 비교는 dry-run으로 재현 가능하다.
- Amazon 로그인, CAPTCHA, 주소/결제 확인은 자동화하지 않는다.
- 일반 상품은 검색/장바구니 준비가 가능하지만 실제 배송 가능 시간은 checkout 직전 상태에 따른다.

iPhone App:

- iPhone Mirroring 또는 iPhone Amazon Shopping 앱을 전제로 한다.
- 앱 권한, Face ID/Touch ID, 보안 확인이 뜨면 사용자가 직접 처리한다.
- 앱 UI 변경으로 버튼 위치가 달라지면 자동 조작하지 않고 체크리스트 출력으로 fallback한다.

Fresh/Whole Foods:

- 지역, Prime 상태, 재고, 시간대에 따라 배송창이 달라질 수 있다.
- 배송창이 없거나 최소 주문/수수료 조건이 맞지 않으면 실패로 기록한다.

## 공식 참고

- Amazon grocery ordering guide: https://www.aboutamazon.com/news/retail/how-to-order-groceries-amazon
- Amazon Same-Day store: https://www.amazon.com/fmc/ssd-storefront
- Amazon Pay Buy Now overview: https://developer.amazon.com/docs/amazon-pay-buy-now-checkout/buy-now-overview.html
- Amazon Subscribe & Save overview: https://sell.amazon.com/programs/subscribe-and-save

## 테스트 보고 형식

작동 여부는 실제 구매가 아니라 아래 정적 기준으로 판정한다.

- 설정 JSON이 `AmazonScenario`로 파싱된다.
- Fresh 시나리오는 `amazonfresh` 검색 인덱스를 사용한다.
- 일반 상품 시나리오는 Fresh 인덱스를 사용하지 않는다.
- 후보 필터가 필수 키워드, 금지 키워드, 가격 상한을 적용한다.
- 모든 시나리오가 `stops_before_payment=true`로 종료된다.
- CLI가 전체 및 특정 시나리오 dry-run 결과를 출력한다.
