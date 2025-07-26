# settings.py

import pygame
import json
import os
import sys

# ======================================================================================
# ## 리소스 경로 함수 (가장 중요!) ##
# ======================================================================================
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller one-file/one-folder bundle
        base_path = sys._MEIPASS
    except Exception:
        # Running from source
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# ======================================================================================


# --- 기본 설정 ---
WIDTH, HEIGHT = 1280, 720
BASE_WIDTH, BASE_HEIGHT = 1280, 720
FPS = 60

# --- 타일 크기 관련 상수 ---
BASE_TILE_SIZE = 36  # 기본 해상도(1280x720)에서의 타일 크기

def get_current_tile_size():
    """현재 해상도에 맞는 타일 크기 계산"""
    scale_factor = WIDTH / BASE_WIDTH
    return int(BASE_TILE_SIZE * scale_factor)

# 초기 타일 크기 (나중에 update_tile_size()로 업데이트됨)
TILE_SIZE = BASE_TILE_SIZE

# --- 타일 크기에 맞춘 헬퍼 함수 ---
def align_to_tile_size(value, tile_size=None):
    """값을 타일 크기의 배수로 조정 (가장 가까운 배수로 반올림)"""
    if tile_size is None:
        tile_size = get_current_tile_size()
    return round(value / tile_size) * tile_size

def align_to_tile_size_down(value, tile_size=None):
    """값을 타일 크기의 배수로 조정 (내림)"""
    if tile_size is None:
        tile_size = get_current_tile_size()
    return (value // tile_size) * tile_size

def align_to_tile_size_up(value, tile_size=None):
    """값을 타일 크기의 배수로 조정 (올림)"""
    if tile_size is None:
        tile_size = get_current_tile_size()
    return ((value + tile_size - 1) // tile_size) * tile_size

def update_tile_size():
    """해상도 변경 시 타일 크기 업데이트"""
    global TILE_SIZE
    TILE_SIZE = get_current_tile_size()

# --- 크기 및 위치 조절을 위한 헬퍼 함수 ---
def scale_x(value):
    return int(value * (WIDTH / BASE_WIDTH))

def scale_y(value):
    return int(value * (HEIGHT / BASE_HEIGHT))

def scale_font(size):
    avg_scale = (WIDTH / BASE_WIDTH + HEIGHT / BASE_HEIGHT) / 2
    return int(size * avg_scale)

# --- 색상 정의 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
PLACEHOLDER_COLOR = (170, 170, 170)
ACTIVE_BORDER_COLOR = (70, 130, 180)
RED = (255, 0, 0, 255)
BLUE = (0, 0, 255)
BACKGROUND_COLOR = (50, 50, 60)
YELLOW = (255, 255, 0)

# --- 해상도 목록 ---
RESOLUTIONS = [(1280, 720), (1600, 900), (1920, 1080)]

# --- 충돌 필터링 카테고리 ---
PLAYER_CATEGORY = 0b1
ANIMAL_CATEGORY = 0b10
TERRAIN_CATEGORY = 0b100
CEILING_CATEGORY = 0b1000

# === 추가: 충돌 타입 정의 ===
PLAYER_COLLISION_TYPE = 1
CARNIVORE_HEAD_COLLISION_TYPE = 2
# ============================

# --- 육식동물 리스트 ---
CARNIVORES = ["tiger", "lion", "crocodile", "python", "bear"]

# --- JSON 파일에서 동물 블록 데이터 불러오기 ---
try:
    # resource_path를 사용하여 파일 경로를 지정합니다.
    with open(resource_path('final_animal_blocks.json'), 'r') as f:
        ANIMAL_DATA = json.load(f)
except FileNotFoundError:
    print("Error: 'final_animal_blocks.json' 파일을 찾을 수 없습니다.")
    ANIMAL_DATA = {}

# ======================================================================================
# === 스테이지별 설정 데이터 (5, 6, 9 스테이지 재설계) ===
# ======================================================================================
STAGE_DATA = {
    "1": {
        "name": "첫걸음: 설치와 포식",
        "available_animals": ["turtle", "tiger"],
        "terrain": [ (250, 600, 504, 108), (1030, 600, 504, 108) ],
        "goal_pos": (1180, 546)
    },
    "2": {
        "name": "포식자의 식사",
        "available_animals": ["turtle", "zebra", "lion"],
        "terrain": [ (150, 550, 288, 216), (640, 585, 108, 36), (1130, 550, 288, 216) ],
        "goal_pos": (1180, 442)
    },
    "3": {
        "name": "회전의 기술",
        "available_animals": ["sloth", "python", "turtle"],
        "terrain": [ (150, 550, 288, 216), (640, 650, 144, 36), (1130, 550, 288, 216) ],
        "goal_pos": (1180, 442)
    },
    "4": {
        "name": "공중 정원",
        "available_animals": ["hippo", "giraffe", "tiger"],
        "terrain": [ (150, 550, 288, 216), (WIDTH / 2, 400, 144, 36), (1130, 550, 288, 216) ],
        "goal_pos": (1180, 442)
    },
    "5": {
        "name": "코끼리 볼링",
        "available_animals": ["elephant", "turtle"],
        "terrain": [ (150, 600, 324, 72), (800, 600, 108, 72), (1150, 600, 216, 72) ],
        "goal_pos": (1200, 564)
    },
    "6": {
        "name": "위태로운 외줄타기",
        "available_animals": ["giraffe", "flamingo", "sloth"],
        "terrain": [ (250, 500, 504, 36), (1030, 350, 504, 36) ],
        "goal_pos": (1180, 332)
    },
    "7": {
        "name": "곰의 동굴",
        "available_animals": ["bear", "sloth", "python", "turtle"],
        "terrain": [ (150, 550, 288, 216), (WIDTH/2, 420, 108, 36), (1130, 550, 288, 216) ],
        "goal_pos": (1180, 442)
    },
    "8": {
        "name": "구름 징검다리",
        "available_animals": ["giraffe", "flamingo", "turtle", "sloth"],
        "terrain": [ (150, 600, 288, 108), (500, 525, 108, 36), (800, 450, 108, 36), (1150, 375, 216, 36) ],
        "goal_pos": (1200, 357)
    },
    "9": {
        "name": "탈출! 동물 감옥",
        "available_animals": ["hippo", "bear", "turtle", "lion"],
        "terrain": [ (150, 650, 288, 108), (900, 450, 36, 396), (1100, 580, 288, 108) ],
        "goal_pos": (1050, 524)
    },
    "10": {
        "name": "나락의 다리",
        "available_animals": ["giraffe", "python", "sloth", "hippo", "bear"],
        "terrain": [ (150, 300, 288, 36), (WIDTH/2, 680, 144, 36), (1130, 300, 288, 36) ],
        "goal_pos": (1180, 282)
    }
}