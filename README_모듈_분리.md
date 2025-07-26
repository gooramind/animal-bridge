# README_모듈_분리.md

# Animal Bridge - 모듈 분리 구조

이 프로젝트는 게임 로직과 렌더링/UI/오디오를 분리하여 모듈화된 구조로 개발되었습니다.

## 파일 구조

### 🎮 게임 핵심 로직
- **`game_core.py`** - 메인 게임 로직, 물리 시스템, 게임 상태 관리
- **`settings.py`** - 게임 설정, 상수, 스테이지 데이터

### 🎨 렌더링 및 UI 시스템
- **`tilemap_renderer.py`** - 타일맵 렌더링 시스템
- **`ui_manager.py`** - UI 컴포넌트 렌더링
- **`render_manager.py`** - 통합 렌더링 관리자

### 🔊 오디오 시스템
- **`audio_manager.py`** - 사운드 및 음악 관리

### 📁 에셋 파일들
- **`assets/`** - 타일맵, 사운드, 폰트, 아이콘 등

## 역할 분담

### 게임 로직 담당자
**수정할 파일:**
- `game_core.py` - 게임 플레이 로직, 물리 시스템
- `settings.py` - 게임 밸런스, 스테이지 설정

**담당 업무:**
- 게임 규칙 및 메커니즘
- 물리 시뮬레이션 (pymunk)
- 동물 블록 행동 로직
- 스테이지 설계
- 게임 밸런스 조정

### UI/타일맵/사운드 담당자
**수정할 파일:**
- `tilemap_renderer.py` - 타일맵 시스템
- `ui_manager.py` - UI 컴포넌트
- `render_manager.py` - 렌더링 통합
- `audio_manager.py` - 사운드 시스템

**담당 업무:**
- 타일맵 구현 및 최적화
- UI 디자인 및 사용성
- 비주얼 이펙트
- 사운드 및 음악 관리
- 화면 해상도 대응

## 인터페이스 규약

### 1. 렌더링 인터페이스
```python
# render_manager.py에서 제공하는 메서드들
render_manager.render_background(background_type)
render_manager.render_terrain(terrain_rects)
render_manager.render_game_ui(ui_animals, dragging_animal, stats, fonts)
render_manager.render_start_menu(player_name, input_active, input_box, next_button_rect, fonts)
# ... 기타 화면별 렌더링 메서드들
```

### 2. 오디오 인터페이스
```python
# audio_manager.py에서 제공하는 메서드들
audio_manager.play_sound('click')  # 사운드 재생
audio_manager.set_sound_volume(volume)  # 볼륨 조절
audio_manager.play_music(loops=-1)  # 배경음악 재생
```

### 3. 게임 상태 인터페이스
```python
# game_core.py에서 관리하는 게임 상태
class GameState:
    current_state: str  # "start_menu", "main_menu", "game_play" 등
    player_name: str
    selected_stage: int
    sound_volume: float
```

## 데이터 흐름

```
게임 로직 (game_core.py)
    ↓ 렌더링 요청
렌더링 관리자 (render_manager.py)
    ↓ 세부 렌더링
UI 관리자 (ui_manager.py) + 타일맵 렌더러 (tilemap_renderer.py)
    ↓ 화면 출력
pygame 화면
```

```
사용자 입력
    ↓ 이벤트 처리
게임 로직 (game_core.py)
    ↓ 사운드 요청
오디오 관리자 (audio_manager.py)
    ↓ 사운드 재생
pygame 오디오
```

## 개발 가이드라인

### 게임 로직 수정 시
1. `game_core.py`의 게임 플레이 로직만 수정
2. 렌더링 관련 코드는 `render_manager` 호출로 대체
3. 사운드는 `audio_manager.play_sound()` 사용
4. 새로운 게임 기능 추가 시 렌더링 인터페이스 협의 필요

### UI/렌더링 수정 시
1. `render_manager.py`에서 화면별 렌더링 메서드 수정
2. `ui_manager.py`에서 UI 컴포넌트 개선
3. `tilemap_renderer.py`에서 타일맵 시스템 최적화
4. 새로운 UI 요소 추가 시 게임 로직과 인터페이스 협의 필요

### 오디오 수정 시
1. `audio_manager.py`에서 사운드 로딩 및 재생 로직 수정
2. 새로운 사운드 파일은 `assets/Sound/` 에 추가
3. 사운드 이름은 `audio_manager.sound_paths`에 등록

## 실행 방법

```bash
# 메인 게임 실행
python game_core.py

# 또는 기존 방식
python main.py
```

## 주요 개선 사항

1. **모듈 독립성**: 각 시스템이 독립적으로 개발 가능
2. **코드 재사용성**: UI 컴포넌트와 렌더링 시스템 재사용 가능
3. **유지보수성**: 각 담당자가 자신의 영역에만 집중 가능
4. **확장성**: 새로운 기능 추가 시 인터페이스를 통해 쉽게 통합 가능
5. **성능 최적화**: 렌더링과 로직이 분리되어 각각 최적화 가능

이 구조를 통해 게임 로직 담당자와 UI/그래픽 담당자가 효율적으로 협업할 수 있습니다.
