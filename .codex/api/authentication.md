# 인증 API와 클라이언트 정책

## 서버 계약

- 보호 API에 `Authorization: Bearer <accessToken>` 전송
- 토큰 누락·만료·위조: `401 Unauthorized`
- 인증됐으나 권한 부족: `403 Forbidden`
- 인증 주체는 요청 body/query의 userId가 아니라 서버 컨텍스트로 결정

## 프론트 책임

- API client가 보호 요청에 access token을 자동 부착한다.
- 앱 시작 시 인증 상태를 복원한다.
- `401` 발생 시 refresh를 한 번 시도하고 원 요청을 재시도한다.
- 동시 `401`이면 refresh 요청 하나만 실행한다.
- refresh 실패 시 인증 상태를 제거하고 로그인 화면으로 보낸다.
- 토큰·비밀번호·개인정보를 콘솔·분석 이벤트·에러 화면에 기록하지 않는다.

## 저장 정책 결정 필요

- Access Token: 메모리 저장 우선 검토
- Refresh Token: HttpOnly Secure Cookie 사용 여부 먼저 확인
- localStorage 저장 시 XSS 위험과 만료·폐기 정책 검토

## Open Questions

- 로그인·회원가입·refresh·logout 실제 path와 필드
- JSON token 응답인지 HttpOnly Cookie인지
- refresh token 회전과 로그아웃 폐기 정책
