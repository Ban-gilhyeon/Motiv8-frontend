# Motiv8 프론트엔드 개발 기준

백엔드 `.codex` 문서를 프론트엔드 구현에 맞게 변환한 기준이다.

## 분류 문서

- [API](api/index.md): HTTP 계약, 인증, 오류, 페이지네이션
- [도메인](domain/index.md): 인증, 운동, 기록, 진행, 알림·소셜
- [아키텍처](architecture/index.md): 구조, 상태, 테스트
- [디자인](design/index.md): 홈·운동 목업의 시각·레이아웃 기준
- [운영](operation/index.md): 환경변수, 보안, 배포 점검
- [포트폴리오](portfolio/index.md): 개요, 기능, 결정, 트러블슈팅

## 문서 성격 구분

- 백엔드 구현 지시: NestJS, Prisma, DB 트랜잭션, 서버 예외 필터, 서버 로그 규칙
- 프론트엔드에 적용: API URL 규칙, HTTP 메서드, 요청·응답 계약, 인증 실패 처리, 에러 코드, 도메인 enum과 입력 규칙
- 프론트엔드에서 추가 결정: API 주소와 환경변수, 토큰 저장·갱신, HTTP 클라이언트, 전역 인증 상태, 라우트 보호, 날짜·시간대 표시, 페이지네이션 UI, 알림 권한

## 바로 적용할 계약

### API

- Base path: `/api/v1`
- 현재 사용자 관련 API: `/me`
- 리소스는 복수형 명사 사용: `/exercises`, `/routines`, `/workouts`
- `GET` 조회, `POST` 생성 또는 command, `PATCH` 부분 수정, `DELETE` 삭제·비활성화
- 운동 유형 enum: `WEIGHT`, `BODYWEIGHT`, `CARDIO`

### 인증

- 보호 API 요청에 `Authorization: Bearer <accessToken>` 전송
- `401`은 토큰 누락·만료·위조로 처리하고 로그인 화면 또는 토큰 갱신 흐름으로 연결
- `403`은 인증됐지만 접근 권한이 없는 상태로 처리
- 사용자 ID를 요청 body/query에 넣어 소유권을 판단하지 않음
- Access Token, Refresh Token, 개인정보를 로그·에러 화면에 노출하지 않음

### 응답

성공 응답은 다음 형태를 전제로 한다.

```json
{
  "success": true,
  "data": {},
  "meta": null
}
```

실패 응답은 다음 형태를 전제로 한다.

```json
{
  "success": false,
  "error": {
    "code": "WORKOUT_NOT_FOUND",
    "message": "운동 기록을 찾을 수 없습니다.",
    "details": null
  }
}
```

프론트는 사용자 문구를 `message`만으로 분기하지 말고 `error.code`를 기준으로 분기한다. `details`는 입력 필드 오류 표시가 필요한 경우에만 사용한다.

### 입력·도메인

- 음수·범위·소수 허용 여부를 입력 컴포넌트에서 먼저 제한하되 서버 검증을 최종 기준으로 삼는다.
- `WEIGHT`: 무게 + 반복 횟수
- `BODYWEIGHT`: 반복 횟수 또는 세트
- `CARDIO`: 시간, 필요 시 거리·속도·칼로리
- 기록 없는 날짜·기간은 오류가 아니라 빈 상태로 표시
- 운동 기록 수정·삭제 후 통계·진행도는 서버 재계산 결과를 다시 조회

## 프론트엔드에서 추가 설정할 항목

### 필수

- `VITE_API_BASE_URL` 또는 프로젝트 빌드 도구에 맞는 API base URL 환경변수
- 개발·스테이징·운영별 API 주소
- HTTP 클라이언트와 공통 응답 unwrap 방식
- Access Token 메모리 상태와 Refresh Token 저장 위치
- `401` 동시 요청 처리, refresh 실패 시 로그아웃, 재시도 횟수
- 로그인·회원가입·로그아웃·토큰 갱신 API의 실제 path와 request/response 필드
- 백엔드 CORS 및 쿠키 사용 여부
- 로딩·빈 상태·401·403·404·409·422/400·500 화면 정책
- 날짜 표시 timezone, 월별 조회 시작·종료 포함 규칙
- 목록 기본 page size, 정렬 필드, `meta` 실제 필드명

### MVP 후 결정

- 웹 푸시 권한과 알림 설정 화면
- 캐릭터·배지·추천 화면의 실제 응답 모델
- 친구·공유 데이터 공개 범위와 차단 상태 UI
- 자동 저장 및 실패 복구
- 분석 도구와 프론트 오류 모니터링에서 개인정보 마스킹

## 백엔드에 확인할 질문

1. 실제 API 엔드포인트별 path, method, request/response 예시는 어디에 확정할 것인가?
2. Access Token과 Refresh Token은 JSON 응답인가, HttpOnly Secure Cookie인가?
3. Refresh Token 회전·로그아웃 폐기·탈퇴 시 데이터 삭제 정책은 무엇인가?
4. 성공 응답의 `data`가 항상 있는가? `204`를 사용하는 API는 무엇인가?
5. 목록 `meta`의 정확한 필드명은 `page`, `size`, `total`, `hasNext` 중 무엇인가?
6. 날짜/시간은 ISO 8601 UTC로 주고받는가? 사용자의 timezone은 어떻게 전달하는가?
7. 검증 상세 오류의 실제 구조는 무엇인가?
8. API 명세를 Swagger/OpenAPI 파일로 제공할 수 있는가?

## 백엔드 문서 중 프론트에 복사하지 않는 것

- Prisma/PostgreSQL/Repository/Transaction 규칙
- NestJS Controller, Service, Guard, ExceptionFilter 구현 규칙
- 서버 구조화 로그와 CloudWatch 수집 방식
- 서버 전용 테스트 경계와 모듈 의존 방향

위 항목은 참고만 하고 프론트에는 각각 HTTP 클라이언트, 상태 관리, 라우팅, UI 오류 처리, 브라우저 로그 정책으로 별도 설계한다.

## Open Questions

- 프론트 기술 스택과 빌드 도구가 아직 문서화되지 않았다.
- 실제 API 서버 주소와 인증 저장 방식이 확정되지 않았다.
- 백엔드 문서는 일부 정책을 `결정이 필요한 사항`으로 남겨 두고 있다.
- 따라서 API 연동 코드 작성 전 OpenAPI 또는 엔드포인트별 계약 확정이 필요하다.
