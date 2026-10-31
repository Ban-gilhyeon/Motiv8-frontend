# 프론트 구조

## 기본 경계

- `app`: 앱 진입, 라우팅, 전역 provider
- `pages` 또는 `screens`: 사용자 화면 조합
- `features`: 로그인, 운동 기록 등 사용자 행동 단위
- `entities`: User, Exercise, Workout 표시 모델
- `shared`: API client, UI, 유틸, 상수

## 의존 규칙

- 화면은 feature/entity/shared를 조합한다.
- API 호출은 API 모듈을 통해 실행한다.
- UI 컴포넌트가 직접 fetch하지 않는다.
- 도메인 규칙을 route 컴포넌트에 흩뿌리지 않는다.
- API 응답 타입을 모든 화면에서 직접 재사용하지 않는다.

## Open Questions

- React/Next/Vite 등 프레임워크
- 라우팅·상태 관리·서버 상태 라이브러리
- 스타일 시스템과 디자인 토큰
