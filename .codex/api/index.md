# API 문서 목록

프론트엔드가 백엔드와 통신할 때 지켜야 할 외부 계약을 관리한다.

- [공통 규칙](conventions.md): URL, 메서드, 응답 envelope
- [인증](authentication.md): 토큰 헤더, 갱신, 인증 상태
- [오류 처리](errors.md): 상태 코드, error code, 사용자 메시지
- [페이지네이션](pagination.md): 목록, 날짜 범위, 빈 결과

## 사용 순서

1. 기능의 도메인 문서를 읽는다.
2. 공통 규칙과 인증·오류 규칙을 확인한다.
3. 실제 Swagger/OpenAPI 계약으로 필드명을 확정한다.
4. API client와 화면 타입을 분리한다.

## Open Questions

- 실제 엔드포인트별 request/response 필드가 아직 확정되지 않았다.
- Swagger/OpenAPI 파일 제공 위치가 정해지지 않았다.
