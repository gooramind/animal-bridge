# settings.py (전체 코드)

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
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# ======================================================================================

# --- 기본 설정 ---
WIDTH, HEIGHT = 1280, 720
BASE_WIDTH, BASE_HEIGHT = 1280, 720
FPS = 60

# --- 타일 크기 관련 상수 ---
BASE_TILE_SIZE = 36

def get_current_tile_size():
    scale_factor = WIDTH / BASE_WIDTH
    return int(BASE_TILE_SIZE * scale_factor)

TILE_SIZE = BASE_TILE_SIZE

# --- 타일 크기에 맞춘 헬퍼 함수 ---
def align_to_tile_size(value, tile_size=None):
    if tile_size is None:
        tile_size = get_current_tile_size()
    return round(value / tile_size) * tile_size

def align_to_tile_size_down(value, tile_size=None):
    if tile_size is None:
        tile_size = get_current_tile_size()
    return (value // tile_size) * tile_size

def align_to_tile_size_up(value, tile_size=None):
    if tile_size is None:
        tile_size = get_current_tile_size()
    return ((value + tile_size - 1) // tile_size) * tile_size

def update_tile_size():
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
    with open(resource_path('final_animal_blocks.json'), 'r') as f:
        ANIMAL_DATA = json.load(f)
except FileNotFoundError:
    print("Error: 'final_animal_blocks.json' 파일을 찾을 수 없습니다.")
    ANIMAL_DATA = {}

# ======================================================================================
# === 스테이지별 설정 데이터 ===
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
        "name": "마지막 시련: 가시밭길",
        "available_animals": ["giraffe", "python", "sloth", "hippo", "bear"],
        "terrain": [ (150, 400, 288, 36), (WIDTH/2, 350, 144, 36), (1130, 400, 288, 36) ],
        "goal_pos": (1180, 332),
        "has_hazard_floor": True # <-- [추가] 이 스테이지에 가시 바닥이 있음을 명시
    }
}



# ======================================================================================
# 폰트 중앙 관리
# ======================================================================================
FONT_PATH = "assets/Font/PF스타더스트 3.0 Bold.ttf"

def load_font(size, bold=False, italic=False):
    """게임용 폰트를 로드합니다. 실패 시 시스템 폰트로 대체합니다."""
    try:
        return pygame.font.Font(resource_path(FONT_PATH), scale_font(size))
    except (pygame.error, FileNotFoundError):
        print(f"⚠️ 커스텀 폰트 로드 실패, 시스템 폰트로 대체: {FONT_PATH}")
        return pygame.font.SysFont("malgungothic", scale_font(size), bold=bold, italic=italic)

class GameFonts:
    @staticmethod
    def get_fonts():
        return {
            'title_large': load_font(90, bold=True),
            'title_medium': load_font(70, bold=True),
            'title_small': load_font(60, bold=True),
            'button_large': load_font(60),
            'button_medium': load_font(50),
            'button_small': load_font(40),
            'body_large': load_font(50),
            'body_medium': load_font(35),
            'body_small': load_font(30),
            'input': load_font(50),
            'placeholder': load_font(30, italic=True),
            'timer': load_font(40),
            'count': load_font(25),
            'header': load_font(45, bold=True),
        }

def init_fonts():
    """pygame 초기화 후 호출해야 합니다."""
    pygame.font.init()
    return GameFonts.get_fonts()