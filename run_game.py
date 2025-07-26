#!/usr/bin/env python3
# run_game.py - 게임 실행 스크립트

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    import pygame
    print("✓ pygame이 설치되어 있습니다.")
except ImportError:
    print("✗ pygame이 설치되어 있지 않습니다.")
    print("다음 명령어로 설치하세요: pip install pygame")
    sys.exit(1)

try:
    import pymunk
    print("✓ pymunk이 설치되어 있습니다.")
except ImportError:
    print("✗ pymunk이 설치되어 있지 않습니다.")
    print("다음 명령어로 설치하세요: pip install pymunk")
    sys.exit(1)

# 필요한 파일들 확인
required_files = [
    "game_core.py",
    "settings.py", 
    "render_manager.py",
    "ui_manager.py",
    "audio_manager.py",
    "tilemap_renderer.py",
    "final_animal_blocks.json"
]

missing_files = []
for file in required_files:
    if not os.path.exists(file):
        missing_files.append(file)

if missing_files:
    print("✗ 다음 파일들이 없습니다:")
    for file in missing_files:
        print(f"  - {file}")
    sys.exit(1)

print("✓ 모든 필수 파일이 있습니다.")

# 게임 실행
try:
    from game_core import main
    print("게임을 시작합니다...")
    main()
except KeyboardInterrupt:
    print("\n게임이 사용자에 의해 종료되었습니다.")
except Exception as e:
    print(f"\n게임 실행 중 오류가 발생했습니다: {e}")
    import traceback
    traceback.print_exc()