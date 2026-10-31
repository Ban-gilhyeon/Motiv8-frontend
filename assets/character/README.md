# 기본 캐릭터

2026-10-31 확정한 Motiv8 기본 캐릭터. 이후 커스터마이징과 체형 변화는 이 모델을 기준으로 한다.

- `basicMale.blend`, `basicFemale.blend`: 확정한 남녀 편집 원본. 몸체 이름도 파일명과 동일.
- `basicMale.glb`, `basicFemale.glb`: 서비스 표시용 모델. 뼈대·애니메이션 포함.
- `design-reference.png`: 공통 디자인 기준 시안.
- `../../tools/create_basic.py`: 모델 재생성 스크립트. 실행하면 원본과 GLB, 렌더를 덮어쓰므로 Blender에서 직접 편집한 내용을 먼저 반영해야 한다.

흰색 사람형, A자 자세, 벌린 다리, 둥근 얼굴, 깊이를 보강한 머리, 낮고 매끈한 어깨가 기준이다.
남녀 모두 팔꿈치 부피를 보강한 둥근 팔과 손목으로 완만하게 줄어드는 단면을 사용한다.

## 재생성

- 최종 모델 재생성: Blender의 `--python tools/rig_basic.py` 옵션 사용. 남녀 기본형 생성 후 리깅·동작까지 적용한다.
- `create_basic.py` 단독 실행은 리깅 없는 기본형으로 덮어쓰므로 최종 재생성에는 `rig_basic.py`를 사용한다.
- 두 캐릭터 모두 2026-10-31 확정. 여자형은 작은 머리, 높은 허리·골반, 완만한 가슴·하체 곡선을 사용한다.
- 리깅 스크립트는 임시 렌더 PNG를 정리한다.

## 리깅 테스트

2026-11-01 기본 호흡·운동 후 호흡·땀 닦기·달리기를 프로토타입용으로 확정했다. 힘주기는 추가 조정 가능한 초안이다.

- `basicMale.blend`, `basicFemale.blend`: 기본 뼈대 20개와 관절 보조 뼈대 4개를 적용한 최신 통합 원본.
- 같은 이름의 `.glb`: 스킨과 `BasicMovementTest` 애니메이션 포함.
- `tools/rig_basic.py`: 기본형 생성과 리깅을 수행해 통합 원본을 갱신한다.
- 30fps, 1~120프레임의 4초 테스트. 흉곽 움직임·고개 기울이기·팔 움직임 포함.
- Blender에서 Space로 재생. 자동 가중치는 초안이며 큰 관절 움직임에 대한 보정은 추가 검증 필요.
- `BreathingIdle`: 2초 주기 기본 호흡. Blender 기본 미리보기.
- `BreathingRecovery`: 동일한 호흡을 1초 주기로 재생하는 운동 후 호흡.
- `Flex`: 양팔을 굽혀 올리는 힘주기. 3초.
- `WipeSweat`: 손이 얼굴 안으로 들어가지 않도록 앞쪽 경로로 움직이는 땀 닦기. 3초.
- `Run`: 팔·다리를 교차하는 제자리 달리기. 1초 반복.
- `ShoulderRangeTest`: 쇄골 움직임을 포함한 어깨 다축 회전 테스트. 6초.
- `ElbowVolumeTest`: 0~145도 팔꿈치 굽힘 테스트. 6초.
- `tools/arm_deformation.py`: 각도에 따라 보조 뼈대 단면을 보강한다. 보정 스케일은 GLB 애니메이션에 베이크된다. 정확한 부피 보존이나 극단적인 자세의 충돌 방지를 보장하지 않는다.
- 달리기는 한 주기당 두 번의 상하 반동을 포함한다. 전체 높이 대비 약 2.2% 상승하며 시작·끝 높이는 동일하다.
- 추가 동작은 프로토타입이며 큰 관절 변형과 손의 접촉 위치는 후속 보정 대상이다.
- 호흡 클립은 팔·고개 테스트 동작과 분리되어 있다. NLA Editor에서 해당 트랙의 음소거를 전환해 확인한다.

## 보관 파일

2026-11-01 힘주기 자세 확정:

- `basicMale-FrontDoubleBiceps.blend`, `basicFemale-FrontDoubleBiceps.blend`: 대체 팔꿈치 축과 위팔 비틀림, 표면 스무딩을 적용한 확정 힘주기 원본. 현재 액션은 `FrontDoubleBiceps`.
- `output/character-previews/basicMale-FrontDoubleBiceps.mp4`, `basicFemale-FrontDoubleBiceps.mp4`: 확정 힘주기 영상.
- 기본 `basicMale`·`basicFemale` 모델과 GLB의 `Flex`는 이전 동작이다. 확정 힘주기의 변형 후 스무딩은 GLB 통합 전이며, 현재 GLB를 최종 힘주기와 동일한 결과로 간주하면 안 된다.
- 생성 스크립트는 기본 모델 재생성용이다. 별도 확정 힘주기 파일은 덮어쓰지 않는다.

- 이전 팔 축 비교·원통형 실험·백업 폴더와 중간 관절 테스트 영상은 삭제했다.
- 현재 생성 스크립트는 팔 구조 실험 변경을 포함한다. 기본 모델을 재생성하기 전에 확정 원본과의 차이를 확인해야 한다.

- `output/character-previews/`: 남녀 동작별 최신 영상. 초기 `BasicMovementTest` 영상은 삭제했다.
- `tools/run_motion.py`: 달리기 반동 생성 로직. `rig_basic.py`에서 사용하므로 유지한다.
- `tools/joint_support.py`: 어깨·팔꿈치의 반각 보조 뼈대와 가중치 보정. GLB에도 보조 뼈대 움직임을 베이크한다.
- `tools/record_basic_animations.py`: 검토용 영상 생성. `--run-only` 옵션으로 달리기만 재촬영할 수 있다.
- 일회성 반동 갱신 도구와 Python 캐시는 삭제했다.
