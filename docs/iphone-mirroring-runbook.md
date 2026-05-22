# iPhone Mirroring Runbook

## 사전 준비

1. Mac과 iPhone이 같은 Apple Account로 로그인되어 있어야 합니다.
2. iPhone Mirroring 앱을 Mac에서 실행할 수 있어야 합니다.
3. iPhone에 배달의민족 앱이 설치되어 있고 로그인되어 있어야 합니다.
4. 최근 배달지에 `회사` 라벨 주소가 있어야 합니다.
5. 결제수단에 신한 카드가 있어야 합니다.

## 기본 실행

```bash
lunch-order-agent --config config/hyehwa_poke_lunch.json --provider baemin_iphone_mirroring --dry-run
```

## 실제 운영 절차

1. 평일 11:00에 LaunchAgent 또는 사용자가 CLI를 실행합니다.
2. 출력된 플랜에 따라 iPhone Mirroring을 엽니다.
3. 배달의민족에서 혜화 근처 포케/샐러드 가게를 검색합니다.
4. 고단백, 닭가슴살, 오리훈제, 샐러드, 포케 키워드 후보 중 14,000원 이하 메뉴만 고릅니다.
5. 최근 배달지에서 `회사` 라벨을 선택합니다.
6. 결제수단이 `신한`인지 확인합니다.
7. `KB` 또는 `국민`이 보이면 중단하고 사용자가 직접 신한 카드로 바꿉니다.
8. 결제 직전 화면에서 멈추고 사용자가 결제합니다.

## 금지

- 결제 버튼 자동 클릭
- 카드번호/비밀번호/주소 원문 저장
- 배민 비공개 API 호출
- 앱 화면을 확실히 읽지 못했는데 계속 진행

