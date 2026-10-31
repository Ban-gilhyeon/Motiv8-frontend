# API 오류 처리

## 상태 코드 매핑

- `400`: 입력 형식·필수값·범위 오류
- `401`: 인증 실패 또는 만료
- `403`: 권한 부족
- `404`: 리소스 없음
- `409`: 중복·상태 충돌
- `500`: 서버 내부 오류

## error code 처리

안정적인 분기 기준은 `error.code`다.

- `INVALID_CREDENTIALS`: 로그인 실패 안내
- `USER_ALREADY_EXISTS`: 중복 식별자 안내
- `EXERCISE_NOT_FOUND`: 운동 선택 상태 갱신
- `WORKOUT_NOT_FOUND`: 기록 없음 또는 목록 재조회
- `WORKOUT_ACCESS_DENIED`: 접근 불가 안내
- `INVALID_WORKOUT_MEASUREMENT`: 입력 필드 오류 표시

알 수 없는 코드는 공통 오류 화면 또는 재시도 안내로 처리한다. 서버 `message`를 HTML로 렌더링하지 않는다.

## 화면 상태

- 입력 오류: 필드별 `details` 매핑
- 인증 오류: 로그인 이동
- 권한 오류: 접근 불가 상태
- 없음: 빈 상태
- 서버 오류: 재시도 버튼

## Open Questions

- `details`의 필드별 실제 구조
- 422 사용 여부
