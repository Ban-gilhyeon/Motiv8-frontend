# 오류·로그·보안

## 로그

- 운영 환경에서는 오류와 성능 중심으로 기록한다.
- access token, refresh token, 비밀번호, 개인정보, 요청 전문을 기록하지 않는다.
- 사용자 식별자는 필요한 경우 익명화한다.

## 오류 모니터링

- API 오류 code와 HTTP status를 함께 수집한다.
- 서버 request ID가 내려오면 오류 보고에 연결한다.
- 401·403은 일반 서버 장애와 분리한다.
- 오류 화면에 stack trace와 파일 경로를 노출하지 않는다.

## 브라우저 보안

- 서버 message를 HTML로 삽입하지 않는다.
- 토큰을 URL query나 analytics event에 넣지 않는다.
- 외부 링크·리다이렉트 대상은 허용 목록을 검토한다.

## Open Questions

- 오류 모니터링 도구
- request ID 헤더 이름
- 개인정보 마스킹 목록
