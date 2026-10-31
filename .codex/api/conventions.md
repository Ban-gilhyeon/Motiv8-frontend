# API 공통 규칙

## URL과 메서드

- Base path: `/api/v1`
- 리소스는 복수형 명사 사용: `/exercises`, `/routines`, `/workouts`
- 현재 사용자: `/me`
- 식별자: path parameter
- `GET`: 조회, `POST`: 생성 또는 command
- `PATCH`: 일부 수정, `DELETE`: 삭제 또는 비활성화

## 응답 envelope

성공:

```json
{ "success": true, "data": {}, "meta": null }
```

실패:

```json
{
  "success": false,
  "error": { "code": "WORKOUT_NOT_FOUND", "message": "운동 기록을 찾을 수 없습니다.", "details": null }
}
```

프론트는 `message` 문구가 아니라 `error.code`로 분기한다. API client에서 envelope를 일관되게 unwrap한다.

## 타입 규칙

- 서버 enum 문자열을 그대로 사용한다.
- Domain/API 타입과 화면 전용 ViewModel을 분리한다.
- 날짜는 서버 형식을 확인한 뒤 파싱한다.
- 서버 응답을 그대로 UI 상태로 공유하지 않는다.

## Open Questions

- 성공 응답에 `data`가 없는 API와 `204` 사용 범위
- 날짜·시간 직렬화가 ISO 8601 UTC인지 여부
