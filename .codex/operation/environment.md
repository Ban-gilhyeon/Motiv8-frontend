# 환경변수와 실행 설정

## 필수 설정

- 개발·스테이징·운영별 API base URL
- 빌드 도구가 허용하는 public 환경변수 prefix
- API proxy 또는 CORS 설정
- 앱 환경 구분값

예시 이름은 빌드 도구 확정 후 적용한다.

```text
VITE_API_BASE_URL=https://api.example.com/api/v1
VITE_APP_ENV=development
```

## 규칙

- 비밀키·refresh token을 public 환경변수에 넣지 않는다.
- 로컬 비밀 파일은 Git에 커밋하지 않는다.
- 환경변수 누락은 앱 시작 시 명확히 실패시킨다.
- API base URL을 화면 코드에 하드코딩하지 않는다.

## Open Questions

- 빌드 도구와 실제 prefix
- 배포 플랫폼
- 개발 시 proxy 사용 여부
